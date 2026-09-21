"""Repair Garden — Always-On Collector Daemon.

Runs all collectors on a schedule. Each source has its own cadence.
Logs everything to SQLite. Supports graceful shutdown.

The daemon ONLY schedules. Collectors own their own collector_run records.
The daemon only logs a run if the process never starts, crashes, or times out.

Usage:
    python3 daemon.py                # run once
    python3 daemon.py --loop         # run on schedule
    python3 daemon.py --status       # show health
    python3 daemon.py --init-db      # initialize database only
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.db import init_db, get_db

BASE_DIR = Path(__file__).parent

# Source configurations: module path, cadence_seconds, enabled
SOURCES = [
    {
        'id': 'cex',
        'module': 'collectors.cex_collector',
        'class': 'CexCollector',
        'cadence': 3600 * 6,   # every 6 hours
        'enabled': True,
    },
    {
        'id': 'open_repair',
        'module': 'collectors.open_repair_collector',
        'class': 'OpenRepairCollector',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
    },
    {
        'id': 'robotshop_uk',
        'module': 'collectors.robotshop_collector',
        'class': 'RobotShopCollector',
        'cadence': 3600 * 12,  # every 12 hours
        'enabled': True,
    },
    {
        'id': 'trade_pricing',
        'module': 'collectors.trade_collector',
        'class': 'ScrewfixToolstationCollector',
        'cadence': 3600 * 12,  # every 12 hours
        'enabled': True,
    },
    {
        'id': 'ebay_3market',
        'module': 'collectors.ebay_3market_collector',
        'class': 'Ebay3MarketCollector',
        'cadence': 3600 * 6,   # every 6 hours
        'enabled': True,
    },
    {
        'id': 'partsdb',
        'module': 'collectors.partsdb_collector',
        'class': 'PartsDBCollector',
        'cadence': 3600 * 24,  # daily
        'enabled': bool(os.environ.get('PARTSDB_API_KEY')),
    },
    {
        'id': 'opss_recalls',
        'module': 'collectors.opss_historical',
        'class': 'OpssCollector',
        'cadence': 3600 * 24,  # daily
        'enabled': True,
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
    """Run a single collector via python -m.

    The collector owns its own collector_run record via BaseCollector.
    The daemon only logs if the process itself fails.
    """
    source_id = source['id']
    module = source['module']

    started_at = datetime.now(timezone.utc).isoformat()
    print(f"  [{source_id}] Starting...")

    try:
        result = subprocess.run(
            [sys.executable, '-m', module],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(BASE_DIR),
        )

        finished_at = datetime.now(timezone.utc).isoformat()

        if result.returncode == 0:
            # Collector ran successfully — it logged its own run.
            # Daemon does NOT create a duplicate record.
            print(f"  [{source_id}] OK")
            return True
        else:
            # Process failed — daemon logs this failure.
            error = result.stderr[:500] if result.stderr else 'unknown error'
            _log_daemon_run(source_id, 'error', error, started_at, finished_at)
            print(f"  [{source_id}] ERROR: {error[:100]}")
            return False

    except subprocess.TimeoutExpired:
        finished_at = datetime.now(timezone.utc).isoformat()
        _log_daemon_run(source_id, 'error', 'timeout after 600s', started_at, finished_at)
        print(f"  [{source_id}] TIMEOUT")
        return False
    except Exception as e:
        finished_at = datetime.now(timezone.utc).isoformat()
        _log_daemon_run(source_id, 'error', str(e)[:500], started_at, finished_at)
        print(f"  [{source_id}] EXCEPTION: {e}")
        return False


def _log_daemon_run(source_id, status, error, started_at, finished_at):
    """Only log daemon-level failures (process crash, timeout)."""
    conn = get_db()
    conn.execute(
        "INSERT INTO collector_run "
        "(source_id, started_at, finished_at, status, error) "
        "VALUES (?, ?, ?, ?, ?)",
        (source_id, started_at, finished_at, f'daemon_{status}', error)
    )
    conn.commit()
    conn.close()


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


def show_status():
    """Show health status of all collectors."""
    conn = get_db()
    print("\n=== COLLECTOR HEALTH STATUS ===\n")

    for source in SOURCES:
        source_id = source['id']
        enabled = source.get('enabled', True)

        row = conn.execute(
            "SELECT status, finished_at, source_records_new, error "
            "FROM collector_run WHERE source_id = ? ORDER BY finished_at DESC LIMIT 1",
            (source_id,)
        ).fetchone()

        if row:
            status, last_run, new, error = row
            lr = (last_run or '')[:19]
            err_str = f" err={error[:40]}" if error else ""
            print(f"  {source_id:20s}  {status:12s}  last: {lr}  new: {new or 0}{err_str}")
        else:
            print(f"  {source_id:20s}  {'no_run':12s}  (never run)")

        if not enabled:
            print(f"  {'':20s}  ⚠ DISABLED (needs API key)")

    # Summary
    rows = conn.execute(
        "SELECT source_id, COUNT(*) as runs, MAX(finished_at) as last "
        "FROM collector_run GROUP BY source_id"
    ).fetchall()

    print(f"\n  Total sources: {len(SOURCES)}")
    print(f"  Active collectors: {len(rows)}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Repair Garden Collector Daemon')
    parser.add_argument('--loop', action='store_true', help='Run on schedule')
    parser.add_argument('--interval', type=int, default=3600, help='Loop interval in seconds')
    parser.add_argument('--init-db', action='store_true', help='Initialize database only')
    parser.add_argument('--status', action='store_true', help='Show collector health status')
    args = parser.parse_args()

    init_db()

    if args.init_db:
        return

    if args.status:
        show_status()
        return

    if args.loop:
        loop(args.interval)
    else:
        run_once()


if __name__ == '__main__':
    main()
