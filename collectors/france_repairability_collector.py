"""France Repairability Index Collector — fetches French government repair scores."""

import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'repair_db' / 'france_index'
API_BASE = 'https://app.rfrindustries.com/api/v2'

CATEGORIES = {
    'smartphones': 'smartphone',
    'laptops': 'ordinateur-portable',
    'televisions': 'television',
    'washing_machines': 'lave-linge',
    'mowers': 'tondeuse',
}


def collect_category(category_slug):
    items = []
    try:
        resp = requests.get(f'{API_BASE}/products', params={'category': category_slug, 'limit': 500}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data if isinstance(data, list) else data.get('results', [])
    except Exception as e:
        print(f"  Error: {e}")
    return items


def save(data, category):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}_{category}.jsonl"
    count = 0
    with open(filepath, 'w') as f:
        for record in data:
            record['collected_at'] = datetime.now().isoformat()
            record['source'] = 'france_repairability_index'
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("France Repairability Index Collector")
    print("=" * 40)
    total = 0
    for name, slug in CATEGORIES.items():
        print(f"  {name}...", end=' ')
        items = collect_category(slug)
        n = save(items, name)
        total += n
        print(f"{n} products")
        time.sleep(1)
    print(f"Done. {total} total products. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
