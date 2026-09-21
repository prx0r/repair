"""Master Collector — runs all data sources.

Usage:
    python collect.py              # run all sources
    python collect.py --source ebay  # run specific source
    python collect.py --daemon      # run in daemon mode (hourly)
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

COLLECTORS = {
    'ebay': 'collectors/ebay_uk_collector.py',
    'open_repair': 'collectors/open_repair_collector.py',
    'france': 'collectors/france_repairability_collector.py',
    'eprel': 'collectors/eprel_collector.py',
    'companies': 'collectors/companies_house_collector.py',
    'land_registry': 'collectors/land_registry_collector.py',
    'dvla': 'collectors/dvla_collector.py',
    'planning': 'collectors/planning_data_collector.py',
    'electricity': 'collectors/electricity_maps_collector.py',
}

# eBay is already working (free, no API key). Others need keys/setup.
PRIORITY_ORDER = ['ebay', 'open_repair', 'france', 'eprel', 'planning',
                  'land_registry', 'companies', 'dvla', 'electricity']


def run_collector(name, script):
    print(f"\n{'='*50}")
    print(f"  Running: {name}")
    print(f"{'='*50}")
    try:
        result = subprocess.run([sys.executable, script], capture_output=False, timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {name}")
        return False
    except Exception as e:
        print(f"  ERROR: {name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, help='Run specific source')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode')
    parser.add_argument('--interval', type=int, default=3600, help='Daemon interval (seconds)')
    args = parser.parse_args()

    base = Path(__file__).parent

    if args.source:
        if args.source in COLLECTORS:
            run_collector(args.source, str(base / COLLECTORS[args.source]))
        else:
            print(f"Unknown source: {args.source}. Available: {list(COLLECTORS.keys())}")
        return

    print("Repair Garden — Master Collector")
    print(f"Sources: {len(COLLECTORS)}")

    while True:
        results = {}
        for name in PRIORITY_ORDER:
            script = COLLECTORS[name]
            success = run_collector(name, str(base / script))
            results[name] = success

        print(f"\n{'='*50}")
        print("  Results:")
        for name, ok in results.items():
            print(f"    {'✓' if ok else '✗'} {name}")

        if not args.daemon:
            break

        print(f"\n  Next run in {args.interval}s...")
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
