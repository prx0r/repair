"""Land Registry PPD Collector — downloads UK property transaction data."""

import json
import csv
import io
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'property'
API_URL = 'https://landregistry.data.gov.uk/data/ppi/transaction-record'


def collect_ppd(limit=500):
    """Collect recent property transactions from Land Registry."""
    items = []
    params = {'_view': 'ppi', '_pageSize': min(limit, 5000)}
    try:
        resp = requests.get(API_URL, params=params, headers={'Accept': 'application/json'}, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"  Error: {e}")
    return items


def save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"
    count = 0
    with open(filepath, 'w') as f:
        for record in data:
            record['collected_at'] = datetime.now().isoformat()
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("Land Registry PPD Collector")
    print("=" * 40)
    print("  Collecting transactions...", end=' ')
    items = collect_ppd()
    n = save(items)
    print(f"{n} transactions")
    print(f"Done. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
