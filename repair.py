#!/usr/bin/env python3
"""Repair Garden CLI — single entrypoint for all operations.

Usage:
    python -m repair sources           # list sources
    python -m repair collect <source>  # run one collector
    python -m repair collect --all     # run all collectors
    python -m repair backfill <source> # backfill historical data
    python -m repair backfill --all    # backfill all
    python -m repair status            # show status
    python -m repair verify            # run verification
    python -m repair init              # initialize database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_init():
    from shared.db import init_db
    init_db()


def cmd_status():
    from shared.db import status
    status()


def cmd_sources():
    from sources.registry import SOURCES
    print(f'{'ID':30s} {'DOMAIN':20s} {'STATUS':15s} {'CADENCE'}')
    print('-' * 80)
    for s in SOURCES:
        print(f'{s["id"]:30s} {s.get("domain",""):20s} {s.get("status",""):15s} {s.get("cadence","")}')


def cmd_collect(source_id=None):
    if source_id == 'open_repair':
        from collectors.open_repair_historical import run
        run()
    elif source_id == 'opss':
        from collectors.opss_historical import run
        run()
    elif source_id == 'all':
        for mod in ['open_repair_historical', 'opss_historical']:
            try:
                __import__(f'collectors.{mod}').run()
            except Exception as e:
                print(f'  {mod}: {e}')
    else:
        print(f'Unknown source: {source_id}')
        print('Available: open_repair, opss, all')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    commands = {
        'init': cmd_init,
        'status': cmd_status,
        'sources': cmd_sources,
        'collect': lambda: cmd_collect(arg),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f'Unknown command: {cmd}')
        print('Commands: init, status, sources, collect')


if __name__ == '__main__':
    main()
