from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "data" / "local_literature" / "local_literature_index.csv"
UNCLEAR = "unclear"

DOI_RE = re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+\-]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

DIRECTION_RULES = [
    (
        "A",
        [
            "high gravity",
            "hypergravity",
            "超重力",
            "co2",
            "carbonation",
            "cao",
            "dry grinding",
        ],
    ),
    (
        "B",
        [
            "centrifugal",
            "centrifugally",
            "centrifuged",
            "spun",
            "phc",
            "pipe pile",
            "pile",
            "离心",
            "管桩",
            "钢管混凝土",
        ],
    ),
    (
        "C",
        [
            "centrifugal model",
            "model test",
            "重力场",
            "离心模型",
            "离心模拟",
        ],
    ),
    (
        "D",
        [
            "co2 curing",
            "carbon dioxide curing",
            "carbonated concrete",
            "co2养护",
            "碳化混凝土",
        ],
    ),
    (
        "E",
        [
            "concrete sludge",
            "solid waste",
            "waste concrete",
            "sludge",
            "scm",
            "固废",
            "废弃物",
            "污泥",
        ],
    ),
    (
        "F",
        [
            "rotating packed bed",
            "mass transfer",
            "process intensification",
            "旋转填充床",
            "传质",
        ],
    ),
]


KEYWORD_RULES = [
    "high gravity",
    "hypergravity",
    "超重力",
    "centrifugal",
    "centrifugally",
    "centrifuged",
    "离心",
    "管桩",
    "PHC",
    "concrete",
    "混凝土",
    "cement",
    "cementitious",
    "胶凝",
    "CO2",
    "carbonation",
    "碳化",
    "CaO",
    "dry grinding",
    "solid waste",
    "waste",
    "sludge",
    "固废",
    "废弃物",
    "钢管混凝土",
    "ECC",
    "model test",
    "离心模型",
    "rotating packed bed",
    "mass transfer",
]


CSV_FIELDS = [
    "file_name",
    "file_path",
    "file_extension",
    "file_size_bytes",
    "modified_time",
    "title",
    "authors",
    "year",
    "journal_or_source",
    "doi",
    "document_type",
    "detected_keywords",
    "matched_direction",
    "relevance_to_project",
    "sci_mainstream_status",
    "use_recommendation",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Index local literature files into data/local_literature/local_literature_index.csv. "
            "The script records metadata only and never copies or moves source files."
        )
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        help="Local literature folder to scan.",
    )
    return parser.parse_args()


def normalize_unclear(value: Any) -> str:
    if value is None:
        return UNCLEAR
    text = str(value).strip()
    return text if text else UNCLEAR


def clean_title_from_stem(stem: str) -> str:
    if "_" in stem and not re.search(r"[A-Za-z]{3,}", stem):
        return stem.split("_", 1)[0].strip() or UNCLEAR
    text = re.sub(r"\s+", " ", stem).strip()
    return text or UNCLEAR


def author_from_stem(stem: str) -> str:
    if "_" not in stem:
        return UNCLEAR
    author = stem.rsplit("_", 1)[-1].strip()
    if 1 <= len(author) <= 20 and not re.search(r"[A-Za-z]{3,}", author):
        return author
    return UNCLEAR


def detect_year(text: str) -> str:
    years = YEAR_RE.findall(text)
    # findall with a capturing group returns only the group; use finditer for full year.
    full_years = [match.group(0) for match in YEAR_RE.finditer(text)]
    for year in full_years:
        if 1900 <= int(year) <= datetime.now().year + 1:
            return year
    return UNCLEAR


def detect_doi(text: str) -> str:
    match = DOI_RE.search(text)
    if not match:
        return UNCLEAR
    return match.group(0).rstrip(").,;]> ")


def detect_keywords(text: str) -> str:
    lower = text.lower()
    found: list[str] = []
    for keyword in KEYWORD_RULES:
        if keyword.lower() in lower and keyword not in found:
            found.append(keyword)
    return ";".join(found) if found else UNCLEAR


