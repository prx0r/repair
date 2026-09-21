"""A few immediately runnable no-key collectors.
Each request goes through `compat.fetch_json`, therefore through existing POW
raw archival when installed in the repo. Normalization is intentionally thin:
we preserve source-native payload and extract only stable identifiers/timestamps.
"""
from urllib.parse import quote
from ..compat import fetch_json, store

def _archive_rows(source_id, result, rows, entity_type, id_fn, time_fn=None):
    rid=result.get('observation_id') if isinstance(result,dict) else None
    n=0
    for row in rows:
        eid=id_fn(row)
        if not eid: continue
        et=time_fn(row) if time_fn else None
        store('economic_event', {'source_id':source_id,'entity_id':eid,'entity_type':entity_type,'payload':row}, raw_event_id=rid, event_time=et)
        n+=1
    return n

def collect_openalex(query, per_page=100):
    url='https://api.openalex.org/works'
    r=fetch_json(url,source_id='openalex',params={'search':query,'per-page':per_page})
    p=r.get('parsed') or {}; rows=p.get('results',[]) if isinstance(p,dict) else []
    n=_archive_rows('openalex',r,rows,'research_work',lambda x:x.get('id'),lambda x:x.get('publication_date'))
    return {'raw_event_id':r.get('observation_id'),'normalized':n}

def collect_find_tender(updated_from, updated_to=None, stages=None, limit=100):
    url='https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages'
    params={'updatedFrom':updated_from,'limit':limit}
    if updated_to: params['updatedTo']=updated_to
    if stages: params['stages']=stages
    r=fetch_json(url,source_id='find_tender',params=params)
    p=r.get('parsed') or {}; releases=p.get('releases',[]) if isinstance(p,dict) else []
    n=_archive_rows('find_tender',r,releases,'procurement',lambda x:x.get('ocid') or x.get('id'),lambda x:x.get('date'))
    return {'raw_event_id':r.get('observation_id'),'normalized':n}

def collect_nhtsa_recalls(make, model, model_year):
    url='https://api.nhtsa.gov/recalls/recallsByVehicle'
    r=fetch_json(url,source_id='nhtsa',params={'make':make,'model':model,'modelYear':model_year})
    p=r.get('parsed') or {}; rows=p.get('results',[]) if isinstance(p,dict) else []
    n=_archive_rows('nhtsa',r,rows,'recall',lambda x:x.get('NHTSACampaignNumber') or x.get('NHTSAActionNumber'),lambda x:x.get('ReportReceivedDate'))
    return {'raw_event_id':r.get('observation_id'),'normalized':n}

def collect_planning_applications(start_date, limit=100, offset=0):
    y,m,d=map(int,start_date.split('-'))
    url='https://www.planning.data.gov.uk/entity.json'
    params={'dataset':'planning-application','start_date_year':y,'start_date_month':m,'start_date_day':d,'start_date_match':'since','limit':limit,'offset':offset}
    r=fetch_json(url,source_id='planning_data',params=params)
    p=r.get('parsed') or {}; rows=p.get('entities',p.get('entity',[])) if isinstance(p,dict) else []
    if isinstance(rows,dict): rows=[rows]
    n=_archive_rows('planning_data',r,rows,'planning_application',lambda x:str(x.get('entity') or x.get('reference') or ''),lambda x:x.get('start-date') or x.get('entry-date'))
    return {'raw_event_id':r.get('observation_id'),'normalized':n}
