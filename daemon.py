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
from shared.db import init_db
from shared.persist import log_run

BASE_DIR = Path(__file__).parent

# Source configurations: name, script path, cadence_seconds, enabled
SOURCES = [
    {
        'id': 'cex',
        'script': 'collectors/cex_collector.py',
        'cadence': 3600 * 6,   # every 6 hours
        'enabled': True,
        'args': [],
    },
    {
        'id': 'open_repair',
        'script': 'collectors/open_repair_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
        'args': [],
    },
    {
        'id': 'robotshop_uk',
        'script': 'collectors/robotshop_collector.py',
        'cadence': 3600 * 12,  # every 12 hours
        'enabled': True,
        'args': [],
    },
    {
        'id': 'trade_pricing',
        'script': 'collectors/trade_collector.py',
        'cadence': 3600 * 12,  # every 12 hours
        'enabled': True,
        'args': [],
    },
    {
        'id': 'partsdb',
        'script': 'collectors/partsdb_collector.py',
        'cadence': 3600 * 24,  # daily
        'enabled': bool(os.environ.get('PARTSDB_API_KEY')),
        'args': [],
    },
    {
        'id': 'opss_recalls',
        'script': 'collectors/opss_historical.py',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
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

    started_at = datetime.now(timezone.utc).isoformat()
    print(f"  [{source_id}] Starting collection...")

    try:
        result = subprocess.run(
            [sys.executable, str(script)] + source.get('args', []),
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(BASE_DIR),
        )

        finished_at = datetime.now(timezone.utc).isoformat()

        if result.returncode == 0:
            log_run(source_id, 'ok', started_at=started_at, finished_at=finished_at)
            print(f"  [{source_id}] OK")
            return True
        else:
            error = result.stderr[:500] if result.stderr else 'unknown error'
            log_run(source_id, 'error', error=error, started_at=started_at, finished_at=finished_at)
            print(f"  [{source_id}] ERROR: {error[:100]}")
            return False

    except subprocess.TimeoutExpired:
        finished_at = datetime.now(timezone.utc).isoformat()
        log_run(source_id, 'error', error='timeout after 600s',
                started_at=started_at, finished_at=finished_at)
        print(f"  [{source_id}] TIMEOUT")
        return False
    except Exception as e:
        finished_at = datetime.now(timezone.utc).isoformat()
        log_run(source_id, 'error', error=str(e)[:500],
                started_at=started_at, finished_at=finished_at)
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
