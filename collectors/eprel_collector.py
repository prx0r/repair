"""EPREL Collector — fetches EU energy efficiency product data."""

import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'eprel'
API_BASE = 'https://eprel.ec.europa.eu/api'

CATEGORIES = [
    'solar-photovoltaic',
    'electrical-storage',
    'heat-pumps',
    'led',
]


def collect_category(category):
    items = []
    try:
        resp = requests.get(f'{API_BASE}/products', params={'category': category, 'limit': 200}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data if isinstance(data, list) else data.get('results', [])
    except Exception as e:
        print(f"  Error: {e}")
    return items


def save(data, category):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}_{category.replace('/', '_')}.jsonl"
    count = 0
    with open(filepath, 'w') as f:
        for record in data:
            record['collected_at'] = datetime.now().isoformat()
            record['source'] = 'eprel'
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("EPREL Collector")
    print("=" * 40)
    total = 0
    for cat in CATEGORIES:
        print(f"  {cat}...", end=' ')
        items = collect_category(cat)
        n = save(items, cat)
        total += n
        print(f"{n} products")
        time.sleep(1)
    print(f"Done. {total} total. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
