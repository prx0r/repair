from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class EntityRef:
    entity_id: str
    entity_type: str  # technology|component|material|firm|occupation|facility|market|location
    name: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Observation:
    entity_id: str
    entity_type: str
    variable: str
    value: Any
    event_time: Optional[str]
    source_id: str
    unit: Optional[str] = None
    observed_at: Optional[str] = None
    dimensions: Dict[str, Any] = field(default_factory=dict)
    quality_flags: List[str] = field(default_factory=list)
    raw_event_id: Optional[str] = None
    schema_version: str = "pow-economic-observation-v1"
    def to_dict(self): return asdict(self)

@dataclass
class Relation:
    src_id: str
    dst_id: str
    relation_type: str  # requires|substitutes|complements|produced_by|uses_skill|located_at|cites
    event_time: Optional[str]
    source_id: str
    weight: Optional[float] = None
    confidence: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    raw_event_id: Optional[str] = None
    schema_version: str = "pow-economic-relation-v1"
    def to_dict(self): return asdict(self)

@dataclass
class HyperRelation:
    relation_type: str
    members: List[Dict[str, str]]  # [{entity_id, role}, ...]
    event_time: Optional[str]
    source_id: str
    score: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    raw_event_id: Optional[str] = None
    schema_version: str = "pow-economic-hyperrelation-v1"
    def to_dict(self): return asdict(self)

@dataclass
class ShockEvent:
    event_id: str
    event_type: str
    entity_id: str
    event_time: str
    source_id: str
    description: str = ""
    magnitude: Optional[float] = None
    unit: Optional[str] = None
    raw_event_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "pow-shock-event-v1"
    def to_dict(self): return asdict(self)
