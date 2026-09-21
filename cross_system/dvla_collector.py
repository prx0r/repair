"""DVLA/DVSA Collector — fetches UK vehicle tax and MOT data."""

import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'hardware' / 'vehicles'
MOT_API = 'https://www.check-mot.service.gov.uk/trade/vehicles/mot-tests'


def check_mot(registration):
    """Check MOT status for a vehicle registration."""
    try:
        resp = requests.get(MOT_API, params={'registration': registration}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def collect_sample_fleet():
    """Collect MOT data for a sample of common vehicle registrations.
    
    In production, this would ingest from DVLA bulk data or RDE/ANPR feeds.
    """
    sample_registrations = [
        'AB12CDE', 'WX52ABC', 'LN62XYZ', 'BV19HMN', 'SK63EFG',
    ]
    results = []
    for reg in sample_registrations:
        data = check_mot(reg)
        if data:
            data['registration'] = reg
            data['collected_at'] = datetime.now().isoformat()
            results.append(data)
        time.sleep(0.5)
    return results


def save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"
    count = 0
    with open(filepath, 'w') as f:
        for record in data:
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def main():
    print("DVLA/DVSA MOT Collector")
    print("=" * 40)
    print("  Collecting sample fleet...", end=' ')
    items = collect_sample_fleet()
    n = save(items)
    print(f"{n} vehicles")
    print(f"Done. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
