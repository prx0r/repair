from __future__ import annotations
import hashlib, json, os
import requests
from .registry import get_source
from .compat import store_observation, utcnow, HAVE_POW_CORE, pow_fetch_json

def _subst(url, params):
    for k,v in params.items(): url=url.replace('{'+k+'}',str(v))
    return url

def probe(source_id: str, params=None, timeout=30):
    """Generic GET probe for simple/keyless sources.

    When running inside powpowpow, core.fetch_json archives the exact raw response
    before parsing and returns the raw observation lineage. Auth-specific sources
    fail loudly until their dedicated collector is configured.
    """
    s=get_source(source_id); params=params or {}
    if s.get('auth') not in ('none','optional_key','optional_token'):
        raise RuntimeError(f"{source_id} requires {s.get('auth')}; add source-specific adapter / credentials")
    url=_subst(s['url'], params)
    headers={'User-Agent':'POW.SYSTEMS research probe/0.1 contact=agents@intelligentothers.xyz','Accept':'application/json,text/csv,*/*'}
    if source_id=='openalex_frontier' and os.getenv('OPENALEX_API_KEY'):
        sep='&' if '?' in url else '?'; url += sep+'api_key='+os.environ['OPENALEX_API_KEY']
    if source_id.startswith('github_') and os.getenv('GITHUB_TOKEN'):
        headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']; headers['X-GitHub-Api-Version']='2026-03-10'
    raw_event_id=None
    if HAVE_POW_CORE and not headers.get('Authorization'):
        got=pow_fetch_json(url, timeout=timeout, source_id=source_id, chain_id=s['family'],
                           archive=True, source_role='raw', event_type='source_snapshot', return_result=True)
        status=got.get('http_status',0); raw_event_id=got.get('observation_id'); parsed=got.get('parsed')
        body=json.dumps(parsed,default=str).encode() if not isinstance(parsed,str) else parsed.encode()
        preview=str(parsed)[:500]
    else:
        r=requests.get(url,headers=headers,timeout=timeout); status=r.status_code; body=r.content; preview=r.text[:500]
    sha=hashlib.sha256(body).hexdigest()
    row={'entity_id':f'source:{source_id}','entity_type':'source','metric':'raw_snapshot',
         'value':{'http_status':status,'bytes':len(body),'sha256':sha},'unit':None,'event_time':utcnow(),
         'source_id':source_id,'raw_event_id':raw_event_id,
         'dimensions':{'url':url,'family':s['family']},'state':'observed'}
    store_observation(s['family'],row)
    return {'source':s,'status':status,'sha256':sha,'bytes':len(body),'raw_event_id':raw_event_id,'preview':preview}
