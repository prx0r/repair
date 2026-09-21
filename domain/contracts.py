"""Contracts — the only shared persistence primitives.

Observation, DerivedFact, EconomicEvent, Relationship.
These are the ONLY ways data gets stored.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
import hashlib
import json


class TruthClass(Enum):
    OBSERVED = "observed"       # directly measured
    DERIVED = "derived"         # computed from observations
    ESTIMATED = "estimated"     # computed with assumptions
    RECORDED = "recorded"       # from a trusted source


class Recoverability(Enum):
    EPHEMERAL = "ephemeral"     # MUST archive now or lose forever
    RECENTLY_RECOVERABLE = "recently_recoverable"  # can reconstruct from recent data
    BACKFILLABLE = "backfillable"  # historical data exists somewhere
    PERMANENT = "permanent"     # always available


class TemporalSemantic(Enum):
    """What the timestamp means."""
    EFFECTIVE = "effective_at"     # when this was true in reality
    PUBLISHED = "published_at"     # when the source published it
    OBSERVED = "observed_at"       # when we collected it
    PERIOD_START = "period_start"  # start of measurement period
    PERIOD_END = "period_end"      # end of measurement period


@dataclass
class Observation:
    """A raw, immutable record from reality.

    The primary storage primitive. Every collector emits observations.
    """
    observation_id: str          # deterministic hash
    source_id: str               # which source
    dataset_id: str              # which dataset within the source
    entity_id: str               # what was observed
    metric: str                  # what was measured
    value: Any                   # the observation value

    # Temporal — at least 3 are mandatory
    effective_at: str = ""       # when this was true in reality
    published_at: str = ""       # when the source published it
    observed_at: str = ""        # when we collected it

    # Quality
    truth_class: TruthClass = TruthClass.OBSERVED
    recoverability: Recoverability = Recoverability.RECENTLY_RECOVERABLE

    # Provenance
    parent_observation_ids: list = field(default_factory=list)
    raw_event_id: str = ""       # link to raw storage

    # Metadata
    unit: str = ""
    tags: dict = field(default_factory=dict)

    def compute_id(self) -> str:
        content = json.dumps({
            "source_id": self.source_id,
            "entity_id": self.entity_id,
            "metric": self.metric,
            "effective_at": self.effective_at,
        }, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {k: v.value if isinstance(v, Enum) else v
                for k, v in self.__dict__.items()}


@dataclass
class DerivedFact:
    """A fact computed from observations.

    Never raw data. Always has a method that produced it.
    """
    derived_id: str
    source_id: str               # which method produced this
    entity_id: str
    metric: str
    value: Any
    method_id: str
    method_version: str

    input_observation_ids: list = field(default_factory=list)
    truth_class: TruthClass = TruthClass.DERIVED
    confidence: float = 0.0

    computed_at: str = ""
    valid_from: str = ""
    valid_to: str = ""

    limitations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v.value if isinstance(v, Enum) else v
                for k, v in self.__dict__.items()}


@dataclass
class EconomicEvent:
    """A meaningful economic occurrence.

    Events are the bridge between raw observations and derived understanding.
    """
    event_id: str
    garden: str                  # which garden this belongs to
    event_type: str              # "company_status_change", "policy_change", "procurement", etc.

    entity_ids: list = field(default_factory=list)
    direction: str = "neutral"   # "up", "down", "mixed", "neutral"
    magnitude: float = 0.0
    confidence: float = 0.0

    source_ids: list = field(default_factory=list)
    observation_ids: list = field(default_factory=list)

    effective_at: str = ""
    observed_at: str = ""

    description: str = ""

    def to_dict(self) -> dict:
        return {k: v.value if isinstance(v, Enum) else v
                for k, v in self.__dict__.items()}


@dataclass
class Relationship:
    """A directed edge between two entities.

    The graph structure that makes everything connect.
    """
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    predicate: str               # "REQUIRES", "CONFERS", "OPERATES_AT", "HAS_SIC", etc.
    confidence: float = 1.0

    start_date: str = ""
    end_date: str = ""

    source_observation_ids: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v.value if isinstance(v, Enum) else v
                for k, v in self.__dict__.items()}
