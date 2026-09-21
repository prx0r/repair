"""Repair Garden — Full Analysis Pipeline

Exports repair data to k1, runs constraint analysis, derives success rates.
This is the first time the system answers its own question:
"should I fix it, replace it, part it out, or scrap it?"

Usage:
    python3 repair_analyze.py              # full analysis
    python3 repair_analyze.py --export     # export only
    python3 repair_analyze.py --derive     # derive success rates
    python3 repair_analyze.py --k1         # k1 constraint analysis
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shared.persist import get_db
from shared.db import SCHEMA


# ============================================================
# Layer 1: Derive repair success rates from Open Repair data
# ============================================================

def derive_success_rates(conn) -> dict:
    """Compute repair success rates by category, brand, fault, barrier.

    This is the core Layer 1 derivation: what actually gets fixed?
    """
    print("=== REPAIR SUCCESS RATES ===\n")

    # Parse from normalized_json directly
    rows_raw = conn.execute("""
        SELECT normalized_json FROM source_record
        WHERE source_id = 'open_repair' AND valid = 1
    """).fetchall()

    category_status = defaultdict(Counter)
    brand_status = defaultdict(Counter)
    fault_counts = Counter()
    barrier_counts = Counter()

    for (normalized_json,) in rows_raw:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        cat = data.get('product_category', 'unknown')
        status = data.get('repair_status', 'unknown')
        brand = data.get('brand', 'unknown')
        problem = data.get('problem', '')
        barrier = data.get('repair_barrier', '')

        category_status[cat][status] += 1
        brand_status[brand][status] += 1
        if problem:
            fault_counts[problem] += 1
        if barrier:
            barrier_counts[barrier] += 1

    # Compute success rates
    results = {}

    print("--- By Product Category ---")
    print(f"  {'Category':30s} {'Total':>8s} {'Fixed':>8s} {'Rate':>8s}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")
    for cat in sorted(category_status, key=lambda c: sum(category_status[c].values()), reverse=True)[:20]:
        total = sum(category_status[cat].values())
        fixed = sum(v for k, v in category_status[cat].items() if k.lower() in ('fixed', 'repaired'))
        rate = (fixed / total * 100) if total > 0 else 0
        results[cat] = {'total': total, 'fixed': fixed, 'rate': rate}
        print(f"  {cat[:30]:30s} {total:>8,} {fixed:>8,} {rate:>7.1f}%")

    print()

    # By brand (top 20)
    print("--- By Brand (top 20) ---")
    print(f"  {'Brand':30s} {'Total':>8s} {'Fixed':>8s} {'Rate':>8s}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8}")
    for brand in sorted(brand_status, key=lambda b: sum(brand_status[b].values()), reverse=True)[:20]:
        total = sum(brand_status[brand].values())
        fixed = sum(v for k, v in brand_status[brand].items() if k.lower() in ('fixed', 'repaired'))
        rate = (fixed / total * 100) if total > 0 else 0
        print(f"  {brand[:30]:30s} {total:>8,} {fixed:>8,} {rate:>7.1f}%")

    print()

    # Top faults
    print("--- Top Faults ---")
    for fault, count in fault_counts.most_common(15):
        print(f"  {count:>6,}  {fault[:60]}")

    print()

    # Top barriers
    print("--- Top Repair Barriers ---")
    for barrier, count in barrier_counts.most_common(10):
        print(f"  {count:>6,}  {barrier[:60]}")

    return results


# ============================================================
# Layer 2: k1 constraint analysis
# ============================================================

def run_k1_analysis(conn) -> dict:
    """Export to k1 and run constraint analysis."""
    sys.path.insert(0, str(Path(__file__).parent.parent / 'k1'))

    from pow import Graph, Node, Edge, Observation
    from pow.constraint import constraint_pressure, unknowns, criticality, relieve

    print("\n=== k1 CONSTRAINT ANALYSIS ===\n")

    g = Graph()

    # Load Open Repair as nodes and edges
    rows = conn.execute("""
        SELECT source_native_id, normalized_json FROM source_record
        WHERE source_id = 'open_repair' AND valid = 1
        LIMIT 2000
    """).fetchall()

    brand_counts = Counter()
    category_counts = Counter()

    for native_id, normalized_json in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        brand = data.get('brand', '')
        category = data.get('product_category', '')
        model = data.get('model', '')
        fault = data.get('problem', '')
        repair_status = data.get('repair_status', '')

        if category:
            category_counts[category] += 1

        # Create device node
        if brand or model:
            device_id = f"repair:device:{brand}:{model}".lower().replace(' ', '_')
            if not g.node(device_id):
                g.add_node(Node(id=device_id, kind="device", label=f"{brand} {model}"))

        # Create fault node
        if fault:
            fault_id = f"repair:fault:{fault}".lower().replace(' ', '_')
            if not g.node(fault_id):
                g.add_node(Node(id=fault_id, kind="fault", label=fault[:80]))

            # Edge: device REQUIRES fix for fault
            if device_id:
                edge = Edge(source=device_id, target=fault_id, relation="REQUIRES")
                g.add_edge(edge)

                # Add repair success observation
                if repair_status in ('fixed', 'repaired'):
                    g.add_observation(Observation(
                        subject=device_id,
                        metric="repair_success",
                        value=1.0,
                        as_of=data.get('event_date', ''),
                        source='open_repair',
                    ))

    # Load market data as nodes and observations
    for source_id in ['cex', 'ebay_3market', 'trade_pricing', 'robotshop_uk']:
        mkt_rows = conn.execute("""
            SELECT source_native_id, normalized_json FROM source_record
            WHERE source_id = ? AND valid = 1
            LIMIT 500
        """, (source_id,)).fetchall()

        for native_id, normalized_json in mkt_rows:
            try:
                data = json.loads(normalized_json)
            except:
                continue

            listing_id = f"repair:{source_id}:{native_id}"
            name = data.get('name', '') or data.get('title', native_id)
            g.add_node(Node(id=listing_id, kind="listing", label=str(name)[:80]))

            # Add price observation
            price = data.get('sell_price') or data.get('price')
            if price is not None:
                g.add_observation(Observation(
                    subject=listing_id,
                    metric="price",
                    value=float(price),
                    unit="GBP",
                    source=source_id,
                ))

    print(f"Graph: {g.stats()}")
    print()

    # Category breakdown
    print("--- Devices by Category (from Open Repair) ---")
    for cat, count in category_counts.most_common(15):
        print(f"  {count:>6,}  {cat}")

    print()

    # Constraint pressure
    pressures = constraint_pressure(g)
    valued = [d for d in pressures if d.value is not None]
    unknown = [d for d in pressures if d.value is None]

    print(f"--- Constraint Pressure ---")
    print(f"  Nodes with data:    {len(valued)}")
    print(f"  Nodes UNKNOWN:      {len(unknown)}")
    if valued:
        print()
        print(f"  {'Node':50s} {'Pressure':>10s}")
        print(f"  {'-'*50} {'-'*10}")
        for d in sorted(valued, key=lambda x: x.value, reverse=True)[:15]:
            print(f"  {d.subject[:50]:50s} {d.value:>10.3f}")

    print()

    # Unknowns
    unks = unknowns(g)
    print(f"--- Unknowns ({len(unks)} nodes) ---")
    missing_counts = Counter()
    for node_id, metrics in unks.items():
        for m in metrics:
            missing_counts[m] += 1
    for metric, count in missing_counts.most_common():
        print(f"  {metric:30s} missing from {count:>6,} nodes")

    print()

    # Criticality
    crits = criticality(g)
    if crits:
        print("--- Criticality (top 10) ---")
        for d in crits[:10]:
            print(f"  {d.subject[:50]:50s} {d.value:.3f}")
    else:
        print("--- Criticality ---")
        print("  No paths found (graph is a forest)")

    print()

    # Relief
    reliefs = relieve(g)
    if reliefs:
        print("--- Relief (where adding capacity helps most) ---")
        for d in reliefs[:10]:
            print(f"  {d.subject[:50]:50s} {d.value:.3f}")
    else:
        print("--- Relief ---")
        print("  No relief needed (no constrained nodes)")

    return {
        "graph_stats": g.stats(),
        "pressure_valued": len(valued),
        "pressure_unknown": len(unknown),
        "unknowns": len(unks),
        "criticality": len(crits),
        "relief": len(reliefs),
    }


# ============================================================
# Layer 1: Market tape summary
# ============================================================

def market_tape_summary(conn) -> dict:
    """Summarize current market tape state."""
    print("\n=== MARKET TAPE STATUS ===\n")

    for source_id in ['cex', 'ebay_3market', 'trade_pricing', 'robotshop_uk']:
        count = conn.execute(
            "SELECT COUNT(*) FROM source_record WHERE source_id = ? AND valid = 1",
            (source_id,)
        ).fetchone()[0]

        versions = conn.execute(
            "SELECT COUNT(*) FROM source_record WHERE source_id = ? AND source_record_id LIKE '%:v%'",
            (source_id,)
        ).fetchone()[0]

        mkt = conn.execute(
            "SELECT COUNT(*) FROM market_observation mo "
            "JOIN source_record sr ON mo.source_record_id = sr.source_record_id "
            "WHERE sr.source_id = ?",
            (source_id,)
        ).fetchone()[0]

        print(f"  {source_id:20s}  records: {count:>6,}  versions: {versions:>4,}  observations: {mkt:>6,}")

    # Collector runs
    print()
    rows = conn.execute("""
        SELECT source_id, status, COUNT(*) as runs,
               MAX(finished_at) as last_run
        FROM collector_run
        GROUP BY source_id, status
        ORDER BY source_id
    """).fetchall()

    print("--- Collector Runs ---")
    for source_id, status, runs, last_run in rows:
        lr = (last_run or '')[:19]
        print(f"  {source_id:20s}  {status:8s}  {runs:>4,} runs  last: {lr}")

    return {}


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Repair Garden Analysis Pipeline')
    parser.add_argument('--export', action='store_true', help='Export to k1 format only')
    parser.add_argument('--derive', action='store_true', help='Derive success rates only')
    parser.add_argument('--k1', action='store_true', help='k1 constraint analysis only')
    parser.add_argument('--tape', action='store_true', help='Market tape summary only')
    args = parser.parse_args()

    conn = get_db()

    run_all = not (args.export or args.derive or args.k1 or args.tape)

    if args.export or run_all:
        from export_k1 import export_all
        print("=== EXPORT TO k1 ===\n")
        stats = export_all()
        print()

    if args.derive or run_all:
        derive_success_rates(conn)
        print()

    if args.tape or run_all:
        market_tape_summary(conn)
        print()

    if args.k1 or run_all:
        run_k1_analysis(conn)

    conn.close()


if __name__ == '__main__':
    main()
