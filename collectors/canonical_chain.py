"""Canonical Chain — builds the DEVICE→FAULT→PART→VALUE graph from collected data.

Reads from source_record and produces derived facts in the derived_fact table.
Layer 2: analysis pipeline, consumes Layer 1 data.

- device_value_curves: price by condition over time
- repair_opportunities: broken→repaired spread
"""

import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from shared.persist import get_db


def compute_value_curves(conn):
    """Compute price distributions by device × condition from market data."""
    rows = conn.execute("""
        SELECT source_native_id, normalized_json FROM source_record
        WHERE source_id = 'ebay_3market' AND valid = 1
    """).fetchall()

    devices = {}
    for native_id, normalized_json in rows:
        try:
            data = json.loads(normalized_json)
        except:
            continue

        domain = data.get('domain', 'unknown')
        model = data.get('model', 'unknown')
        condition = data.get('condition', 'working')
        price = data.get('price')
        if price is None:
            continue

        key = f"{domain}:{model}"
        if key not in devices:
            devices[key] = {'broken': [], 'working': [], 'parts': []}

        if condition in devices[key]:
            devices[key][condition].append(float(price))

    count = 0
    for device_key, prices in devices.items():
        curve = {}
        for cond, price_list in prices.items():
            if price_list:
                price_list.sort()
                n = len(price_list)
                curve[cond] = {
                    'count': n,
                    'min': min(price_list),
                    'max': max(price_list),
                    'median': price_list[n // 2],
                    'p10': price_list[max(0, n // 10)],
                    'p90': price_list[min(n - 1, n * 9 // 10)],
                }

        if curve.get('broken', {}).get('count', 0) > 0 and curve.get('working', {}).get('count', 0) > 0:
            broken_med = curve['broken']['median']
            working_med = curve['working']['median']
            curve['repair_spread'] = working_med - broken_med
            curve['repair_spread_pct'] = ((working_med - broken_med) / broken_med * 100) if broken_med > 0 else 0

        derived_id = hashlib.sha256(
            json.dumps({"kind": "value_curve", "subject": device_key}, sort_keys=True).encode()
        ).hexdigest()

        conn.execute(
            "INSERT OR REPLACE INTO derived_fact "
            "(derived_id, source_id, entity_id, metric, value, method_id, method_version, "
            "input_observation_ids, computed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (derived_id, 'canonical_chain', device_key, 'value_curve',
             json.dumps(curve, default=str), 'value_curve', 'v1',
             '[]', datetime.now(timezone.utc).isoformat())
        )
        count += 1

    conn.commit()
    return count


def compute_repair_opportunities(conn):
    """Find devices with profitable repair spread."""
    rows = conn.execute("""
        SELECT entity_id, value FROM derived_fact
        WHERE metric = 'value_curve'
    """).fetchall()

    count = 0
    for device_key, value_json in rows:
        try:
            data = json.loads(value_json)
        except:
            continue

        if 'repair_spread' not in data:
            continue

        spread = data['repair_spread']
        broken_med = data.get('broken', {}).get('median', 0)
        working_med = data.get('working', {}).get('median', 0)

        opportunity = {
            'device': device_key,
            'broken_cost': broken_med,
            'working_value': working_med,
            'gross_spread': spread,
            'spread_pct': data.get('repair_spread_pct', 0),
            'broken_count': data.get('broken', {}).get('count', 0),
            'working_count': data.get('working', {}).get('count', 0),
        }

        derived_id = hashlib.sha256(
            json.dumps({"kind": "repair_opportunity", "subject": device_key}, sort_keys=True).encode()
        ).hexdigest()

        conn.execute(
            "INSERT OR REPLACE INTO derived_fact "
            "(derived_id, source_id, entity_id, metric, value, method_id, method_version, "
            "input_observation_ids, computed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (derived_id, 'canonical_chain', device_key, 'repair_opportunity',
             json.dumps(opportunity, default=str), 'repair_opportunity', 'v1',
             '[]', datetime.now(timezone.utc).isoformat())
        )
        count += 1

    conn.commit()
    return count


def run():
    print('Canonical Chain Builder')
    print('=' * 40)

    conn = get_db()

    print('  Computing value curves...')
    n_curves = compute_value_curves(conn)
    print(f'    {n_curves} device value curves')

    print('  Computing repair opportunities...')
    n_opps = compute_repair_opportunities(conn)
    print(f'    {n_opps} repair opportunities found')

    print('\n  Top repair opportunities:')
    rows = conn.execute("""
        SELECT entity_id, value FROM derived_fact
        WHERE metric = 'repair_opportunity'
        ORDER BY computed_at DESC LIMIT 10
    """).fetchall()

    for device_key, value_json in rows:
        try:
            data = json.loads(value_json)
        except:
            continue
        spread = data.get('gross_spread', 0)
        pct = data.get('spread_pct', 0)
        print(f'    {data.get("device", "?"):40s}  £{spread:>8.2f}  ({pct:>6.1f}%)')

    conn.close()


if __name__ == '__main__':
    run()
