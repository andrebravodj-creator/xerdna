"""
One-time fetch utility for HGNC (HUGO Gene Nomenclature Committee) gene
records -- the ONE file in this engine that performs network access.

NOT imported by any test, by GRAPH/engine/sources/hgnc_ingest.py, or by
GRAPH/engine/sources/hgnc_mapper.py. It is a standalone, manually-invoked
script whose sole job is to populate
GRAPH/engine/sources/fixtures/hgnc_sample.json -- once. Every downstream
step in this milestone (mapping, ingestion, tests) reads only that cached
file and never touches the network.

Verified access method (2026-07-10, via live request, not assumed):
  Base URL:  https://rest.genenames.org/
  Endpoint:  /fetch/{field}/{term}
  Headers:   Accept: application/json
  Response:  {"response": {"numFound": int, "docs": [ {...gene record...} ]}}
  Rate limit: HGNC's own documentation asks for at most 10 requests/second --
    trivially satisfied by this milestone's "very small sample" (3 genes),
    but a small delay between requests is included anyway as good practice.
  Source: https://www.genenames.org/help/rest/

Run manually:  python -m GRAPH.engine.sources.hgnc_fetch
Re-running overwrites the fixture with a fresh fetch -- not part of any
automated pipeline (no continuous sync, no background jobs, per Milestone
004's explicit scope).
"""

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HGNC_BASE_URL = "https://rest.genenames.org/fetch/symbol"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "hgnc_sample.json"

# A very small, hand-picked sample of stable, well-known, unambiguous human
# gene symbols -- not a bulk fetch, not a query result set (Milestone 004
# scope: "fetch only a very small sample").
SAMPLE_SYMBOLS = ["BRCA1", "TP53", "EGFR"]


def fetch_one(symbol: str) -> dict:
    """Fetch a single gene record by symbol. Raises on any non-200 response."""
    url = f"{HGNC_BASE_URL}/{symbol}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"HGNC fetch for {symbol!r} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def fetch_sample_and_cache() -> Path:
    """Fetch SAMPLE_SYMBOLS and write the raw, unmodified responses to the fixture file."""
    records = []
    for symbol in SAMPLE_SYMBOLS:
        raw_response = fetch_one(symbol)
        docs = raw_response.get("response", {}).get("docs", [])
        if len(docs) != 1:
            raise RuntimeError(f"expected exactly 1 doc for symbol {symbol!r}, got {len(docs)}")
        records.append(docs[0])
        time.sleep(0.15)  # well under HGNC's 10 req/s limit

    fixture = {
        "source": "HGNC (HUGO Gene Nomenclature Committee)",
        "source_url": "https://rest.genenames.org/",
        "access_method": "GET /fetch/symbol/{symbol}, Accept: application/json",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "docs": records,
    }
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(fixture, indent=2, sort_keys=True), encoding="utf-8")
    return FIXTURE_PATH


if __name__ == "__main__":
    path = fetch_sample_and_cache()
    print(f"Wrote {path}")
