"""Canonical Chain — builds the DEVICE→FAULT→PART→VALUE graph from collected data.

Reads from SQLite observations and produces derived facts:
- device_value_curves: price by condition over time
- repair_opportunities: broken→repaired spread
- part_scarcity_signals: MPN availability across distributors
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).parent.parent / 'warehouse' / 'repair.db'


def compute_value_curves(conn):
    """Compute price distributions by device × condition from eBay data."""
    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id = 'ebay_3market' AND metric = 'listing'
    """).fetchall()

    devices = {}
    for row in rows:
        data = json.loads(row[1])
        domain = data.get('domain', 'unknown')
        search = data.get('search', 'unknown')
        condition = data.get('condition', 'working')
        price = data.get('price', 0)

        key = f"{domain}:{search}"
        if key not in devices:
            devices[key] = {'broken': [], 'working': [], 'parts': []}

        if condition in devices[key]:
            devices[key][condition].append(price)

    # Store derived value curves
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

        # Calculate repair spread if we have broken + working
        if curve.get('broken', {}).get('count', 0) > 0 and curve.get('working', {}).get('count', 0) > 0:
            broken_med = curve['broken']['median']
            working_med = curve['working']['median']
            curve['repair_spread'] = working_med - broken_med
            curve['repair_spread_pct'] = ((working_med - broken_med) / broken_med * 100) if broken_med > 0 else 0

        conn.execute(
            'INSERT OR REPLACE INTO observations '
            '(source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('canonical_chain', device_key, 'value_curve',
             json.dumps(curve, default=str), 'json',
             json.dumps(curve, default=str), datetime.now().isoformat())
        )
        count += 1

    conn.commit()
    return count


def compute_repair_opportunities(conn):
    """Find devices with profitable repair spread."""
    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id = 'canonical_chain' AND metric = 'value_curve'
    """).fetchall()

    count = 0
    for row in rows:
        data = json.loads(row[1])
        if 'repair_spread' not in data:
            continue

        device = row[0]
        spread = data['repair_spread']
        broken_med = data.get('broken', {}).get('median', 0)
        working_med = data.get('working', {}).get('median', 0)

        opportunity = {
            'device': device,
            'broken_cost': broken_med,
            'working_value': working_med,
            'gross_spread': spread,
            'spread_pct': data.get('repair_spread_pct', 0),
            'broken_count': data.get('broken', {}).get('count', 0),
            'working_count': data.get('working', {}).get('count', 0),
        }

        conn.execute(
            'INSERT OR REPLACE INTO observations '
            '(source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('canonical_chain', device, 'repair_opportunity',
             json.dumps(opportunity, default=str), 'json',
             json.dumps(opportunity, default=str), datetime.now().isoformat())
        )
        count += 1

    conn.commit()
    return count


def run():
    print('Canonical Chain Builder')
    print('=' * 40)

    conn = sqlite3.connect(str(DB))

    print('  Computing value curves...')
    n_curves = compute_value_curves(conn)
    print(f'    {n_curves} device value curves')

    print('  Computing repair opportunities...')
    n_opps = compute_repair_opportunities(conn)
    print(f'    {n_opps} repair opportunities found')

    # Show top opportunities
    print('\n  Top repair opportunities:')
    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id = 'canonical_chain' AND metric = 'repair_opportunity'
        ORDER BY CAST(value AS REAL) DESC LIMIT 10
    """).fetchall()

    for row in rows:
        data = json.loads(row[1])
        spread = data.get('gross_spread', 0)
        pct = data.get('spread_pct', 0)
        print(f'    {data.get("device", "?"):40s}  £{spread:>8.2f}  ({pct:>6.1f}%)')

    conn.close()


if __name__ == '__main__':
    run()
