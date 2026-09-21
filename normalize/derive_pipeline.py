"""Derive Pipeline — source records → derived facts.

NOTE: This module still references the legacy `observations` table.
It needs rewriting to use `source_record` and `derived_fact` via shared/persist.py.
For now, fix imports and paths so it doesn't crash.

TODO: Rewrite to read from source_record, write to derived_fact.
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.db import get_db, get_db_path


def derive_repair_success_rates(conn):
    """Compute repair success rates from Open Repair data.

    Reads from source_record (not legacy observations table).
    """
    rows = conn.execute("""
        SELECT normalized_json FROM source_record
        WHERE source_id='open_repair' AND valid = 1
    """).fetchall()

    outcomes = {}
    for (normalized_json,) in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        item_type = data.get('product_category', 'unknown')
        outcome = data.get('repair_status', 'unknown')

        if item_type not in outcomes:
            outcomes[item_type] = {'fixed': 0, 'not_fixed': 0, 'partly_fixed': 0, 'end_of_life': 0, 'total': 0}

        outcomes[item_type]['total'] += 1
        if outcome.lower() in ('fixed', 'repaired'):
            outcomes[item_type]['fixed'] += 1
        elif outcome.lower() in ('not fixed', 'not repairable'):
            outcomes[item_type]['not_fixed'] += 1
        elif outcome.lower() in ('partly fixed', 'repairable'):
            outcomes[item_type]['partly_fixed'] += 1
        elif outcome.lower() == 'end of life':
            outcomes[item_type]['end_of_life'] += 1

    count = 0
    for item_type, counts in outcomes.items():
        if counts['total'] < 10:
            continue
        success_rate = counts['fixed'] / counts['total']
        derived = {
            'item_type': item_type,
            'total_repairs': counts['total'],
            'success_rate': round(success_rate, 3),
            'fixed': counts['fixed'],
            'not_fixed': counts['not_fixed'],
            'partly_fixed': counts['partly_fixed'],
            'end_of_life': counts['end_of_life'],
        }

        derived_id = hashlib.sha256(
            json.dumps({"kind": "repair_success", "subject": item_type}, sort_keys=True).encode()
        ).hexdigest()

        conn.execute(
            "INSERT OR REPLACE INTO derived_fact "
            "(derived_id, source_id, entity_id, metric, value, method_id, method_version, "
            "input_observation_ids, computed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (derived_id, 'derive_pipeline', f'repair_success:{item_type}', 'repair_success',
             json.dumps(derived, default=str), 'repair_success', 'v1',
             '[]', datetime.now(timezone.utc).isoformat())
        )
        count += 1

    conn.commit()
    return count


def derive_failure_distribution(conn):
    """Compute fault distribution from Open Repair data.

    Reads from source_record (not legacy observations table).
    """
    rows = conn.execute("""
        SELECT normalized_json FROM source_record
        WHERE source_id='open_repair' AND valid = 1
    """).fetchall()

    faults = {}
    for (normalized_json,) in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        item_type = data.get('product_category', 'unknown')
        fault = data.get('problem', 'unknown')[:80]

        if item_type not in faults:
            faults[item_type] = {}
        if fault not in faults[item_type]:
            faults[item_type][fault] = 0
        faults[item_type][fault] += 1

    count = 0
    for item_type, fault_counts in faults.items():
        total = sum(fault_counts.values())
        if total < 10:
            continue
        top_faults = sorted(fault_counts.items(), key=lambda x: -x[1])[:10]
        derived = {
            'item_type': item_type,
            'total_records': total,
            'top_faults': [{'fault': f, 'count': c, 'pct': round(c/total*100, 1)} for f, c in top_faults],
        }

        derived_id = hashlib.sha256(
            json.dumps({"kind": "fault_distribution", "subject": item_type}, sort_keys=True).encode()
        ).hexdigest()

        conn.execute(
            "INSERT OR REPLACE INTO derived_fact "
            "(derived_id, source_id, entity_id, metric, value, method_id, method_version, "
            "input_observation_ids, computed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (derived_id, 'derive_pipeline', f'fault_dist:{item_type}', 'fault_distribution',
             json.dumps(derived, default=str), 'fault_distribution', 'v1',
             '[]', datetime.now(timezone.utc).isoformat())
        )
        count += 1

    conn.commit()
    return count


def run():
    print('Derive Pipeline')
    print('=' * 40)

    conn = get_db()

    print('  Computing repair success rates...')
    n = derive_repair_success_rates(conn)
    print(f'    {n} item types with success rates')

    print('  Computing failure distributions...')
    n = derive_failure_distribution(conn)
    print(f'    {n} item types with fault distributions')

    # Show derived facts
    print('\n  Repair success rates (top 10):')
    rows = conn.execute("""
        SELECT entity_id, value FROM derived_fact
        WHERE metric='repair_success'
        ORDER BY computed_at DESC LIMIT 10
    """).fetchall()
    for entity_id, value_json in rows:
        try:
            data = json.loads(value_json)
        except:
            continue
        rate = data.get('success_rate', 0)
        total = data.get('total_repairs', 0)
        print(f'    {data.get("item_type", "?"):30s}  {rate:.1%} success  ({total} repairs)')

    conn.close()


if __name__ == '__main__':
    run()
