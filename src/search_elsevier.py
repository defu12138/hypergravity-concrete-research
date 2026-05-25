from __future__ import annotations

import argparse
import os
from typing import Any
from urllib.parse import urlparse

import requests


SCIENCEDIRECT_SEARCH_URL = "https://api.elsevier.com/content/search/sciencedirect"
DIAGNOSIS_QUERY = "carbonation concrete"


def elsevier_api_key() -> str:
    return os.environ.get("ELSEVIER_API_KEY", "").strip()


def science_direct_headers(api_key: str) -> dict[str, str]:
    return {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json",
    }


def diagnose_elsevier(timeout: int = 30) -> dict[str, Any]:
    api_key = elsevier_api_key()
    parsed = urlparse(SCIENCEDIRECT_SEARCH_URL)
    result: dict[str, Any] = {
        "key_present": bool(api_key),
        "key_length": len(api_key),
        "request_domain": parsed.netloc,
        "proxy_disabled": True,
        "http_status": "unclear",
        "x_els_status": "unclear",
        "error": "unclear",
    }
    if not api_key:
        result["error"] = "ELSEVIER_API_KEY is not set"
        return result

    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(
            SCIENCEDIRECT_SEARCH_URL,
            params={"query": DIAGNOSIS_QUERY, "count": 1},
            headers=science_direct_headers(api_key),
            timeout=timeout,
        )
        result["http_status"] = response.status_code
        result["x_els_status"] = response.headers.get("X-ELS-Status", "unclear")
        if response.status_code >= 400:
            result["error"] = f"HTTP {response.status_code}"
    except Exception as exc:  # noqa: BLE001 - diagnostics should report failures without exposing secrets
        result["error"] = str(exc)
    finally:
        session.close()
    return result


def print_diagnosis(result: dict[str, Any]) -> None:
    for key in ["key_present", "key_length", "request_domain", "proxy_disabled", "http_status", "x_els_status", "error"]:
        print(f"{key}={result.get(key, 'unclear')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="ScienceDirect / Elsevier API utilities.")
    parser.add_argument("--diagnose-elsevier", action="store_true", help="Check ScienceDirect Search API access without using system proxies.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.diagnose_elsevier:
        print_diagnosis(diagnose_elsevier(timeout=args.timeout))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
