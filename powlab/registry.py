from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT/'config'/'pow_sources.json'

def load_sources(path=None):
    with open(path or DEFAULT) as f:
        return json.load(f)

def get_source(source_id, path=None):
    for s in load_sources(path):
        if s['id'] == source_id:
            return s
    raise KeyError(source_id)

def filter_sources(priority=None, family=None, path=None):
    xs=load_sources(path)
    if priority: xs=[x for x in xs if x.get('priority')==priority]
    if family: xs=[x for x in xs if x.get('family')==family]
    return xs
