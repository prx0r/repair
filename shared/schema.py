"""
repair shared schema — canonical types for the Repair Garden.

Hierarchy:
    shared/ → Observation, Entity, DerivedFact, EconomicEvent
    repair/ → Asset, Fault, Part, PartOffer, Compatibility, RepairAttempt, Outcome

This is the ONLY schema contract. All collectors produce these types.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
import hashlib
import json


# ─── ENUMS ────────────────────────────────────────────────────

class TruthClass(Enum):
    OBSERVED = "observed"           # directly measured
    REPORTED = "reported"           # from a source, not verified
    DERIVED = "derived"             # computed from other observations
    ESTIMATED = "estimated"         # modeled/inferred
    UNKNOWN = "unknown"


class Recoverability(Enum):
    IRREVERSIBLE = "irreversible"   # data changes, can't re-collect
    SNAPSHOT = "snapshot"           # point-in-time, could re-collect
    CANONICAL = "canonical"         # authoritative, won't change
    EPHEMERAL = "ephemeral"         # listing prices, availability


class EntityState(Enum):
    NEW = "new"
    WORKING = "working"
    FAULTY = "faulty"
    PARTIALLY_REPAIRED = "partially_repaired"
    REPAIRED = "repaired"
    PARTED_OUT = "parted_out"
    SCRAPPED = "scrapped"
    SOLD = "sold"
    UNKNOWN = "unknown"


# ─── SHARED ENTITIES ──────────────────────────────────────────

@dataclass
class Entity:
    """Base entity — anything with persistent identity."""
    entity_id: str
    entity_type: str               # asset_model, part, supplier, etc.
    canonical_name: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    attributes: Optional[dict] = None
    
    def __post_init__(self):
        if not self.entity_id:
            raw = f"{self.entity_type}:{self.canonical_name}"
            self.entity_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class Observation:
    """Immutable observation — the atomic unit of the garden."""
    observation_id: str
    garden: str
    source_id: str
    entity_id: str
    metric: str
    value: Optional[str] = None
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    event_time: Optional[str] = None
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    truth_class: TruthClass = TruthClass.OBSERVED
    recoverability: Recoverability = Recoverability.SNAPSHOT
    rights: str = "powuk_internal"
    raw_payload_hash: Optional[str] = None
    source_native_id: Optional[str] = None
    payload_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.observation_id:
            # Use source_native_id if available for stable IDs
            if self.source_native_id:
                raw = f"{self.source_id}:{self.source_native_id}:{self.observed_at}"
            else:
                raw = f"{self.source_id}:{self.entity_id}:{self.metric}:{self.event_time}:{self.observed_at}"
            self.observation_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class DerivedFact:
    """Computed from observations — can be recomputed."""
    derived_id: str
    garden: str
    entity_id: str
    metric: str
    value: Optional[str] = None
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    computed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    method_id: str = "unknown"
    method_version: str = "1.0"
    input_ids: List[str] = field(default_factory=list)
    truth_class: TruthClass = TruthClass.DERIVED
    confidence: Optional[float] = None  # NOT fake 0.9 — None if unknown
    rights: str = "powuk_internal"
    
    def __post_init__(self):
        if not self.derived_id:
            raw = f"{self.entity_id}:{self.metric}:{self.method_id}:{self.computed_at}"
            self.derived_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class EntityResolution:
    """Records how entities were resolved/matched."""
    resolution_id: str
    source_record_id: str
    candidate_entity_id: str
    match_method: str              # exact, fuzzy, manual
    match_features: Optional[str] = None
    confidence: float = 0.0
    resolved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolver_version: str = "1.0"
    
    def __post_init__(self):
        if not self.resolution_id:
            raw = f"{self.source_record_id}:{self.candidate_entity_id}:{self.match_method}"
            self.resolution_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


# ─── REPAIR ENTITIES ──────────────────────────────────────────

@dataclass
class AssetFamily:
    """Broad category of asset."""
    family_id: str
    name: str                      # "GPU", "Smartphone", "Laptop"
    description: Optional[str] = None
    
    def __post_init__(self):
        if not self.family_id:
            self.family_id = hashlib.sha256(f"family:{self.name}".encode()).hexdigest()[:24]


@dataclass
class AssetModel:
    """Specific make/model of asset."""
    model_id: str
    family_id: str
    manufacturer: str
    model_name: str
    model_number: Optional[str] = None
    release_date: Optional[str] = None
    
    def __post_init__(self):
        if not self.model_id:
            raw = f"model:{self.manufacturer}:{self.model_name}"
            self.model_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class AssetRevision:
    """Hardware revision within a model."""
    revision_id: str
    model_id: str
    revision_code: str             # "Rev 1.0", "PCB X"
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.revision_id:
            raw = f"revision:{self.model_id}:{self.revision_code}"
            self.revision_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class AssetInstance:
    """One specific physical item."""
    instance_id: str
    model_id: str
    revision_id: Optional[str] = None
    serial_number: Optional[str] = None
    acquired_at: Optional[str] = None
    acquisition_cost: Optional[float] = None
    current_state: EntityState = EntityState.UNKNOWN
    
    def __post_init__(self):
        if not self.instance_id:
            raw = f"instance:{self.model_id}:{self.serial_number or 'unknown'}"
            self.instance_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class Fault:
    """A fault/defect on an asset."""
    fault_id: str
    fault_type: str                # "dead_battery", "cracked_screen", "no_power"
    description: Optional[str] = None
    symptoms: Optional[str] = None  # JSON array of symptoms
    severity: Optional[str] = None
    
    def __post_init__(self):
        if not self.fault_id:
            raw = f"fault:{self.fault_type}"
            self.fault_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class FaultObservation:
    """Observed fault on a specific asset instance."""
    observation_id: str
    instance_id: str
    fault_id: str
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_id: str = ""
    confidence: Optional[float] = None  # None, not 0.9
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.observation_id:
            raw = f"fault_obs:{self.instance_id}:{self.fault_id}:{self.observed_at}"
            self.observation_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class Part:
    """A replacement component — persistent entity."""
    part_id: str
    manufacturer: str
    mpn: str                       # manufacturer part number
    description: Optional[str] = None
    specifications: Optional[str] = None  # JSON
    category: Optional[str] = None
    
    def __post_init__(self):
        if not self.part_id:
            raw = f"part:{self.manufacturer}:{self.mpn}"
            self.part_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class PartOffer:
    """Ephemeral market observation of a part."""
    offer_id: str
    part_id: str
    supplier_id: str
    price: Optional[float] = None
    currency: str = "GBP"
    stock_quantity: Optional[int] = None  # None, not 0
    moq: Optional[int] = None
    lead_time_days: Optional[int] = None
    condition: str = "new"
    listing_url: Optional[str] = None
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def __post_init__(self):
        if not self.offer_id:
            raw = f"offer:{self.part_id}:{self.supplier_id}:{self.observed_at}"
            self.offer_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class Compatibility:
    """Part ↔ Asset compatibility relationship."""
    compatibility_id: str
    part_id: str
    model_id: str
    revision_id: Optional[str] = None
    compatibility_type: str = "direct_fit"  # direct_fit, compatible, requires_mod
    confidence: float = 1.0
    evidence: Optional[str] = None  # source of compatibility claim
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    
    def __post_init__(self):
        if not self.compatibility_id:
            raw = f"compat:{self.part_id}:{self.model_id}"
            self.compatibility_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class Intervention:
    """A repair action taken."""
    intervention_id: str
    instance_id: str
    fault_id: str
    actions: str                   # JSON array of actions
    parts_used: Optional[str] = None  # JSON array of part_ids
    tools_required: Optional[str] = None
    labour_minutes: Optional[int] = None
    skill_level: Optional[str] = None  # easy, moderate, expert
    
    def __post_init__(self):
        if not self.intervention_id:
            raw = f"intervention:{self.instance_id}:{self.fault_id}:{datetime.now(timezone.utc).isoformat()}"
            self.intervention_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


@dataclass
class RepairAttempt:
    """Complete repair receipt — the proprietary garden data."""
    attempt_id: str
    instance_id: str
    model_id: str
    
    # Input state
    fault_observations: str         # JSON array of fault_observation_ids
    condition_before: Optional[str] = None
    
    # Diagnosis
    suspected_faults: Optional[str] = None  # JSON array
    diagnosis_confidence: Optional[float] = None  # None, not 0.9
    
    # Intervention
    intervention_id: Optional[str] = None
    parts_used: Optional[str] = None
    labour_minutes: Optional[int] = None
    tools_used: Optional[str] = None
    
    # Economics
    acquisition_cost: Optional[float] = None
    parts_cost: Optional[float] = None
    labour_cost: Optional[float] = None
    total_cost: Optional[float] = None
    
    # Immediate outcome
    repaired: Optional[bool] = None  # None = unknown
    partially_repaired: Optional[bool] = None
    
    # Longitudinal outcome
    survived_7d: Optional[bool] = None
    survived_30d: Optional[bool] = None
    failed_again: Optional[bool] = None
    failure_mode: Optional[str] = None
    
    # Market outcome
    resale_price: Optional[float] = None
    days_to_sale: Optional[int] = None
    
    # Provenance
    source_id: str = ""
    photos: Optional[str] = None  # JSON array of photo URLs
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def __post_init__(self):
        if not self.attempt_id:
            raw = f"repair:{self.instance_id}:{self.observed_at}"
            self.attempt_id = hashlib.sha256(raw.encode()).hexdigest()[:24]


# ─── SCHEMA REGISTRY ─────────────────────────────────────────

ALL_TYPES = {
    "entity": Entity,
    "observation": Observation,
    "derived_fact": DerivedFact,
    "entity_resolution": EntityResolution,
    "asset_family": AssetFamily,
    "asset_model": AssetModel,
    "asset_revision": AssetRevision,
    "asset_instance": AssetInstance,
    "fault": Fault,
    "fault_observation": FaultObservation,
    "part": Part,
    "part_offer": PartOffer,
    "compatibility": Compatibility,
    "intervention": Intervention,
    "repair_attempt": RepairAttempt,
}
