"""UKGraph Normalization Pipeline.

Every observation flows through:
1. collect_raw() - pull from source
2. normalize() - raw → canonical form
3. enrich() - add provenance, freshness, quality
4. store() - save to JSONL

The pipeline ensures:
- Every observation has observation_id (deterministic hash)
- Every observation has provenance (source, hash, timestamp, licence)
- Every observation has truth_class
- No raw data is thrown away
"""

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Directory structure
# ---------------------------------------------------------------------------

DATAGARDEN_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_ROOT = DATAGARDEN_ROOT / "canonical"

GARDENS = {
    "ukopportunity": CANONICAL_ROOT / "ukopportunity",
    "ukproducts": CANONICAL_ROOT / "ukproducts",
    "ukgraph": CANONICAL_ROOT / "ukgraph",
    "ukadmin": CANONICAL_ROOT / "ukadmin",
    "breadup": CANONICAL_ROOT / "breadup",
    "powpowpow": CANONICAL_ROOT / "powpowpow",
}

# ---------------------------------------------------------------------------
# Thread-safe JSONL writer
# ---------------------------------------------------------------------------

_locks: Dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_lock(filepath: str) -> threading.Lock:
    with _locks_lock:
        if filepath not in _locks:
            _locks[filepath] = threading.Lock()
        return _locks[filepath]


def _append_jsonl(filepath: Path, records: List[dict]) -> int:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    lock = _get_lock(str(filepath))
    with lock:
        with open(filepath, "a") as f:
            count = 0
            for rec in records:
                f.write(json.dumps(rec, default=str) + "\n")
                count += 1
        return count


def _read_jsonl(filepath: Path, limit: int = 0) -> List[dict]:
    records = []
    if not filepath.exists():
        return records
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
                if limit and len(records) >= limit:
                    break
    return records


