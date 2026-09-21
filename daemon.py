"""Repair Garden — Always-On Collector Daemon.

Runs all collectors on a schedule. Each source has its own cadence.
Logs everything to SQLite. Supports graceful shutdown.

Usage:
    python daemon.py                # run once
    python daemon.py --loop         # run on schedule
    python daemon.py --loop --interval 3600  # custom interval
"""

import os
import sys
import time
import signal
import json
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from storage import init_db, start_collection_run, finish_collection_run, insert_observations_batch

BASE_DIR = Path(__file__).parent

# Source configurations: name, script path, cadence_seconds, enabled
SOURCES = [
    {
        'id': 'ebay_uk',
        'script': 'collectors/ebay_uk_collector.py',
        'cadence': 3600 * 6,   # every 6 hours
        'enabled': True,
        'args': ['--count', '50'],
    },
    {
        'id': 'open_repair',
        'script': 'collectors/open_repair_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
        'args': [],
    },
    {
        'id': 'france_repairability',
        'script': 'collectors/france_repairability_collector.py',
        'cadence': 3600 * 24 * 7,  # weekly
        'enabled': True,
        'args': [],
    },
    {
        'id': 'eprel',
        'script': 'collectors/eprel_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
        'args': [],
    },
    {
        'id': 'planning_data',
        'script': 'collectors/planning_data_collector.py',
        'cadence': 3600 * 12,  # every 12 hours
        'enabled': True,
        'args': [],
    },
    {
        'id': 'land_registry',
        'script': 'collectors/land_registry_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
        'args': [],
    },
    {
        'id': 'companies_house',
        'script': 'collectors/companies_house_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': bool(os.environ.get('COMPANIES_HOUSE_API_KEY')),
        'args': [],
    },
    {
        'id': 'dvla',
        'script': 'collectors/dvla_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
        'args': [],
    },
    {
        'id': 'electricity_maps',
        'script': 'collectors/electricity_maps_collector.py',
        'cadence': 3600,  # hourly
        'enabled': bool(os.environ.get('ELECTRICITY_MAPS_TOKEN')),
        'args': [],
    },
]

# Track last run times
last_runs = {}

RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    print(f"\nReceived signal {sig}, shutting down...")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def run_collector(source):
    """Run a single collector and log to SQLite."""
    source_id = source['id']
    script = BASE_DIR / source['script']

    if not script.exists():
        print(f"  [{source_id}] Script not found: {script}")
        return False

    run_id = start_collection_run(source_id)
    print(f"  [{source_id}] Starting collection run #{run_id}...")

    try:
        result = subprocess.run(
            [sys.executable, str(script)] + source.get('args', []),
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(BASE_DIR),
        )

        if result.returncode == 0:
            # Try to count rows from output
            rows = 0
            for line in result.stdout.split('\n'):
                if 'items' in line or 'products' in line or 'companies' in line:
                    parts = line.strip().split()
                    for p in parts:
                        try:
                            rows = int(p)
                        except ValueError:
                            continue

            finish_collection_run(run_id, rows_collected=rows, rows_inserted=rows, status='ok')
            print(f"  [{source_id}] OK ({rows} rows)")
            return True
        else:
            error = result.stderr[:500] if result.stderr else 'unknown error'
            finish_collection_run(run_id, status='error', error=error)
            print(f"  [{source_id}] ERROR: {error[:100]}")
            return False

    except subprocess.TimeoutExpired:
        finish_collection_run(run_id, status='timeout', error='timeout after 600s')
        print(f"  [{source_id}] TIMEOUT")
        return False
    except Exception as e:
        finish_collection_run(run_id, status='error', error=str(e)[:500])
        print(f"  [{source_id}] EXCEPTION: {e}")
        return False


def should_run(source):
    """Check if a source is due for collection."""
    source_id = source['id']
    if not source.get('enabled', True):
        return False

    last = last_runs.get(source_id, 0)
    now = time.time()
    return (now - last) >= source.get('cadence', 3600)


def run_once():
    """Run all due collectors once."""
    print(f"\n{'='*60}")
    print(f"  Repair Garden Collector — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")

    results = {}
    for source in SOURCES:
        if should_run(source):
            ok = run_collector(source)
            results[source['id']] = ok
            last_runs[source['id']] = time.time()
            time.sleep(2)  # rate limit between sources

    enabled = [s for s in SOURCES if s.get('enabled', True)]
    skipped = [s['id'] for s in SOURCES if not should_run(s) and s.get('enabled', True)]
    disabled = [s['id'] for s in SOURCES if not s.get('enabled', True)]

    print(f"\n  Results: {sum(results.values())}/{len(results)} OK")
    if skipped:
        print(f"  Skipped (not due): {', '.join(skipped)}")
    if disabled:
        print(f"  Disabled (needs API key): {', '.join(disabled)}")

    return results


def loop(interval=3600):
    """Run collectors on a loop."""
    print(f"Repair Garden Daemon — interval {interval}s")
    print(f"Sources: {len(SOURCES)} total, {sum(1 for s in SOURCES if s.get('enabled'))} enabled")

    while RUNNING:
        run_once()
        if not RUNNING:
            break
        print(f"\n  Next cycle in {interval}s...")
        # Sleep in small increments so we can respond to signals
        for _ in range(interval):
            if not RUNNING:
                break
            time.sleep(1)

    print("Daemon stopped.")


def main():
    parser = argparse.ArgumentParser(description='Repair Garden Collector Daemon')
    parser.add_argument('--loop', action='store_true', help='Run on schedule')
    parser.add_argument('--interval', type=int, default=3600, help='Loop interval in seconds')
    parser.add_argument('--init-db', action='store_true', help='Initialize database only')
    args = parser.parse_args()

    init_db()

    if args.init_db:
        return

    if args.loop:
        loop(args.interval)
    else:
        run_once()


if __name__ == '__main__':
    main()
