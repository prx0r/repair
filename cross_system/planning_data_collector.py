"""Planning Data Collector — fetches UK planning applications."""

import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'planning'
API_BASE = 'https://www.planning.data.gov.uk/api/v1'

SEARCH_TERMS = [
    'solar panel',
    'heat pump',
    'ev charger',
    'electric vehicle charging',
    'battery storage',
    'electrical repair',
    'workshop',
]


def search_planning(query, limit=100):
    items = []
    try:
        resp = requests.get(f'{API_BASE}/search', params={'q': query, 'limit': limit}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data if isinstance(data, list) else data.get('results', [])
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
    print("Planning Data Collector")
    print("=" * 40)
    total = 0
    for q in SEARCH_TERMS:
        print(f"  {q}...", end=' ')
        items = search_planning(q)
        n = save(items, q)
        total += n
        print(f"{n} applications")
        time.sleep(1)
    print(f"Done. {total} total. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
