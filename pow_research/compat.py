"""Compatibility bridge to the existing powpowpow core.py.

Drop this package into the repo root. If `core` is importable, every network
request uses POW's auto-archiving `fetch_json` and every normalized row uses
`store_normalized`. Outside the repo it falls back to an append-only local
warehouse with the same conceptual lineage fields, so demos/tests still run.
"""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from core import fetch_json as _pow_fetch_json, store_normalized as _pow_store_normalized, utcnow as _pow_utcnow
    HAS_POW_CORE = True
except Exception:
    HAS_POW_CORE = False

BASE = Path(os.environ.get("POW_RESEARCH_WAREHOUSE", Path.cwd()/"warehouse"))

def utcnow():
    if HAS_POW_CORE: return _pow_utcnow()
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def _hash(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, default=str).encode()).hexdigest()

def fetch_json(url: str, *, source_id: str, params: Optional[Dict]=None, timeout: int=20, partition: str="physical-economy"):
    if HAS_POW_CORE:
        return _pow_fetch_json(url, params=params, timeout=timeout, source_id=source_id,
                               chain_id=partition, archive=True, return_result=True,
                               event_type="economic_source_snapshot")
    import requests
    observed = utcnow()
    r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent":"PowPowPow-Research/0.1"})
    body = r.text
    try: parsed = r.json()
    except Exception: parsed = body
    oid = _hash([source_id,url,observed,body])[:16]
    d = BASE/"raw"/partition; d.mkdir(parents=True, exist_ok=True)
    payload = {"observation_id":oid,"source_id":source_id,"endpoint":url,"request_params":params or {},
               "observed_at":observed,"response_received":utcnow(),"http_status":r.status_code,
               "raw_payload":body,"parsed_payload":parsed,"payload_hash":_hash(body),
               "schema_version":"fallback-1.0"}
    (d/f"{oid}.json").write_text(json.dumps(payload,indent=2,default=str))
    return {"parsed":parsed,"observation_id":oid,"observed_at":observed,"received_at":payload["response_received"],
            "payload_hash":payload["payload_hash"],"source_id":source_id,"http_status":r.status_code}

def store(table: str, data: Dict[str,Any], *, raw_event_id: Optional[str]=None, event_time: Optional[str]=None,
          partition: str="physical-economy"):
    if HAS_POW_CORE:
        return _pow_store_normalized(table, partition, data, raw_event_id=raw_event_id, event_time=event_time)
    now=utcnow(); date=now[:10]; hour=now[11:13]
    d=BASE/"normalized"/table/f"chain={partition}"/f"date={date}"; d.mkdir(parents=True, exist_ok=True)
    p=d/f"hour={hour}.jsonl"
    row={"record_id":f"{partition}_{table}_{now}","raw_event_id":raw_event_id,"network_id":partition,
         "event_time":event_time,"observed_at":now,"normalized_at":now,"schema_name":table,"schema_version":"1.0",**data}
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(row,default=str)+"\n")
    return str(p)
