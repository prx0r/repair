"""Electricians Vertical — end-to-end test case.

Manchester × Electrical Installation × 2026-09-21

Should return:
  - current registered capacity
  - company capacity
  - sole-trader estimate
  - employment estimate
  - training providers
  - apprenticeship starts
  - expected completions
  - vacancy demand
  - procurement demand
  - policy events
  - historical deltas
  - provenance for every number
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path('/home/ubuntu/warehouse/repair.db')

# Manchester test parameters
TEST_GEO = "LAD:E08000003"
TEST_GEO_NAME = "Manchester"
TEST_CAPABILITY = "electrical_domestic_installation"
TEST_DATE = "2026-09-21"


def get_manchester_electricians(conn):
    """Query all data about Manchester electricians."""
    result = {
        'geography': TEST_GEO_NAME,
        'capability': 'electrical_domestic_installation',
        'date': TEST_DATE,
        'layers': {},
    }

    # Layer 1: Companies House — active companies with relevant SICs
    sic_codes = ['43210', '43220', '43310', '43320', '43999']
    for sic in sic_codes:
        rows = conn.execute(
            "SELECT entity_id, value FROM observations "
            "WHERE source_id='companies_house' AND metric='company_search' "
            "AND value LIKE ?", (f'%{sic}%',)
        ).fetchall()
        for row in rows:
            data = json.loads(row[1])
            if 'electrical' in data.get('name', '').lower() or 'electric' in data.get('name', '').lower():
                result['layers'].setdefault('companies', []).append({
                    'company_number': row[0],
                    'name': data.get('name'),
                    'sic': sic,
                })

    # Layer 2: Open Repair — electrical repair records
    rows = conn.execute(
        "SELECT value FROM observations "
        "WHERE source_id='open_repair' AND metric='repair_record' "
        "AND value LIKE '%electrical%' LIMIT 100"
    ).fetchall()
    for row in rows:
        data = json.loads(row[0])
        result['layers'].setdefault('repair_records', []).append({
            'item_type': data.get('item_type'),
            'fault': data.get('fault_type'),
            'outcome': data.get('repair_outcome'),
            'brand': data.get('brand'),
        })

    # Layer 3: Planning Data — electrical installations in Manchester area
    rows = conn.execute(
        "SELECT entity_id, value FROM observations "
        "WHERE source_id='planning_data' AND metric='application' "
        "AND value LIKE '%Manchester%' LIMIT 20"
    ).fetchall()
    for row in rows:
        data = json.loads(row[1])
        result['layers'].setdefault('planning', []).append({
            'reference': row[0],
            'description': data.get('description', '')[:100],
        })

    # Layer 4: OpenAlex — research on electrical repair
    rows = conn.execute(
        "SELECT value FROM observations "
        "WHERE source_id='openalex' AND metric='research_paper' "
        "AND (value LIKE '%electrical%' OR value LIKE '%repair%') LIMIT 10"
    ).fetchall()
    for row in rows:
        data = json.loads(row[0])
        result['layers'].setdefault('research', []).append({
            'title': data.get('title'),
            'cited_by': data.get('cited_by'),
            'year': data.get('year'),
        })

    return result


def run():
    print(f'Electricians Vertical Test')
    print(f'Geography: {TEST_GEO_NAME}')
    print(f'Capability: {TEST_CAPABILITY}')
    print(f'Date: {TEST_DATE}')
    print('=' * 60)

    if not DB.exists():
        print(f'Database not found: {DB}')
        return

    conn = sqlite3.connect(str(DB))
    result = get_manchester_electricians(conn)

    # Print layers
    for layer_name, layer_data in result['layers'].items():
        print(f'\n{layer_name.upper()} ({len(layer_data)} records):')
        for item in layer_data[:5]:
            for k, v in item.items():
                if v:
                    print(f'  {k}: {v}')
            print()

    # Summary
    total = sum(len(v) for v in result['layers'].values())
    print(f'\nTotal records across all layers: {total}')
    print(f'Layers populated: {list(result["layers"].keys())}')

    conn.close()


if __name__ == '__main__':
    run()
