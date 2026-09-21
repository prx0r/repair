"""Electricity Maps Collector — fetches real-time electricity pricing."""

import json
import os
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'energy'
API_BASE = 'https://api.electricitymap.org/v3'
API_TOKEN = os.environ.get('ELECTRICITY_MAPS_TOKEN', '')

ZONES = ['GB', 'DE', 'FR', 'NL', 'BE', 'ES', 'IT', 'PL', 'SE', 'NO']


def collect_zone(zone):
    if not API_TOKEN:
        return {'zone': zone, 'error': 'no_api_key'}
    try:
        resp = requests.get(f'{API_BASE}/carbon-intensity/latest',
                            params={'zone': zone},
                            headers={'auth-token': API_TOKEN},
                            timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        return {'zone': zone, 'error': str(e)}
    return {'zone': zone, 'error': f'HTTP {resp.status_code}'}


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
    print("Electricity Maps Collector")
    print("=" * 40)
    results = []
    for zone in ZONES:
        print(f"  {zone}...", end=' ')
        data = collect_zone(zone)
        results.append(data)
        print("ok" if 'error' not in data else data['error'])
        time.sleep(0.5)
    n = save(results)
    print(f"Done. {n} zones. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
