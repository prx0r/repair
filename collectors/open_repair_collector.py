"""Open Repair Alliance Collector — fetches repair data from community repair cafés."""

import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'repair_db' / 'open_repair'
API_BASE = 'https://openrepairdata.org/api/v1'


def collect_items(limit=500):
    items = []
    offset = 0
    while offset < limit:
        try:
            resp = requests.get(f'{API_BASE}/items', params={'limit': 100, 'offset': offset}, timeout=30)
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}")
                break
            data = resp.json()
            if not data:
                break
            items.extend(data)
            offset += 100
            time.sleep(1)
        except Exception as e:
            print(f"  Error at offset {offset}: {e}")
            break
    return items


def collect_repairs(limit=500):
    repairs = []
    offset = 0
    while offset < limit:
        try:
            resp = requests.get(f'{API_BASE}/repairs', params={'limit': 100, 'offset': offset}, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            if not data:
                break
            repairs.extend(data)
            offset += 100
            time.sleep(1)
        except Exception as e:
            print(f"  Error: {e}")
            break
    return repairs


def save(data, name):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}_{name}.jsonl"
    count = 0
    with open(filepath, 'w') as f:
        for record in data:
            record['collected_at'] = datetime.now().isoformat()
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("Open Repair Alliance Collector")
    print("=" * 40)
    print("  Collecting items...", end=' ')
    items = collect_items()
    n = save(items, 'items')
    print(f"{n} items")
    print("  Collecting repairs...", end=' ')
    repairs = collect_repairs()
    n = save(repairs, 'repairs')
    print(f"{n} repairs")
    print(f"Done. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
