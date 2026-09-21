from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

@dataclass
class Observation:
    entity_id: str
    entity_type: str
    metric: str
    value: Any
    unit: Optional[str] = None
    event_time: Optional[str] = None
    observed_at: Optional[str] = None
    source_id: Optional[str] = None
    dimensions: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    state: str = "observed"  # observed | inferred | simulated | hypothesized

    def to_dict(self):
        return asdict(self)

@dataclass
class CausalEdge:
    src: str
    dst: str
    relation: str
    weight: float = 1.0
    confidence: float = 1.0
    lag_seconds: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    state: str = "observed"
    method: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
