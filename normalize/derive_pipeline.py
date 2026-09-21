"""Derive Pipeline — raw observations → DerivedFacts → EconomicEvents.

Runs transformations on the observations table to produce higher-level insights.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DB = Path('/home/ubuntu/warehouse/repair.db')


def derive_repair_success_rates(conn):
    """Compute repair success rates from Open Repair data."""
    rows = conn.execute("""
        SELECT value FROM observations
        WHERE source_id='open_repair' AND metric='repair_record'
    """).fetchall()

    outcomes = {}
    for row in rows:
        data = json.loads(row[0])
        item_type = data.get('product_category', data.get('item_type', 'unknown'))
        outcome = data.get('repair_status', data.get('repair_outcome', 'unknown'))

        if item_type not in outcomes:
            outcomes[item_type] = {'fixed': 0, 'not_fixed': 0, 'partly_fixed': 0, 'end_of_life': 0, 'total': 0}

        outcomes[item_type]['total'] += 1
        if outcome in ('Fixed', 'Repaired'):
            outcomes[item_type]['fixed'] += 1
        elif outcome in ('Not fixed', 'Not repairable'):
            outcomes[item_type]['not_fixed'] += 1
        elif outcome in ('Partly fixed', 'Repairable'):
            outcomes[item_type]['partly_fixed'] += 1
        elif outcome == 'End of life':
            outcomes[item_type]['end_of_life'] += 1

    count = 0
    for item_type, counts in outcomes.items():
        if counts['total'] < 10:  # skip thin data
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
        conn.execute(
            "INSERT OR REPLACE INTO observations "
            "(source_id, entity_id, metric, value, value_type, raw_json, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('derive_pipeline', f'repair_success:{item_type}', 'derived_fact',
             json.dumps(derived, default=str), 'json',
             json.dumps(derived, default=str), datetime.now().isoformat())
        )
        count += 1

    conn.commit()
    return count


def derive_failure_distribution(conn):
    """Compute fault distribution from Open Repair data."""
    rows = conn.execute("""
        SELECT value FROM observations
        WHERE source_id='open_repair' AND metric='repair_record'
    """).fetchall()

    faults = {}
    for row in rows:
        data = json.loads(row[0])
        item_type = data.get('product_category', data.get('item_type', 'unknown'))
        fault = data.get('problem', data.get('fault_type', 'unknown'))[:80]

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
        conn.execute(
            "INSERT OR REPLACE INTO observations "
            "(source_id, entity_id, metric, value, value_type, raw_json, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('derive_pipeline', f'fault_dist:{item_type}', 'derived_fact',
             json.dumps(derived, default=str), 'json',
             json.dumps(derived, default=str), datetime.now().isoformat())
        )
        count += 1

    conn.commit()
    return count


def derive_companies_by_capability(conn):
    """Map Companies House companies to capabilities via SIC codes."""
    from resolve.sic_capability import sic_to_capabilities, SIC_DESCRIPTIONS

    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id='companies_house' AND metric='company_profile'
    """).fetchall()

    count = 0
    for row in rows:
        data = json.loads(row[1])
        company_number = row[0]
        name = data.get('name', '')
        sic_codes = data.get('sic', [])

        if not sic_codes:
            continue

        capabilities = sic_to_capabilities(sic_codes)
        if not capabilities:
            continue

        derived = {
            'company_number': company_number,
            'name': name,
            'sic_codes': sic_codes,
            'capabilities': capabilities,
            'sic_descriptions': [SIC_DESCRIPTIONS.get(s, s) for s in sic_codes],
        }
        conn.execute(
            "INSERT OR REPLACE INTO observations "
            "(source_id, entity_id, metric, value, value_type, raw_json, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('derive_pipeline', f'company_capability:{company_number}', 'derived_fact',
             json.dumps(derived, default=str), 'json',
             json.dumps(derived, default=str), datetime.now().isoformat())
        )
        count += 1

    conn.commit()
    return count


def run():
    print('Derive Pipeline')
    print('=' * 40)

    conn = sqlite3.connect(str(DB))

    print('  Computing repair success rates...')
    n = derive_repair_success_rates(conn)
    print(f'    {n} item types with success rates')

    print('  Computing failure distributions...')
    n = derive_failure_distribution(conn)
    print(f'    {n} item types with fault distributions')

    print('  Mapping companies to capabilities...')
    n = derive_companies_by_capability(conn)
    print(f'    {n} companies mapped to capabilities')

    # Show derived facts
    print('\n  Repair success rates (top 10):')
    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id='derive_pipeline' AND metric='derived_fact'
        AND entity_id LIKE 'repair_success:%'
        ORDER BY CAST(value AS TEXT) DESC LIMIT 10
    """).fetchall()
    for row in rows:
        data = json.loads(row[1])
        rate = data.get('success_rate', 0)
        total = data.get('total_repairs', 0)
        print(f'    {data.get("item_type", "?"):30s}  {rate:.1%} success  ({total} repairs)')

    print('\n  Companies mapped to capabilities (top 10):')
    rows = conn.execute("""
        SELECT entity_id, value FROM observations
        WHERE source_id='derive_pipeline' AND metric='derived_fact'
        AND entity_id LIKE 'company_capability:%'
        LIMIT 10
    """).fetchall()
    for row in rows:
        data = json.loads(row[1])
        caps = data.get('capabilities', [])
        print(f'    {data.get("name", "?"):40s}  → {", ".join(caps[:3])}')

    conn.close()


if __name__ == '__main__':
    run()
