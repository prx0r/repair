from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "research_data" if (ROOT / "research_data").exists() else ROOT / "data"
SOURCE_CSV = DATA_DIR / "source_assets.csv"
MODEL_CSV = DATA_DIR / "model_requirements.csv"

def _read(path):
    with open(path, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def sources(priority=None, family=None):
    rows=_read(SOURCE_CSV)
    if priority: rows=[r for r in rows if r['priority']==priority]
    if family: rows=[r for r in rows if r['family']==family]
    return rows

def source(source_id):
    return next((r for r in sources() if r['source_id']==source_id), None)

def models(): return _read(MODEL_CSV)

def coverage():
    out=[]
    for m in models():
        name=m['model']; matched=[]
        for s in sources():
            if name in s['models_unlocked'].split(';'): matched.append(s['source_id'])
        out.append({**m,'source_count':len(matched),'sources':matched})
    return out
