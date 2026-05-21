from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml

UNCLEAR = "unclear"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PDFS = PROJECT_ROOT / "data" / "pdfs"
REPORTS = PROJECT_ROOT / "reports"
FIGURES = PROJECT_ROOT / "figures"
QUERIES_PATH = PROJECT_ROOT / "queries.yaml"
RESULT_COLUMNS = [
    "direction",
    "direction_zh",
    "query",
    "title",
    "year",
    "authors",
    "venue",
    "doi",
    "url",
    "abstract",
    "citation_count",
    "source_database",
    "open_access_pdf",
    "raw_id",
]


def ensure_dirs() -> None:
    for path in [DATA_RAW, DATA_PROCESSED, DATA_PDFS, REPORTS, FIGURES]:
        path.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def load_queries(path: Path = QUERIES_PATH) -> dict[str, Any]:
    data = load_yaml(path)
    directions = data.get("directions")
    if not isinstance(directions, list) or len(directions) != 6:
        raise ValueError("queries.yaml must define exactly six directions.")
    ids = [str(direction.get("id")) for direction in directions]
    if ids != ["A", "B", "C", "D", "E", "F"]:
        raise ValueError(f"Direction ids must be A-F, got {ids}")
    for direction in directions:
        if not direction.get("queries"):
            raise ValueError(f"Direction {direction.get('id')} has no queries.")
    return data


def is_unclear(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == "" or value.strip().lower() == UNCLEAR
    return False


def clean_text(value: Any) -> str:
    if is_unclear(value):
        return UNCLEAR
    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text or UNCLEAR


def strip_html(value: Any) -> str:
    text = clean_text(value)
    if text == UNCLEAR:
        return UNCLEAR
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or UNCLEAR


def normalize_doi(value: Any) -> str:
    if is_unclear(value):
        return UNCLEAR
    doi = str(value).strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.strip().lower()
    return doi or UNCLEAR


def title_key(value: Any) -> str:
    text = clean_text(value)
    if text == UNCLEAR:
        return UNCLEAR
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or UNCLEAR


def safe_int(value: Any) -> int | None:
    if is_unclear(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def direction_labels(value: Any) -> list[str]:
    if is_unclear(value):
        return []
    if isinstance(value, list):
        raw = value
    else:
        raw = re.split(r"[|,;]", str(value))
    return sorted({str(item).strip() for item in raw if str(item).strip()})


def json_dumps(value: Any) -> str:
    if value == UNCLEAR:
        return UNCLEAR
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_loads(value: Any, fallback: Any) -> Any:
    if is_unclear(value):
        return fallback
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError):
        return fallback


def abstract_from_inverted_index(index: Any) -> str:
    if not isinstance(index, dict) or not index:
        return UNCLEAR
    positioned: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            try:
                positioned.append((int(position), str(word)))
            except (TypeError, ValueError):
                continue
    if not positioned:
        return UNCLEAR
    return " ".join(word for _, word in sorted(positioned))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
            except json.JSONDecodeError:
                rows.append({"source": "jsonl_parse_error", "error": "invalid json line", "raw": line.strip()})
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]] | pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    frame.to_csv(path, index=False)
    return path


def result_row(**kwargs: Any) -> dict[str, Any]:
    row = {column: UNCLEAR for column in RESULT_COLUMNS}
    for column in RESULT_COLUMNS:
        if column in kwargs and not is_unclear(kwargs[column]):
            row[column] = kwargs[column]
    for column in ["direction", "direction_zh", "query", "title", "year", "authors", "venue", "doi", "url", "abstract", "citation_count", "source_database", "open_access_pdf", "raw_id"]:
        row[column] = clean_text(row[column])
    row["doi"] = normalize_doi(row["doi"])
    return row


def write_results_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    frame.to_csv(path, index=False)
    return path


def author_names(items: Any, name_getter: str = "name") -> str:
    if not isinstance(items, list):
        return UNCLEAR
    names = []
    for item in items:
        if isinstance(item, dict):
            name = clean_text(item.get(name_getter))
            if name != UNCLEAR:
                names.append(name)
    return "; ".join(names) if names else UNCLEAR


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna(UNCLEAR)


def request_json(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    pause_seconds: float = 0.8,
    max_retries: int = 2,
    session: requests.Session | None = None,
) -> tuple[Any | None, dict[str, Any]]:
    client = session or requests.Session()
    last_error = UNCLEAR
    status_code: int | str = UNCLEAR
    for attempt in range(1, max_retries + 2):
        try:
            response = client.get(url, params=params, headers=headers, timeout=timeout)
            status_code = response.status_code
            response.raise_for_status()
            payload = response.json()
            time.sleep(pause_seconds)
            return payload, {
                "ok": True,
                "status_code": status_code,
                "attempts": attempt,
                "error": UNCLEAR,
                "retrieved_at": now_iso(),
            }
        except Exception as exc:  # noqa: BLE001 - keep pipeline alive and audit the failure
            last_error = str(exc)
            time.sleep(pause_seconds * attempt)
    return None, {
        "ok": False,
        "status_code": status_code,
        "attempts": max_retries + 1,
        "error": last_error,
        "retrieved_at": now_iso(),
    }


def env(name: str) -> str:
    return os.getenv(name, "").strip()


def markdown_table(frame: pd.DataFrame, max_rows: int = 20) -> str:
    if frame.empty:
        return "unclear\n"
    subset = frame.head(max_rows).fillna(UNCLEAR).astype(str)
    columns = list(subset.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in subset.iterrows():
        lines.append("| " + " | ".join(row[column].replace("|", "/") for column in columns) + " |")
    return "\n".join(lines) + "\n"
