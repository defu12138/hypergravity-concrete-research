from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "four_directions.yml"
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "sciencedirect_four_directions"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS = PROJECT_ROOT / "reports"
LOGS = PROJECT_ROOT / "logs"
SCIENCEDIRECT_SEARCH_URL = "https://api.elsevier.com/content/search/sciencedirect"
ABSTRACT_DOI_URL = "https://api.elsevier.com/content/abstract/doi"
UNCLEAR = "unclear"

OUTPUT_COLUMNS = [
    "direction",
    "title",
    "authors",
    "year",
    "journal",
    "DOI",
    "ScienceDirect URL or Elsevier URL",
    "source",
    "abstract",
    "keywords",
    "material/object",
    "method",
    "gravity/centrifugal/carbonation condition",
    "main findings",
    "relevance_to_hypergravity_concrete",
    "engineering_usefulness",
    "limitations",
    "score_relevance_0_5",
    "score_practicality_0_5",
    "score_novelty_0_5",
    "score_data_quality_0_5",
    "final_priority_score",
]


@dataclass(frozen=True)
class Direction:
    id: str
    slug: str
    name_zh: str
    name_en: str
    common_names: list[str]
    queries: list[str]
    inclusion: list[str]
    exclusion: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any) -> str:
    if value is None:
        return UNCLEAR
    if isinstance(value, list):
        value = "; ".join(clean_text(item) for item in value if clean_text(item) != UNCLEAR)
    if isinstance(value, dict):
        value = value.get("$") or value.get("_") or value.get("text") or json.dumps(value, ensure_ascii=False)
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text or UNCLEAR


def normalize_doi(value: Any) -> str:
    text = clean_text(value)
    if text == UNCLEAR:
        return UNCLEAR
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    return text.lower().strip() or UNCLEAR


def normalize_title(value: Any) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip() or UNCLEAR