def _read_all_jsonl(directory: Path, limit: int = 0) -> List[dict]:
    records = []
    if not directory.exists():
        return records
    for root, dirs, files in os.walk(directory):
        for fname in sorted(files):
            if fname.endswith(".jsonl"):
                filepath = Path(root) / fname
                remaining = limit - len(records) if limit else 0
                records.extend(_read_jsonl(filepath, remaining))
                if limit and len(records) >= limit:
                    return records[:limit]
    return records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _float(val: Any) -> float:
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _int(val: Any) -> int:
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _sha256(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serialisable value."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_effective_at(raw: dict, *date_keys) -> str:
    """Try multiple date keys, return ISO string or empty."""
    for key in date_keys:
        val = raw.get(key)
        if val:
            s = str(val).strip()
            if "T" in s:
                return s
            if len(s) == 10 and s[4] == "-" and s[7] == "-":
                return s
    return ""


# ---------------------------------------------------------------------------
# Normalizers — raw → canonical value dict
# ---------------------------------------------------------------------------

def normalize_planning(raw: dict) -> dict:
    """Normalise a planning.data.gov.uk entity to canonical form.

    Raw shape (from planning.data.gov.uk entity.json):
        {
            "entry-date": "2025-05-30",
            "entity": 123,
            "reference": "23/08472/FUL",
            "name": "10 Downing Street",
            "description": "Erection of single storey rear extension",
            "decision-date": "2025-06-15",
            "organisation-entity": "4010",
            "typology": "authority",
            ...
        }
    """
    entity_id = _int(raw.get("entity"))
    reference = _str(raw.get("reference"))
    entry_date = _str(raw.get("entry-date"))
    start_date = _str(raw.get("start-date"))
    decision_date = _str(raw.get("decision-date"))
    name = _str(raw.get("name"))
    description = _str(raw.get("description"))[:500]
    org_entity = _str(raw.get("organisation-entity"))
    typology = _str(raw.get("typology"))

    has_decision = bool(decision_date)
    status = "decided" if has_decision else "pending"

    value = {
        "entity_id": entity_id,
        "reference": reference,
        "name": name,
        "description": description,
        "status": status,
        "entry_date": entry_date,
        "start_date": start_date,
        "decision_date": decision_date,
        "organisation_entity": org_entity,
        "typology": typology,
    }

    effective_at = _extract_effective_at(raw, "entry-date", "start-date")

    entity_ref = reference or f"planning_{entity_id}"

    return {
        "metric": "planning_application",
        "entity_type": "planning_application",
        "entity_ref": entity_ref,
        "effective_at": effective_at,
        "value": value,
    }


def normalize_contract(raw: dict) -> dict:
    """Normalise a Contracts Finder record to canonical form.

    Raw shape (from contracts_finder.service.gov.uk):
        {
            "item": {
                "id": "CF-0036100...",
                "title": "Highway Maintenance Contract",
                "description": "...",
                "organisationName": "Oldham Council",
                "awardedValue": 123456,
                "awardedDate": "2025-06-10",
                "awardedSupplier": "ACME Ltd",
                "noticeStatus": "Awarded",
                ...
            }
        }
    """
    item = raw.get("item", raw)

    contract_id = _str(item.get("id")) or _str(item.get("noticeIdentifier"))
    title = _str(item.get("title"))
    description = _str(item.get("description"))[:500]
    buyer = _str(item.get("organisationName"))
    buyer_location = _str(item.get("postcode"))
    value_gbp = _float(item.get("awardedValue"))
    award_date = _str(item.get("awardedDate")) or _str(item.get("publishedDate"))
    supplier = _str(item.get("awardedSupplier"))
    status = _str(item.get("noticeStatus"))
    cpv_codes = item.get("cpvCodes", [])
    cpv_description = _str(item.get("cpvDescription"))

    effective_at = award_date

    entity_ref = contract_id or f"contract_{hashlib.md5(title.encode()).hexdigest()[:12]}"

    value = {
        "contract_id": contract_id,
        "title": title,
        "description": description,
        "buyer": buyer,
        "buyer_location": buyer_location,
        "value_gbp": value_gbp,
        "award_date": award_date,
        "supplier": supplier,
        "status": status,
        "cpv_codes": cpv_codes,
        "cpv_description": cpv_description,
    }

    return {
        "metric": "contract_award",
        "entity_type": "contract",
        "entity_ref": f"CF-{entity_ref}" if not entity_ref.startswith("CF-") else entity_ref,
        "effective_at": effective_at,
        "value": value,
    }


def normalize_ebay(raw: dict) -> dict:
    """Normalise an eBay UK sold listing to canonical form.

    Raw shape (from Apify ebay-sold-scraper):
        {
            "itemId": "123456",
            "title": "Sony WH-1000XM5 Headphones",
            "soldPrice": 189.99,
            "soldCurrency": "GBP",
            "endedAt": "2025-09-15T14:30:00Z",
            "condition": "Used",
            "keyword": "sony headphones",
            ...
        }
    """
    item_id = _str(raw.get("itemId"))
    title = _str(raw.get("title"))
    sold_price = _float(raw.get("soldPrice"))
    currency = _str(raw.get("soldCurrency")) or "GBP"
    ended_at = _str(raw.get("endedAt"))
    condition = _str(raw.get("condition"))
    keyword = _str(raw.get("keyword"))

    sold_date = ended_at
    if sold_date and "T" in sold_date:
        sold_date = sold_date.split("T")[0]

    effective_at = sold_date

    entity_ref = f"ebay_{item_id}" if item_id else f"ebay_{hashlib.md5(title.encode()).hexdigest()[:12]}"

    value = {
        "item_id": item_id,
        "title": title,
        "sold_price": sold_price,
        "currency": currency,
        "ended_at": ended_at,
        "condition": condition,
        "keyword": keyword,
    }

    return {
        "metric": "item_sold",
        "entity_type": "product",
        "entity_ref": entity_ref,
        "effective_at": effective_at,
        "value": value,
    }


def normalize_ons(raw: dict) -> dict:
    """Normalise an ONS labour-market datum to canonical form.

    Raw shape (from ONS API / ons_jobs collector):
        {
            "source": "ons_bulletin",
            "title": "UK Labour Market",
            "summary": "Employment statistics",
            "release_date": "2026-08-18",
            "uri": "https://...",
            "query": "labour market",
            ...
        }

    Or the wrapped envelope:
        {
            "data_type": "labour_demand",
            "data": { ... above ... }
        }
    """
    data = raw.get("data", raw)
    source_type = _str(data.get("source")) or _str(raw.get("data_type")) or "ons_bulletin"
    title = _str(data.get("title"))
    summary = _str(data.get("summary"))[:500]
    release_date = _str(data.get("release_date")) or _str(data.get("date"))
    uri = _str(data.get("uri")) or _str(data.get("url"))
    query = _str(data.get("query"))

    effective_at = release_date

    value = {
        "source_type": source_type,
        "title": title,
        "summary": summary,
        "release_date": release_date,
        "uri": uri,
        "query": query,
    }

    return {
        "metric": "employment_signal",
        "entity_type": "dataset",
        "entity_ref": "ons_labour",
        "effective_at": effective_at,
        "value": value,
    }


# ---------------------------------------------------------------------------
# Pipeline functions
# ---------------------------------------------------------------------------

NORMALIZERS = {
    "planning_data": normalize_planning,
    "contracts_finder": normalize_contract,
    "ebay_uk_sold": normalize_ebay,
    "ons_labour": normalize_ons,
}

LICENCES = {
    "planning_data": "OGL",
    "contracts_finder": "OGL",
    "ebay_uk_sold": "proprietary",
    "ons_labour": "OGL",
}

SOURCE_URLS = {
    "planning_data": "https://www.planning.data.gov.uk/entity.json",
    "planning_data_api": "https://www.planning.data.gov.uk/entity.json",
    "contracts_finder": "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/JSON",
    "ebay_uk_sold": "https://www.ebay.co.uk",
    "ons_labour": "https://api.beta.ons.gov.uk/v1",
}

SOURCE_IDS = {
    "planning_data": "planning_data_api",
    "contracts_finder": "contracts_finder",
    "ebay_uk_sold": "ebay_uk_sold",
    "ons_labour": "ons_labour",
}

SOURCE_TO_GARDEN = {
    "planning_data": "ukopportunity",
    "contracts_finder": "ukopportunity",
    "ebay_uk_sold": "ukproducts",
    "ons_labour": "ukopportunity",
}


def compute_observation_id(obs: dict) -> str:
    """Deterministic SHA-256 hash of observation identity fields.

    Uses garden, source_id, entity_ref, metric, effective_at — the fields
    that uniquely identify *what* was observed *when* from *where*.
    """
    identity = {
        "garden": obs.get("garden", ""),
        "source_id": obs.get("source_id", ""),
        "entity_ref": obs.get("entity_ref", ""),
        "metric": obs.get("metric", ""),
        "effective_at": obs.get("effective_at", ""),
    }
    return _sha256(identity)[:16]


def enrich_observation(obs: dict, source_id: str, licence: str) -> dict:
    """Add provenance, observation_id, and truth_class to a normalised record.

    Mutates and returns the same dict.
    """
    obs["source_id"] = source_id
    obs["licence"] = licence
    obs["source_url"] = SOURCE_URLS.get(source_id, "")
    obs["observed_at"] = _now_iso()
    obs["raw_hash"] = _sha256(obs.get("value", {}))
    obs["truth_class"] = "KNOWN"
    obs["observation_id"] = compute_observation_id(obs)
    return obs


def normalize(source_key: str, raw: dict) -> dict:
    """Full pipeline: raw → normalised → enriched canonical observation.

    Args:
        source_key: one of 'planning_data', 'contracts_finder', 'ebay_uk_sold', 'ons_labour'
        raw: the raw record as collected

    Returns:
        Complete canonical observation dict ready for storage
    """
    source_key = source_key.lower().strip()
    if source_key not in NORMALIZERS:
        raise ValueError(
            f"Unknown source: {source_key!r}. Must be one of: {list(NORMALIZERS.keys())}"
        )

    normalizer = NORMALIZERS[source_key]
    obs = normalizer(raw)

    obs["garden"] = SOURCE_TO_GARDEN[source_key]
    obs["source_id"] = SOURCE_IDS[source_key]

    licence = LICENCES[source_key]
    return enrich_observation(obs, obs["source_id"], licence)


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def store_observation(garden: str, obs: dict) -> str:
    """Store a single canonical observation to JSONL.

    Returns the observation_id.
    """
    garden = garden.lower().strip()
    if garden not in GARDENS:
        raise ValueError(f"Unknown garden: {garden!r}")

    garden_dir = GARDENS[garden]
    garden_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = garden_dir / f"{date_str}.jsonl"
    _append_jsonl(filepath, [obs])
    return obs.get("observation_id", "")


def store_observation_batch(garden: str, observations: List[dict]) -> int:
    """Store a batch of canonical observations. Returns count stored."""
    garden = garden.lower().strip()
    if garden not in GARDENS:
        raise ValueError(f"Unknown garden: {garden!r}")

    garden_dir = GARDENS[garden]
    garden_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = garden_dir / f"{date_str}.jsonl"
    return _append_jsonl(filepath, observations)


def load_observations(garden: str, source: str = None, limit: int = 1000) -> list:
    """Load canonical observations for a garden.

    Args:
        garden: 'ukopportunity' or 'ukproducts'
        source: optional source_id filter (e.g. 'planning_data_api')
        limit: max records to return

    Returns:
        List of observation dicts
    """
    garden = garden.lower().strip()
    if garden not in GARDENS:
        raise ValueError(f"Unknown garden: {garden!r}")

    garden_dir = GARDENS[garden]
    records = _read_all_jsonl(garden_dir, limit=0)

    if source:
        records = [r for r in records if r.get("source_id") == source]

    return records[:limit]


def search_observations(garden: str, query: str, limit: int = 50) -> list:
    """Search observations by text query across all string fields."""
    garden = garden.lower().strip()
    if garden not in GARDENS:
        raise ValueError(f"Unknown garden: {garden!r}")

    query_lower = query.lower()
    all_records = load_observations(garden, limit=10000)

    matches = []
    for rec in all_records:
        for val in rec.values():
            if isinstance(val, str) and query_lower in val.lower():
                matches.append(rec)
                break
            elif isinstance(val, (int, float)) and query_lower in str(val):
                matches.append(rec)
                break
            elif isinstance(val, dict):
                text = json.dumps(val, default=str).lower()
                if query_lower in text:
                    matches.append(rec)
                    break

        if limit and len(matches) >= limit:
            break

    return matches


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """CLI entry point for testing the pipeline."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.normalize <command> [args]")
        print("Commands:")
        print("  stats <garden>              - Show garden statistics")
        print("  search <garden> <query>     - Search observations")
        print("  load <garden> [source] [limit]")
        print("  test                        - Run integration test")
        return

    cmd = sys.argv[1]

    if cmd == "stats":
        garden = sys.argv[2] if len(sys.argv) > 2 else "ukopportunity"
        records = load_observations(garden, limit=0)
        sources = {}
        for r in records:
            s = r.get("source_id", "unknown")
            sources[s] = sources.get(s, 0) + 1
        print(json.dumps({
            "garden": garden,
            "record_count": len(records),
            "sources": sources,
        }, indent=2))

    elif cmd == "search":
        if len(sys.argv) < 4:
            print("Usage: python -m core.normalize search <garden> <query>")
            return
        garden = sys.argv[2]
        query = sys.argv[3]
        results = search_observations(garden, query)
        print(f"Found {len(results)} results:")
        for r in results[:10]:
            print(json.dumps(r, indent=2))

    elif cmd == "load":
        garden = sys.argv[2] if len(sys.argv) > 2 else "ukopportunity"
        source = None
        limit = 10
        for arg in sys.argv[3:]:
            if arg.isdigit():
                limit = int(arg)
            elif arg != "--":
                source = arg
        records = load_observations(garden, source=source, limit=limit)
        print(f"Loaded {len(records)} records:")
        for r in records[:5]:
            print(json.dumps(r, indent=2))

    elif cmd == "test":
        print("=== UKGraph Normalization Pipeline Test ===\n")

        # Planning
        print("1. Planning Data...")
        raw_planning = {
            "entry-date": "2025-05-30",
            "entity": 40100672,
            "reference": "23/08472/FUL",
            "name": "15 High Street, Oldham",
            "description": "Erection of single storey rear extension to dwelling house",
            "decision-date": "2025-06-15",
            "organisation-entity": "4010",
            "typology": "authority",
        }
        obs = normalize("planning_data", raw_planning)
        store_observation(obs["garden"], obs)
        print(f"   metric={obs['metric']}  ref={obs['entity_ref']}  id={obs['observation_id']}")
        print(f"   licence={obs['licence']}  truth_class={obs['truth_class']}")
        print(f"   raw_hash={obs['raw_hash'][:16]}...")

        # Contracts
        print("\n2. Contracts Finder...")
        raw_contract = {
            "item": {
                "id": "CF-0036100532",
                "title": "Highway Maintenance and Surface Dressing",
                "description": "Contract for highway maintenance works across the borough",
                "organisationName": "Oldham Metropolitan Borough Council",
                "awardedValue": 2450000,
                "awardedDate": "2025-06-10",
                "awardedSupplier": "Tarmac Trading Ltd",
                "noticeStatus": "Awarded",
                "postcode": "OL1 1AA",
            }
        }
        obs = normalize("contracts_finder", raw_contract)
        store_observation(obs["garden"], obs)
        print(f"   metric={obs['metric']}  ref={obs['entity_ref']}  id={obs['observation_id']}")
        print(f"   value_gbp={obs['value']['value_gbp']}")

        # eBay
        print("\n3. eBay UK Sold...")
        raw_ebay = {
            "itemId": "285837462910",
            "title": "Sony WH-1000XM5 Wireless Headphones - Black",
            "soldPrice": 189.99,
            "soldCurrency": "GBP",
            "endedAt": "2025-09-15T14:30:00Z",
            "condition": "Used - Like New",
            "keyword": "sony headphones",
        }
        obs = normalize("ebay_uk_sold", raw_ebay)
        store_observation(obs["garden"], obs)
        print(f"   metric={obs['metric']}  ref={obs['entity_ref']}  id={obs['observation_id']}")
        print(f"   sold_price={obs['value']['sold_price']}")

        # ONS
        print("\n4. ONS Labour...")
        raw_ons = {
            "source": "ons_bulletin",
            "title": "UK Labour Market Bulletin",
            "summary": "Employment rate was 75.2% in June to August 2025",
            "release_date": "2025-10-14",
            "uri": "https://www.ons.gov.uk/employmentandlabourmarket/...",
            "query": "labour market",
        }
        obs = normalize("ons_labour", raw_ons)
        store_observation(obs["garden"], obs)
        print(f"   metric={obs['metric']}  ref={obs['entity_ref']}  id={obs['observation_id']}")

        # Load back
        print("\n5. Load round-trip...")
        for garden in ["ukopportunity", "ukproducts"]:
            records = load_observations(garden, limit=100)
            sources = {}
            for r in records:
                s = r.get("source_id", "?")
                sources[s] = sources.get(s, 0) + 1
            print(f"   {garden}: {len(records)} records — {sources}")

        print("\n=== Pipeline test complete ===")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
