"""UK Companies House Collector — fetches company data for repair businesses."""

import json
import os
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'companies'
API_BASE = 'https://api.company-information.service.gov.uk'
API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY', '')

SEARCH_QUERIES = [
    'electronics repair',
    'phone repair',
    'laptop repair',
    'computer repair',
    'solar panel installation',
    'electrical contractor',
    'robot',
    'drone',
    'battery',
    '3d printing',
]


def search_companies(query, limit=50):
    if not API_KEY:
        print("  Set COMPANIES_HOUSE_API_KEY in .env")
        return []
    items = []
    try:
        resp = requests.get(f'{API_BASE}/search/companies', params={'q': query, 'items_per_page': limit},
                            auth=(API_KEY, ''), timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
    except Exception as e:
        print(f"  Error: {e}")
    return items


def save(data, query):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"
    count = 0
    with open(filepath, 'a') as f:
        for record in data:
            record['collected_at'] = datetime.now().isoformat()
            record['search_query'] = query
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("UK Companies House Collector")
    print("=" * 40)
    total = 0
    for q in SEARCH_QUERIES:
        print(f"  {q}...", end=' ')
        items = search_companies(q)
        n = save(items, q)
        total += n
        print(f"{n} companies")
        time.sleep(1)
    print(f"Done. {total} total. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