def load_config(path: Path = CONFIG_PATH) -> tuple[dict[str, Any], list[Direction]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    directions = []
    for raw in data.get("directions", []):
        directions.append(
            Direction(
                id=str(raw["id"]),
                slug=str(raw["slug"]),
                name_zh=str(raw["name_zh"]),
                name_en=str(raw["name_en"]),
                common_names=[str(item) for item in raw.get("common_names", [])],
                queries=[str(item) for item in raw.get("queries", [])],
                inclusion=[str(item) for item in raw.get("inclusion", [])],
                exclusion=[str(item) for item in raw.get("exclusion", [])],
            )
        )
    if [direction.id for direction in directions] != ["D1", "D2", "D3", "D4"]:
        raise ValueError("four_directions.yml must define D1-D4 in order.")
    return data, directions


def api_key() -> str:
    return os.environ.get("ELSEVIER_API_KEY", "").strip()


def headers() -> dict[str, str]:
    key = api_key()
    if not key:
        raise RuntimeError("ELSEVIER_API_KEY is not set")
    return {"X-ELS-APIKey": key, "Accept": "application/json"}


def request_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None,
    log_base: dict[str, Any],
    max_retries: int = 2,
    pause_seconds: float = 0.7,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    audit = dict(log_base)
    audit.update({"retrieved_at": now_iso(), "status": "failed", "status_code": UNCLEAR, "x_els_status": UNCLEAR, "error": UNCLEAR, "api_url": url})
    for attempt in range(1, max_retries + 2):
        try:
            response = session.get(url, params=params or {}, headers=headers(), timeout=40)
            audit["status_code"] = response.status_code
            audit["x_els_status"] = response.headers.get("X-ELS-Status", UNCLEAR)
            audit["api_url"] = response.url
            audit["quota_limit"] = response.headers.get("X-RateLimit-Limit", UNCLEAR)
            audit["quota_remaining"] = response.headers.get("X-RateLimit-Remaining", UNCLEAR)
            audit["attempts"] = attempt
            if response.status_code in {429, 500, 502, 503, 504} and attempt <= max_retries + 1:
                audit["error"] = f"retryable HTTP {response.status_code}"
                time.sleep(pause_seconds * attempt)
                continue
            response.raise_for_status()
            audit["status"] = "ok"
            audit["error"] = UNCLEAR
            time.sleep(pause_seconds)
            return response.json(), audit
        except Exception as exc:  # noqa: BLE001 - batch search should continue and log failures
            audit["attempts"] = attempt
            audit["error"] = str(exc)[:500]
            if attempt <= max_retries:
                time.sleep(pause_seconds * attempt)
                continue
            return None, audit
    return None, audit


def entry_list(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    entries = payload.get("search-results", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    return [entry for entry in entries if isinstance(entry, dict)]


def list_text(value: Any) -> str:
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(clean_text(item.get("$") or item.get("name") or item.get("surname")))
            else:
                parts.append(clean_text(item))
        return "; ".join(part for part in parts if part != UNCLEAR) or UNCLEAR
    return clean_text(value)


def sd_url(entry: dict[str, Any]) -> str:
    if clean_text(entry.get("prism:url")) != UNCLEAR:
        return clean_text(entry.get("prism:url"))
    links = entry.get("link", [])
    if isinstance(links, dict):
        links = [links]
    for link in links:
        if isinstance(link, dict) and link.get("@href"):
            return clean_text(link.get("@href"))
    doi = normalize_doi(entry.get("prism:doi"))
    if doi != UNCLEAR:
        return f"https://doi.org/{doi}"
    return UNCLEAR


def parse_year(*values: Any) -> str:
    for value in values:
        match = re.search(r"\b(19|20)\d{2}\b", clean_text(value))
        if match:
            return match.group(0)
    return UNCLEAR


def search_query(session: requests.Session, direction: Direction, query: str, count: int, from_year: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload, audit = request_json(
        session,
        SCIENCEDIRECT_SEARCH_URL,
        params={"query": query, "count": count, "start": 0},
        log_base={"direction": direction.slug, "direction_id": direction.id, "query": query, "request_type": "search", "from_year_note": from_year},
    )
    entries = entry_list(payload)
    total = clean_text((payload or {}).get("search-results", {}).get("opensearch:totalResults") if isinstance(payload, dict) else None)
    audit["returned_records"] = len(entries)
    audit["total_results"] = total
    return entries, [audit]


def article_abstract(payload: dict[str, Any] | None) -> tuple[str, str]:
    if not isinstance(payload, dict):
        return UNCLEAR, UNCLEAR
    abstract_response = payload.get("abstracts-retrieval-response", {})
    if isinstance(abstract_response, dict):
        core = abstract_response.get("coredata", {})
        abstract = clean_text(core.get("dc:description"))
        keywords = keyword_text(abstract_response.get("authkeywords"))
        if keywords == UNCLEAR:
            keywords = keyword_text(abstract_response.get("idxterms"))
        if abstract != UNCLEAR:
            return abstract, keywords
    core = payload.get("full-text-retrieval-response", {}).get("coredata", {})
    abstract = clean_text(core.get("dc:description"))
    keywords = clean_text(core.get("dcterms:subject") or core.get("prism:keyword"))
    if abstract != UNCLEAR:
        return abstract, keywords
    head = payload.get("full-text-retrieval-response", {}).get("originalText", "")
    return clean_text(head), keywords


def keyword_text(value: Any) -> str:
    if not isinstance(value, dict):
        return UNCLEAR
    raw = value.get("author-keyword") or value.get("mainterm") or value.get("idxterm")
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return UNCLEAR
    keywords = []
    for item in raw:
        if isinstance(item, dict):
            keyword = clean_text(item.get("$") or item.get("mainterm") or item.get("idxterm"))
        else:
            keyword = clean_text(item)
        if keyword != UNCLEAR:
            keywords.append(keyword)
    return "; ".join(keywords) if keywords else UNCLEAR


def fetch_article_metadata(session: requests.Session, doi: str, direction: Direction, query: str) -> tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]:
    if doi == UNCLEAR:
        return UNCLEAR, UNCLEAR, None, None
    url = f"{ABSTRACT_DOI_URL}/{quote(doi, safe='')}"
    payload, audit = request_json(
        session,
        url,
        params={},
        log_base={"direction": direction.slug, "direction_id": direction.id, "query": query, "request_type": "abstract_metadata", "doi": doi},
        max_retries=1,
        pause_seconds=0.4,
    )
    abstract, keywords = article_abstract(payload)
    return abstract, keywords, payload, audit


def row_from_entry(entry: dict[str, Any], direction: Direction, query: str) -> dict[str, Any]:
    doi = normalize_doi(entry.get("prism:doi") or entry.get("doi"))
    return {
        "direction": direction.slug,
        "direction_id": direction.id,
        "direction_zh": direction.name_zh,
        "direction_en": direction.name_en,
        "query": query,
        "title": clean_text(entry.get("dc:title") or entry.get("title")),
        "authors": list_text(entry.get("dc:creator") or entry.get("authors")),
        "year": parse_year(entry.get("prism:coverDate"), entry.get("coverDate"), entry.get("prism:coverDisplayDate")),
        "journal": clean_text(entry.get("prism:publicationName") or entry.get("publicationName")),
        "DOI": doi,
        "ScienceDirect URL or Elsevier URL": sd_url(entry),
        "source": "ScienceDirect",
        "abstract": clean_text(entry.get("dc:description") or entry.get("prism:teaser") or entry.get("description")),
        "keywords": UNCLEAR,
        "raw_id": clean_text(entry.get("eid") or entry.get("pii") or entry.get("dc:identifier")),
    }


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


DIRECT_TERMS = {
    "centrifuged_concrete": ["concrete", "cement", "mortar", "phc", "pile", "uhpc", "sfrc", "cementitious"],
    "geotechnical_centrifuge_modeling": ["concrete", "lining", "segment", "pile", "tunnel", "shield", "cross passage", "structure"],
    "gravity_cement_hydration": ["cement", "hydration", "paste", "c-s-h", "calcium silicate hydrate", "solidification"],
    "high_gravity_carbonation_mineralization": ["cement", "concrete", "calcium", "cao", "ca(oh)2", "slag", "recycled concrete", "cementitious", "paste"],
}

METHOD_TERMS = {
    "centrifuged_concrete": ["centrifuged concrete", "centrifugally", "centrifugal forming", "centrifugal casting", "centrifugal rotation", "spun", "spun cast", "spc pile", "pipe pile", "phc"],
    "geotechnical_centrifuge_modeling": ["centrifuge model", "geotechnical centrifuge", "model test", "soil-structure"],
    "gravity_cement_hydration": ["microgravity", "hypergravity", "gravity", "centrifugation", "sedimentation"],
    "high_gravity_carbonation_mineralization": ["carbonation", "mineralization", "mineralisation", "rotating packed bed", "co2", "carbonation curing"],
}


def include_record(row: dict[str, Any], direction: Direction) -> bool:
    text = " ".join(clean_text(row.get(field)) for field in ["title", "abstract", "journal", "keywords"])
    lower = text.lower()
    exclusion_hit = contains_any(lower, direction.exclusion)
    method_hit = contains_any(lower, METHOD_TERMS[direction.slug])
    object_hit = contains_any(lower, DIRECT_TERMS[direction.slug])
    if direction.slug == "centrifuged_concrete":
        geotech_noise = contains_any(lower, ["centrifuge model", "dynamic centrifuge", "concrete-faced", "concrete faced", "rock-fill dam", "rockfill dam"])
        return method_hit and object_hit and not exclusion_hit and not geotech_noise
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "centrifuge" in lower and object_hit and not exclusion_hit
    if direction.slug == "gravity_cement_hydration":
        return method_hit and object_hit and not exclusion_hit
    if direction.slug == "high_gravity_carbonation_mineralization":
        process_hit = contains_any(lower, ["carbonation", "mineralization", "mineralisation", "co2", "carbon dioxide", "calcium carbonate", "co 2"])
        material_hit = contains_any(lower, ["cement", "concrete", "calcium", "cao", "ca(oh)2", "slag", "recycled concrete", "cementitious", "paste", "steelmaking"])
        noise_hit = contains_any(lower, ["amine", "solvent", "pet particles", "enzymatic degradation", "so 2", "sulfur dioxide"])
        return method_hit and process_hit and material_hit and not exclusion_hit and not noise_hit
    return method_hit and object_hit and not exclusion_hit


def material_object(row: dict[str, Any]) -> str:
    text = " ".join(clean_text(row.get(field)).lower() for field in ["title", "abstract", "keywords"])
    for label, terms in [
        ("PHC/concrete pipe pile or spun concrete member", ["phc", "pipe pile", "spun concrete", "hollow concrete"]),
        ("cement paste / cement hydration products", ["cement paste", "cement hydration", "c-s-h", "calcium silicate hydrate"]),
        ("tunnel lining / pile foundation concrete structure", ["lining", "segment", "pile foundation", "shield tunnel", "cross passage"]),
        ("cementitious or calcium-rich carbonation material", ["cementitious", "cement", "concrete fines", "calcium hydroxide", "cao", "slag"]),
    ]:
        if any(term in text for term in terms):
            return label
    return "Concrete/cementitious material or calcium-rich object inferred from title/abstract"


def method(row: dict[str, Any]) -> str:
    text = " ".join(clean_text(row.get(field)).lower() for field in ["title", "abstract", "keywords"])
    if "rotating packed bed" in text:
        return "Rotating packed bed / high-gravity process"
    if "carbonation curing" in text or "accelerated carbonation" in text or "co2" in text:
        return "CO2 carbonation, mineralization, or carbonation curing"
    if "microgravity" in text or "hypergravity" in text or "centrifugation" in text:
        return "Gravity-field or centrifugation-controlled cement hydration experiment"
    if "centrifuge model" in text or "geotechnical centrifuge" in text:
        return "Geotechnical centrifuge model test"
    if "centrifug" in text or "spun" in text:
        return "Centrifugal forming / spinning / casting"
    return "Method inferred from ScienceDirect title/abstract"


def condition(row: dict[str, Any]) -> str:
    text = " ".join(clean_text(row.get(field)).lower() for field in ["title", "abstract", "keywords"])
    phrases = []
    for term in ["centrifugal", "centrifuged", "spun", "microgravity", "hypergravity", "rotating packed bed", "accelerated carbonation", "carbonation curing", "co2 mineralization", "co2 mineralisation"]:
        if term in text:
            phrases.append(term)
    return "; ".join(phrases) if phrases else "Condition present in query/title but not quantitatively stated in available metadata"


def relevance_sentence(row: dict[str, Any], direction: Direction) -> str:
    if direction.slug == "centrifuged_concrete":
        return "It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming."
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research."
    if direction.slug == "gravity_cement_hydration":
        return "It links gravity level or centrifugation to cement hydration, C-S-H, settling, or microstructure, matching the mechanism side of hypergravity concrete."
    return "It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts."


def score_record(row: dict[str, Any], direction: Direction) -> dict[str, Any]:
    text = " ".join(clean_text(row.get(field)).lower() for field in ["title", "abstract", "keywords"])
    abstract_ok = clean_text(row.get("abstract")) != UNCLEAR and len(clean_text(row.get("abstract"))) > 80
    doi_ok = clean_text(row.get("DOI")) != UNCLEAR
    direct = 5 if include_record(row, direction) else 2
    if direction.slug == "geotechnical_centrifuge_modeling":
        practicality = 3
    elif direction.slug == "gravity_cement_hydration":
        practicality = 2 if ("microgravity" in text or "hypergravity" in text) else 3
    else:
        practicality = 4
    novelty = 4 if any(term in text for term in ["hypergravity", "microgravity", "rotating packed bed", "high gravity"]) else 3
    data_quality = (2 if doi_ok else 1) + (2 if abstract_ok else 0) + (1 if clean_text(row.get("journal")) != UNCLEAR else 0)
    final = round(0.40 * direct + 0.25 * practicality + 0.20 * novelty + 0.15 * data_quality, 2)
    row.update(
        {
            "material/object": material_object(row),
            "method": method(row),
            "gravity/centrifugal/carbonation condition": condition(row),
            "main findings": "See abstract metadata; detailed findings require full-text reading where access is lawful." if abstract_ok else "ScienceDirect direct metadata did not provide enough abstract detail.",
            "relevance_to_hypergravity_concrete": relevance_sentence(row, direction),
            "engineering_usefulness": engineering_usefulness(direction),
            "limitations": limitations(row, direction),
            "score_relevance_0_5": direct,
            "score_practicality_0_5": practicality,
            "score_novelty_0_5": novelty,
            "score_data_quality_0_5": data_quality,
            "final_priority_score": final,
            "screening_status": "included" if include_record(row, direction) else "excluded_or_low_relevance",
            "off_track_judgement": off_track_judgement(direction),
        }
    )
    return row


def engineering_usefulness(direction: Direction) -> str:
    if direction.slug == "centrifuged_concrete":
        return "High: directly informs pipe piles, hollow members, mix stability, density gradient, durability, and centrifugal production."
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "Medium: useful for structural-geotechnical similitude and loading references, but less useful for concrete material design."
    if direction.slug == "gravity_cement_hydration":
        return "Medium-low: mechanistic value is high, but experiments are harder to reproduce without gravity-field equipment."
    return "High: CO2 mineralization/carbonation can connect to strength, carbon storage, curing, and recycled cementitious resources."


def limitations(row: dict[str, Any], direction: Direction) -> str:
    missing = []
    if clean_text(row.get("DOI")) == UNCLEAR:
        missing.append("missing DOI")
    if clean_text(row.get("abstract")) == UNCLEAR or len(clean_text(row.get("abstract"))) <= 80:
        missing.append("abstract unavailable or too short in API metadata")
    base = "; ".join(missing) if missing else "metadata is usable for initial screening"
    if direction.slug == "geotechnical_centrifuge_modeling":
        return f"{base}; this is a parallel geotechnical modeling field, not direct hypergravity concrete material research."
    return base


def off_track_judgement(direction: Direction) -> str:
    if direction.slug == "centrifuged_concrete":
        return "Directly studies concrete materials or concrete members under centrifugal forming."
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "Studies geotechnical models involving concrete structures; use as parallel field reference, not as hypergravity concrete material evidence."
    if direction.slug == "gravity_cement_hydration":
        return "Directly studies cementitious hydration/microstructure only when gravity, microgravity, hypergravity, or centrifugation is an experimental variable."
    return "Often chemical-engineering carbonation; only keep records transferable to cementitious/calcium-rich materials."


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    output = []
    rows = sorted(rows, key=lambda row: (row["direction"], -float(row.get("final_priority_score", 0)), row.get("title", "")))
    for row in rows:
        doi = normalize_doi(row.get("DOI"))
        title = normalize_title(row.get("title"))
        key = ("doi", doi) if doi != UNCLEAR else ("title", title)
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_search(count: int, from_year: int, fetch_abstracts: bool = True) -> dict[str, Any]:
    _meta, directions = load_config()
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.trust_env = False
    rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    raw_files: list[str] = []
    try:
        for direction in directions:
            for query in direction.queries:
                entries, audits = search_query(session, direction, query, count=count, from_year=from_year)
                audit_rows.extend(audits)
                raw_path = DATA_RAW / f"{direction.slug}__{safe_name(query)}.json"
                write_json(raw_path, {"direction": direction.slug, "query": query, "entries": entries})
                raw_files.append(str(raw_path))
                for entry in entries:
                    row = row_from_entry(entry, direction, query)
                    rows.append(score_record(row, direction))
    finally:
        session.close()

    deduped = dedupe(rows)
    included = [row for row in deduped if row.get("screening_status") == "included"]
    if fetch_abstracts:
        session = requests.Session()
        session.trust_env = False
        try:
            direction_map = {direction.slug: direction for direction in directions}
            for row in included:
                if clean_text(row["abstract"]) != UNCLEAR and len(clean_text(row["abstract"])) > 80:
                    continue
                direction = direction_map[row["direction"]]
                abstract, keywords, payload, audit = fetch_article_metadata(session, row["DOI"], direction, row.get("query", UNCLEAR))
                if audit:
                    audit_rows.append(audit)
                if payload:
                    write_json(DATA_RAW / "article_metadata" / f"{safe_name(row['DOI'])}.json", payload)
                if abstract != UNCLEAR:
                    row["abstract"] = abstract
                if keywords != UNCLEAR:
                    row["keywords"] = keywords
                score_record(row, direction)
        finally:
            session.close()
    final_included = [
        row
        for row in included
        if clean_text(row.get("abstract")) != UNCLEAR and len(clean_text(row.get("abstract"))) > 80
    ]
    for row in included:
        if row not in final_included:
            row["screening_status"] = "excluded_missing_abstract"
            row["limitations"] = f"{row.get('limitations', '')}; excluded from final Excel because no usable abstract was available from Elsevier metadata."
    output_rows = [{column: row.get(column, UNCLEAR) for column in OUTPUT_COLUMNS} for row in final_included]
    xlsx_path = DATA_PROCESSED / "four_directions_literature.xlsx"
    pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS).to_excel(xlsx_path, index=False)
    pd.DataFrame(deduped).to_csv(DATA_PROCESSED / "four_directions_literature_all_screened.csv", index=False)
    pd.DataFrame(audit_rows).to_csv(LOGS / "four_directions_sciencedirect_search_log.csv", index=False)
    write_json(LOGS / "four_directions_sciencedirect_search_log.json", audit_rows)
    stats = write_reports(directions, rows, deduped, final_included, audit_rows)
    return {"xlsx": xlsx_path, "audit": LOGS / "four_directions_sciencedirect_search_log.csv", "stats": stats, "raw_files": raw_files}


def safe_name(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip().lower())
    return text[:120].strip("_") or "query"


def direction_stats(directions: list[Direction], rows: list[dict[str, Any]], deduped: list[dict[str, Any]], included: list[dict[str, Any]], audit_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats = {}
    for direction in directions:
        query_audits = [row for row in audit_rows if row.get("direction") == direction.slug and row.get("request_type") == "search"]
        total_results = 0
        for audit in query_audits:
            try:
                total_results += int(audit.get("total_results") or 0)
            except (TypeError, ValueError):
                pass
        stats[direction.slug] = {
            "name_zh": direction.name_zh,
            "name_en": direction.name_en,
            "common_names": direction.common_names,
            "raw_returned": sum(1 for row in rows if row["direction"] == direction.slug),
            "sd_total_results_sum_by_query": total_results,
            "deduped": sum(1 for row in deduped if row["direction"] == direction.slug),
            "included": sum(1 for row in included if row["direction"] == direction.slug),
            "api_ok_queries": sum(1 for row in query_audits if row.get("status") == "ok"),
            "api_failed_queries": sum(1 for row in query_audits if row.get("status") != "ok"),
        }
    return stats


def representative(rows: list[dict[str, Any]], direction: Direction, limit: int = 10) -> list[dict[str, Any]]:
    subset = [row for row in rows if row["direction"] == direction.slug and row.get("screening_status") == "included"]
    subset = sorted(subset, key=lambda row: (float(row.get("final_priority_score", 0)), int(row.get("year") if str(row.get("year", "")).isdigit() else 0)), reverse=True)
    return subset[:limit]


def write_reports(directions: list[Direction], rows: list[dict[str, Any]], deduped: list[dict[str, Any]], included: list[dict[str, Any]], audit_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats = direction_stats(directions, rows, deduped, included, audit_rows)
    write_landscape(directions, stats, included)
    write_comparison(directions, stats)
    write_teacher_outline(directions, stats, included)
    write_legacy_archive()
    return stats


def write_landscape(directions: list[Direction], stats: dict[str, dict[str, Any]], included: list[dict[str, Any]]) -> None:
    lines = [
        "# 四方向 ScienceDirect 文献格局报告",
        "",
        f"- 检索时间：{now_iso()}",
        "- 数据源：ScienceDirect / Elsevier API。未混入 Crossref、Semantic Scholar 或 Google Scholar 记录。",
        "- 合规边界：仅保存 API 返回的 metadata、摘要/teaser、DOI、ScienceDirect/Elsevier 稳定链接；未抓取付费全文，未绕过访问权限。",
        "",
        "## 为什么从六方向收敛到四方向",
        "",
        "原六方向把高重力碳化、CO2 养护、碳化 SCM、旋转填充床等拆得较细，适合发散，但国际文献实际检索时容易把同一批 carbonation/mineralization 文献重复切分；同时“hypergravity concrete”本身不是常用题名词。四方向改按国际常用命名收敛：离心成型混凝土、土工离心模型、水泥水化重力效应、高重力碳化/矿化。这样既保留超重力主题，又能减少化工、土工、普通碳化文献之间的混淆。",
        "",
        "## 检索数量概览",
        "",
        "| 方向 | ScienceDirect query total 合计 | API返回记录 | 去重后数量 | 初筛相关数量 | 判断 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for direction in directions:
        item = stats[direction.slug]
        shortage = "该方向 ScienceDirect 直接文献不足" if item["included"] < 5 else "可形成初步阅读池"
        lines.append(f"| {direction.name_zh} | {item['sd_total_results_sum_by_query']} | {item['raw_returned']} | {item['deduped']} | {item['included']} | {shortage} |")
    lines.extend(["", "## 分方向分析", ""])
    for direction in directions:
        item = stats[direction.slug]
        lines.extend(
            [
                f"### {direction.name_zh}",
                "",
                f"- 国际常用叫法：{'; '.join(direction.common_names)}",
                f"- ScienceDirect 检索结果数量：query total 合计 {item['sd_total_results_sum_by_query']}；API 实际返回 {item['raw_returned']}。",
                f"- 去重后数量：{item['deduped']}；初筛后相关文献数量：{item['included']}。",
                f"- 不跑偏判断：{off_track_judgement(direction)}",
                f"- 研究热点：{hotspots(direction)}",
                f"- 近年趋势：{trend_note(direction, item)}",
                f"- 与“超重力混凝土”的关系：{relation_note(direction)}",
                f"- 是否适合作为硕士论文方向：{master_degree_note(direction, item)}",
                f"- 风险与不足：{risk_note(direction, item)}",
                "",
                "代表性文献（10篇以内）：",
                "",
            ]
        )
        reps = representative(included, direction)
        if not reps:
            lines.append("- 该方向 ScienceDirect 直接文献不足，未筛出足够代表性文献。")
        for index, row in enumerate(reps, start=1):
            lines.append(f"{index}. {row['title']} ({row['year']}). {row['journal']}. DOI/URL: {row['DOI']} / {row['ScienceDirect URL or Elsevier URL']}")
            lines.append(f"   - 相关性：{row['relevance_to_hypergravity_concrete']}")
        lines.append("")
    lines.extend(
        [
            "## 候选主线",
            "",
            "- 候选主线 A：离心成型混凝土 / PHC 管桩 / 离心浇筑材料性能。",
            "- 候选主线 B：高重力 CO2 矿化 / 水泥基材料碳化强化。",
            "- 候选主线 C：重力场影响水泥水化与微结构演化。",
            "",
            "土工离心模型更适合作为“平行领域参考”，不应直接等同于超重力混凝土材料研究。",
        ]
    )
    (REPORTS / "four_directions_landscape.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def hotspots(direction: Direction) -> str:
    return {
        "centrifuged_concrete": "spun/centrifuged pipe piles, hollow members, fiber reinforcement, durability gradients, centrifugal forming process.",
        "geotechnical_centrifuge_modeling": "shield tunnels, cross passages, concrete linings, pile-soil-structure interaction under scaled gravity fields.",
        "gravity_cement_hydration": "microgravity cement paste, hydration kinetics, bleeding/sedimentation, pore and C-S-H microstructure.",
        "high_gravity_carbonation_mineralization": "rotating packed bed carbonation, CO2 mineralization, carbonation curing, recycled concrete fines, calcium-rich wastes.",
    }[direction.slug]


def trend_note(direction: Direction, item: dict[str, Any]) -> str:
    if item["included"] < 5:
        return "ScienceDirect 直接命中文献偏少，趋势判断需谨慎。"
    if direction.slug == "high_gravity_carbonation_mineralization":
        return "碳化养护、CO2 矿化和再生粉体方向近年更活跃，高重力/旋转填充床是可迁移的过程强化支线。"
    if direction.slug == "centrifuged_concrete":
        return "离心管桩和离心成型构件持续有工程论文，但材料微结构与低碳胶凝体系耦合仍可深化。"
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "土工离心模型文献量较大，但混凝土材料本体不是核心变量。"
    return "水泥水化重力效应很专门，直接文献少，机制新颖但实验门槛较高。"


def relation_note(direction: Direction) -> str:
    return {
        "centrifuged_concrete": "直接对应超重力/离心加速度下混凝土成型、密实、分层和构件性能。",
        "geotechnical_centrifuge_modeling": "对应重力相似和离心试验方法，可参考加载与相似理论，但不是材料制备路线。",
        "gravity_cement_hydration": "对应重力场对水泥浆体水化、沉降、泌水和孔结构的机制影响。",
        "high_gravity_carbonation_mineralization": "对应高重力传质强化下的 CO2 碳化/矿化，可迁移到水泥基材料固碳与强化。",
    }[direction.slug]


def master_degree_note(direction: Direction, item: dict[str, Any]) -> str:
    if direction.slug == "geotechnical_centrifuge_modeling":
        return "不建议作为超重力混凝土材料主线，可作为方法参考或背景对照。"
    if direction.slug == "gravity_cement_hydration":
        return "创新性高，但若没有可控重力/离心实验条件，硕士阶段风险较高。"
    if item["included"] < 5:
        return "可作为小众切入点，但需要补充非 ScienceDirect 或全文阅读验证。"
    return "适合作为候选主线，由导师结合设备、材料来源和论文目标决定。"


def risk_note(direction: Direction, item: dict[str, Any]) -> str:
    base = "该方向 ScienceDirect 直接文献不足；" if item["included"] < 5 else ""
    return base + {
        "centrifuged_concrete": "容易停留在构件工程性能，需把离心制度、浆体迁移、分层和材料参数拉回材料问题。",
        "geotechnical_centrifuge_modeling": "文献多但容易跑偏到土体、边坡、液化和海床；需坚持只作平行领域参考。",
        "gravity_cement_hydration": "检索词敏感且样本少，普通水化文献不能强行归类。",
        "high_gravity_carbonation_mineralization": "化工 CO2 吸收文献很多，必须排除纯胺吸收和普通气液传质。",
    }[direction.slug]


def write_comparison(directions: list[Direction], stats: dict[str, dict[str, Any]]) -> None:
    rows = [
        "| 方向 | 文献数量 | 与混凝土材料的直接相关性 | 工程落地性 | 实验可操作性 | 创新性 | 导师汇报价值 | 继续深入难度 | 推荐优先级 |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for direction in directions:
        item = stats[direction.slug]
        ratings = comparison_ratings(direction, item)
        rows.append(f"| {direction.name_zh} | {item['included']} | {ratings[0]} | {ratings[1]} | {ratings[2]} | {ratings[3]} | {ratings[4]} | {ratings[5]} | {ratings[6]} |")
    rows.extend(
        [
            "",
            "候选主线不直接定题：A 离心成型混凝土/PHC 管桩；B 高重力 CO2 矿化/水泥基材料碳化强化；C 重力场影响水泥水化与微结构演化。",
            "",
            "土工离心模型建议定位为平行领域参考，不直接作为超重力混凝土材料研究主线。",
        ]
    )
    (REPORTS / "four_directions_comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def comparison_ratings(direction: Direction, item: dict[str, Any]) -> tuple[str, str, str, str, str, str, str]:
    if direction.slug == "centrifuged_concrete":
        return ("高", "高", "中", "中高", "高", "中", "优先候选")
    if direction.slug == "high_gravity_carbonation_mineralization":
        return ("高", "高", "中高", "高", "高", "中", "优先候选")
    if direction.slug == "gravity_cement_hydration":
        return ("高", "中低", "低", "高", "中高", "高", "风险候选")
    return ("中低", "中", "低", "中", "中", "中", "参考方向")


def write_teacher_outline(directions: list[Direction], stats: dict[str, dict[str, Any]], included: list[dict[str, Any]]) -> None:
    lines = [
        "# 导师汇报提纲：四方向 ScienceDirect 调研结果",
        "",
        "## 1. 为什么重新调整检索方向",
        "",
        "- 国际文献很少直接使用 “hypergravity concrete”。",
        "- 旧六方向适合发散，但碳化、矿化、旋转填充床和 CO2 养护之间有较多重复。",
        "- 本轮按国际常用叫法收敛为四类，优先使用 ScienceDirect / Elsevier API 重新检索。",
        "",
        "## 2. 国际上相关研究的四种叫法",
        "",
    ]
    for direction in directions:
        lines.append(f"- {direction.name_zh}：{'; '.join(direction.common_names)}")
    lines.extend(["", "## 3. 四个方向分别查到了什么", ""])
    for direction in directions:
        item = stats[direction.slug]
        lines.append(f"- {direction.name_zh}：ScienceDirect query total 合计 {item['sd_total_results_sum_by_query']}，去重后 {item['deduped']}，初筛相关 {item['included']}。{risk_note(direction, item)}")
    lines.extend(
        [
            "",
            "## 4. 哪些方向文献多但容易跑偏",
            "",
            "- 土工离心模型：容易跑到土体、边坡、液化、海床；本轮只保留涉及混凝土结构、隧道衬砌、管片、桩基础的记录。",
            "- 高重力碳化/矿化：容易跑到纯胺吸收或普通气液传质；本轮只保留可迁移到水泥基或钙基材料的记录。",
            "",
            "## 5. 哪些方向更贴近混凝土材料",
            "",
            "- 离心成型混凝土最贴近混凝土构件制备和材料分层。",
            "- 高重力碳化/矿化最贴近低碳胶凝材料、固碳、碳化强化。",
            "- 水泥水化重力效应最贴近材料机制，但直接文献和实验条件是主要风险。",
            "- 土工离心模型更适合作为平行领域参考，不应直接等同于超重力混凝土材料研究。",
            "",
            "## 6. 下一步建议老师重点讨论的问题",
            "",
            "- 是否把离心成型混凝土/PHC 管桩作为工程主线，还是只借用其离心成型机制？",
            "- 是否把高重力 CO2 矿化与水泥基材料碳化强化作为更容易落地的主线？",
            "- 是否具备做重力场影响水泥水化与微结构演化的设备条件？",
            "- 是否需要补充非 ScienceDirect 数据源；若补充，应单独标记 Crossref、Semantic Scholar 或 Google Scholar source。",
            "",
            "本提纲只呈现调查结果，不直接确定最终研究方向。",
        ]
    )
    (REPORTS / "teacher_meeting_outline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_legacy_archive() -> None:
    path = REPORTS / "legacy_six_direction_archive.md"
    lines = [
        "# Legacy six-direction archive note",
        "",
        "The earlier six-direction outputs are kept as legacy/archive material and are not deleted.",
        "",
        "Legacy files include `queries.yaml`, `data/processed/papers_master.csv`, `data/processed/works_master.csv`, `reports/final_research_map.md`, and related A-F landscape/score/reading-list reports.",
        "",
        "The current refocused review uses `config/four_directions.yml` and the generated `data/processed/four_directions_literature.xlsx` / `reports/four_directions_*.md` files.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ScienceDirect-first four-direction literature search for hypergravity concrete.")
    parser.add_argument("--count", type=int, default=20, help="Records per query returned by ScienceDirect Search API.")
    parser.add_argument("--from-year", type=int, default=1990)
    parser.add_argument("--skip-article-abstracts", action="store_true", help="Do not call Elsevier article metadata endpoint to fill missing abstracts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outputs = run_search(count=args.count, from_year=args.from_year, fetch_abstracts=not args.skip_article_abstracts)
    print(f"wrote {outputs['xlsx']}")
    print(f"wrote {outputs['audit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
