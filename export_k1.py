"""Repair → POWKernel export adapter.

Reads from repair's SQLite database and exports as k1-format
Nodes, Edges, Observations, and Evidence.

Repair data maps to k1:
  AssetPassport  →  NODE (kind=asset)
  Component      →  NODE (kind=component)
  PartOffer      →  NODE (kind=part)
  FaultRecord    →  EDGE  (device REQUIRES fix)
  Substitution   →  EDGE  (part REQUIRES substitute)
  MarketListing  →  OBSERVATION (price snapshots)
  Open Repair    →  EVIDENCE (repair outcomes)
  derived_fact   →  DERIVATION
"""

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db_path():
    return Path(os.environ.get('REPAIR_DB', str(Path(__file__).parent / 'warehouse' / 'repair.db')))


def _content_id(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def export_nodes(conn) -> list[dict]:
    """Export repair entities as k1 NODEs."""
    nodes = []

    # Export source records as NODEs (each distinct native_id is an entity)
    rows = conn.execute("""
        SELECT DISTINCT source_id, source_native_id, normalized_json
        FROM source_record
        WHERE valid = 1
    """).fetchall()

    for source_id, native_id, normalized_json in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        # Determine node kind from source
        kind_map = {
            'open_repair': 'repair_record',
            'cex': 'listing',
            'ebay_3market': 'listing',
            'trade_pricing': 'listing',
            'robotshop_uk': 'listing',
            'partsdb': 'component',
            'opss_recalls': 'recall',
        }
        kind = kind_map.get(source_id, 'entity')

        # Extract useful label
        label = data.get('name', '') or data.get('title', '') or native_id

        node_id = f"repair:{source_id}:{native_id}"
        nodes.append({
            "id": node_id,
            "kind": kind,
            "label": str(label)[:200],
            "source": source_id,
        })

    return nodes


def export_edges(conn) -> list[dict]:
    """Export repair dependency relationships as k1 EDGEs (REQUIRES only)."""
    edges = []

    # Open Repair: device → component (implicit requirement)
    rows = conn.execute("""
        SELECT source_native_id, normalized_json
        FROM source_record
        WHERE source_id = 'open_repair' AND valid = 1
    """).fetchall()

    for native_id, normalized_json in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        category = data.get('product_category', '')
        brand = data.get('brand', '')
        model = data.get('model', '')
        fault = data.get('problem', '')
        barrier = data.get('repair_barrier', '')

        if not category:
            continue

        device_id = f"repair:open_repair:device:{brand}:{model}".lower().replace(' ', '_')
        fault_id = f"repair:open_repair:fault:{fault}".lower().replace(' ', '_')

        # Device REQUIRES fix for fault
        if fault:
            edges.append({
                "source": device_id,
                "target": fault_id,
                "relation": "REQUIRES",
                "requirement": {"quantity_per_unit": None, "unit": None},
                "supply": {
                    "capacity": None,
                    "utilisation": None,
                    "growth_rate": None,
                    "lead_time_days": None,
                },
                "substitution": {
                    "substitutability": None,
                    "switching_cost": None,
                },
                "timing": {
                    "needed_by": None,
                    "capacity_available_by": None,
                },
                "meta": {"fault": fault, "barrier": barrier},
            })

    # Parts from marketplace: device REQUIRES part
    for source_id in ['cex', 'ebay_3market', 'trade_pricing', 'robotshop_uk']:
        rows = conn.execute("""
            SELECT source_native_id, normalized_json
            FROM source_record
            WHERE source_id = ? AND valid = 1
        """, (source_id,)).fetchall()

        for native_id, normalized_json in rows:
            try:
                data = json.loads(normalized_json)
            except:
                continue

            category = data.get('category', '')
            name = data.get('name', '')
            if not category or not name:
                continue

            listing_id = f"repair:{source_id}:{native_id}"
            category_node = f"repair:category:{category}".lower().replace(' ', '_')

            # Listing REQUIRES category (listing is instance of category)
            edges.append({
                "source": listing_id,
                "target": category_node,
                "relation": "REQUIRES",
                "meta": {"context": "listing_instance_of"},
            })

    return edges


def export_observations(conn) -> list[dict]:
    """Export repair observations as k1 OBSERVATIONs."""
    observations = []

    # Market observations (price tape)
    rows = conn.execute("""
        SELECT mo.source_record_id, mo.observed_at, mo.price, mo.currency,
               mo.availability, mo.condition, mo.market,
               sr.source_id, sr.source_native_id
        FROM market_observation mo
        JOIN source_record sr ON mo.source_record_id = sr.source_record_id
    """).fetchall()

    for (sr_id, observed_at, price, currency, availability,
         condition, market, source_id, native_id) in rows:

        subject = f"repair:{source_id}:{native_id}"
        observations.append({
            "subject": subject,
            "metric": "price",
            "value": price,
            "unit": currency or "GBP",
            "as_of": observed_at,
            "source": source_id,
            "meta": {
                "availability": availability,
                "condition": condition,
                "market": market,
            },
        })

    # Source record observations (non-price)
    rows = conn.execute("""
        SELECT source_id, source_native_id, normalized_json, retrieved_at
        FROM source_record
        WHERE valid = 1 AND source_id NOT IN ('cex', 'ebay_3market', 'trade_pricing', 'robotshop_uk')
    """).fetchall()

    for source_id, native_id, normalized_json, retrieved_at in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        subject = f"repair:{source_id}:{native_id}"

        # Extract numeric fields as observations
        for key in ['sell_price', 'buy_price', 'exchange_price', 'price',
                     'stock_qty', 'lead_time_days', 'unit_price_gbp']:
            val = data.get(key)
            if val is not None:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    continue
                observations.append({
                    "subject": subject,
                    "metric": key,
                    "value": val,
                    "unit": "GBP" if "price" in key else "",
                    "as_of": retrieved_at,
                    "source": source_id,
                })

    return observations


def export_evidence(conn) -> list[dict]:
    """Export repair evidence (source receipts, open repair outcomes)."""
    evidence = []

    # Open Repair outcomes as evidence
    rows = conn.execute("""
        SELECT source_native_id, normalized_json, retrieved_at
        FROM source_record
        WHERE source_id = 'open_repair' AND valid = 1
    """).fetchall()

    for native_id, normalized_json, retrieved_at in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        repair_status = data.get('repair_status', '')
        if not repair_status:
            continue

        brand = data.get('brand', '')
        model = data.get('model', '')
        problem = data.get('problem', '')
        barrier = data.get('repair_barrier', '')

        claim = f"Device {brand} {model} with fault '{problem}': repair {repair_status}"
        if barrier:
            claim += f" (barrier: {barrier})"

        target = f"repair:open_repair:device:{brand}:{model}".lower().replace(' ', '_')

        evidence.append({
            "claim": claim,
            "target": target,
            "direction": "QUANTIFIES",
            "publisher": data.get('data_provider', 'open_repair'),
            "observed_at": data.get('event_date', retrieved_at),
            "source_uri": f"open_repair:{native_id}",
            "value": 1 if repair_status == 'repaired' else 0,
            "unit": "repair_success",
        })

    return evidence


def export_derived_facts(conn) -> list[dict]:
    """Export repair derived facts as k1 DERIVATIONs."""
    derivations = []

    rows = conn.execute("""
        SELECT entity_id, metric, value, method_id, method_version,
               input_observation_ids, computed_at
        FROM derived_fact
    """).fetchall()

    for entity_id, metric, value, method_id, method_version, input_ids, computed_at in rows:
        try:
            val = float(value)
        except (ValueError, TypeError):
            val = value

        derivations.append({
            "kind": metric,
            "subject": entity_id or "",
            "value": val,
            "as_of": computed_at,
            "model": f"{method_id}/{method_version}" if method_id else "",
            "inputs": json.loads(input_ids) if input_ids else [],
        })

    return derivations


def export_all(output_dir: str = None) -> dict:
    """Export entire repair database to k1 format.

    Writes JSONL files to output_dir (default: repair/k1_export/).
    Returns stats.
    """
    db_path = _db_path()
    if not db_path.exists():
        return {"error": f"Database not found: {db_path}"}

    conn = sqlite3.connect(str(db_path))

    if output_dir is None:
        output_dir = str(Path(__file__).parent.parent / 'k1_export')
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    exports = {
        "node": export_nodes(conn),
        "edge": export_edges(conn),
        "observation": export_observations(conn),
        "evidence": export_evidence(conn),
        "derivation": export_derived_facts(conn),
    }

    stats = {}
    for kind, items in exports.items():
        path = out / f"{kind}.jsonl"
        with open(path, 'w') as f:
            for item in items:
                item["_id"] = _content_id(item)
                f.write(json.dumps(item, default=str) + "\n")
        stats[kind] = len(items)

    conn.close()

    print(f"Exported to {out}/")
    for kind, count in stats.items():
        print(f"  {kind:15s} {count:>8,}")

    return stats


if __name__ == '__main__':
    export_all()