def match_direction(text: str) -> str:
    lower = text.lower()
    # Prefer more specific non-B signals before broad centrifugal matches when present.
    scores: dict[str, int] = {}
    for direction, keywords in DIRECTION_RULES:
        scores[direction] = sum(1 for keyword in keywords if keyword.lower() in lower)
    if scores.get("E", 0) > 0 and scores.get("D", 0) == 0:
        return "E"
    if scores.get("D", 0) > 0:
        return "D"
    if scores.get("A", 0) > 0 and scores.get("B", 0) == 0:
        return "A"
    if scores.get("F", 0) > 0:
        return "F"
    if scores.get("C", 0) > 0:
        return "C"
    if scores.get("B", 0) > 0:
        return "B"
    return "Other"


def document_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "pdf":
        return "PDF"
    return suffix.upper() if suffix else UNCLEAR


def try_read_pdf_metadata(path: Path) -> dict[str, str]:
    if path.suffix.lower() != ".pdf":
        return {}

    for module_name, reader_name in (("pypdf", "PdfReader"), ("PyPDF2", "PdfReader")):
        try:
            module = __import__(module_name, fromlist=[reader_name])
            reader_cls = getattr(module, reader_name)
            reader = reader_cls(str(path))
            metadata = getattr(reader, "metadata", None) or {}
            return {
                "title": normalize_unclear(metadata.get("/Title") or metadata.get("title")),
                "authors": normalize_unclear(metadata.get("/Author") or metadata.get("author")),
            }
        except Exception:
            continue
    return {}


def relevance(direction: str) -> str:
    return {
        "A": "Medium; supports hypergravity or equivalent carbonation process background",
        "B": "Medium for centrifugal concrete background; low-to-medium for current E+D+A mainline",
        "C": "Low-to-medium; gravity or centrifuge model background, not direct cementitious carbonation evidence",
        "D": "Medium-to-high if CO2 curing/carbonated concrete is confirmed",
        "E": "Medium-to-high; supports solid-waste or SCM background",
        "F": "Low-to-medium; process intensification background needs concrete coupling",
        "Other": "Low; outside current mainline unless manually reclassified",
    }.get(direction, "Low; outside current mainline unless manually reclassified")


def recommendation(direction: str) -> str:
    return {
        "A": "背景支撑",
        "B": "背景支撑",
        "C": "慎用或剔除",
        "D": "核心必读",
        "E": "核心必读",
        "F": "背景支撑",
        "Other": "慎用或剔除",
    }.get(direction, "慎用或剔除")


def build_record(path: Path) -> dict[str, str]:
    stat = path.stat()
    stem = path.stem
    file_text = f"{path.name} {stem}"
    metadata = try_read_pdf_metadata(path)

    title = metadata.get("title", UNCLEAR)
    if title == UNCLEAR or len(title) < 5:
        title = clean_title_from_stem(stem)

    authors = metadata.get("authors", UNCLEAR)
    if authors == UNCLEAR:
        authors = author_from_stem(stem)

    direction = match_direction(file_text)
    doi = detect_doi(file_text)
    year = detect_year(file_text)
    keywords = detect_keywords(file_text)

    return {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_extension": path.suffix.lower() or UNCLEAR,
        "file_size_bytes": str(stat.st_size),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "title": title,
        "authors": authors,
        "year": year,
        "journal_or_source": UNCLEAR,
        "doi": doi,
        "document_type": document_type(path),
        "detected_keywords": keywords,
        "matched_direction": direction,
        "relevance_to_project": relevance(direction),
        "sci_mainstream_status": "需人工通过 Web of Science / JCR / 中科院分区核验",
        "use_recommendation": recommendation(direction),
        "notes": "Generated from file attributes, filename, and optional PDF metadata only; no OCR or full-text copy.",
    }


def iter_literature_files(source_dir: Path) -> list[Path]:
    allowed_suffixes = {".pdf", ".caj", ".nh", ".doc", ".docx"}
    return sorted(
        (p for p in source_dir.rglob("*") if p.is_file() and p.suffix.lower() in allowed_suffixes),
        key=lambda item: str(item).lower(),
    )


def write_csv(records: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        raise SystemExit(f"source directory not found: {source_dir}")

    records = [build_record(path) for path in iter_literature_files(source_dir)]
    write_csv(records, DEFAULT_OUTPUT)
    print(f"Indexed {len(records)} local literature files.")
    print(f"Wrote {DEFAULT_OUTPUT}")
    print("Source files were not copied, moved, or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
