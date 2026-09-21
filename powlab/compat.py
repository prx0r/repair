"""Compatibility layer for current PowPowPow core.py.

Inside the repo, normalized observations use core.store_normalized and raw HTTP
calls can use core.fetch_json. Standalone mode writes append-only JSONL.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime, timezone

try:
    from core import fetch_json as pow_fetch_json, store_normalized as pow_store_normalized, utcnow
    HAVE_POW_CORE = True
except Exception:
    HAVE_POW_CORE = False
    pow_fetch_json = None
    pow_store_normalized = None
    def utcnow():
        return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

BASE = Path(os.environ.get('POWLAB_WAREHOUSE', Path.cwd()/'.powlab_warehouse'))

def store_observation(domain: str, row: dict, table: str='causal_observation'):
    if HAVE_POW_CORE:
        return pow_store_normalized(table, domain, row,
                                    raw_event_id=row.get('raw_event_id'),
                                    event_time=row.get('event_time'))
    d = BASE/'normalized'/table/f'domain={domain}'
    d.mkdir(parents=True, exist_ok=True)
    p = d/'rows.jsonl'
    record={'observed_at': utcnow(), **row}
    with p.open('a') as f:
        f.write(json.dumps(record, default=str)+'\n')
    return str(p)
