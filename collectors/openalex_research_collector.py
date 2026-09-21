"""OpenAlex Research Collector — repair/sustainability/circular economy papers.

Fetches latest research that maps the repair knowledge frontier.
"""

import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

DB = Path(__file__).parent.parent / 'warehouse' / 'repair.db'

QUERIES = [
    'electronics repair sustainability',
    'circular economy electronics',
    'right to repair',
    'component obsolescence',
    'product repairability',
    'refurbishment electronics',
    'e-waste recycling recovery',
    'spare parts availability',
    'modular design repair',
    'semiconductor supply chain',
    'gpu mining hardware lifecycle',
    'robot maintenance lifecycle',
]


def fetch_openalex(search_query, per_page=10):
    """Fetch papers from OpenAlex."""
    try:
        resp = requests.get('https://api.openalex.org/works', params={
            'search': search_query,
            'per_page': per_page,
            'sort': 'cited_by_count:desc',
        }, timeout=15)
        if resp.status_code == 200:
            return resp.json().get('results', [])
    except:
        pass
    return []


def run():
    print('OpenAlex Research Collector')
    print(f'Queries: {len(QUERIES)}')
    print('=' * 40)

    conn = sqlite3.connect(str(DB))
    total = 0

    for q in QUERIES:
        print(f'  [{q}]...', end=' ')
        papers = fetch_openalex(q, per_page=10)
        count = 0
        for p in papers:
            topics = [t.get('display_name', '') for t in p.get('topics', [])[:5]]
            store_obs(conn, 'openalex', p.get('id', ''), 'research_paper',
                {'title': p.get('title'), 'cited_by': p.get('cited_by_count'),
                 'year': p.get('publication_year'), 'topics': topics,
                 'doi': p.get('doi'), 'query': q}, p)
            count += 1
        total += count
        print(f'{count} papers')
        conn.commit()

    print(f'\nTotal: {total} papers')
    conn.close()


def store_obs(conn, source, entity, metric, value_dict, raw=None):
    try:
        conn.execute(
            'INSERT OR IGNORE INTO observations '
            '(source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (source, entity, metric, json.dumps(value_dict, default=str),
             'json', json.dumps(raw or value_dict, default=str), datetime.now().isoformat())
        )
        return True
    except:
        return False


if __name__ == '__main__':
    run()
