"""
UKGraph Core — The Route object.

A Route is not merely a search result.
It represents: A real action this agent could plausibly take.

From SPEC.md section 10:
"Every route includes source evidence, freshness and transformation lineage."
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum


class RouteType(Enum):
    JOB = "JOB"
    GIG = "GIG"
    CONTRACT = "CONTRACT"
    LEAD = "LEAD"
    SALE = "SALE"
    FLIP = "FLIP"
    GRANT = "GRANT"
    TRAINING = "TRAINING"
    SERVICE = "SERVICE"
    ADMIN = "ADMIN"
    BOOKING = "BOOKING"
    CANCELLATION = "CANCELLATION"
    SAVING = "SAVING"


class ExecutionType(Enum):
    AUTO = "AUTO"
    APPROVAL = "APPROVAL"
    AUTH_HANDOFF = "AUTH_HANDOFF"
    DECLARATION = "DECLARATION"
    HUMAN_ONLY = "HUMAN_ONLY"


class ProofRule(Enum):
    SUBMISSION_ACKNOWLEDGED = "SUBMISSION_ACKNOWLEDGED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    PAYMENT_SETTLED = "PAYMENT_SETTLED"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    APPLICATION_ACCEPTED = "APPLICATION_ACCEPTED"
    ACCOUNT_STATE_CHANGED = "ACCOUNT_STATE_CHANGED"
    PERMIT_ISSUED = "PERMIT_ISSUED"
    DOCUMENT_ISSUED = "DOCUMENT_ISSUED"
    ITEM_SOLD = "ITEM_SOLD"
    SERVICE_COMPLETED = "SERVICE_COMPLETED"
    CONTRACT_AWARDED = "CONTRACT_AWARDED"
    REFUND_RECEIVED = "REFUND_RECEIVED"


@dataclass
class Evidence:
    """A single piece of evidence supporting a route."""
    evidence_id: str
    source_id: str
    source_url: str = ""
    observed_at: str = ""      # ISO UTC
    effective_at: str = ""     # when this was true in reality
    raw_hash: str = ""         # hash of raw source artifact
    licence: str = "OGL"
    description: str = ""
    confidence: float = 1.0


@dataclass
class Freshness:
    """How current is this data?"""
    last_observed: str = ""     # ISO UTC
    source_frequency: str = ""  # daily, hourly, real-time
    max_age_hours: int = 168    # 7 days default
    stale: bool = False
    source_licence: str = ""    # OGL, transformative, etc.
    
    def check_freshness(self, reference_time: datetime = None) -> str:
        """Check if data is fresh. Returns quality state."""
        if not self.last_observed:
            return "UNKNOWN"
        
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)
        
        try:
            from datetime import datetime as dt
            observed = dt.fromisoformat(self.last_observed.replace('Z', '+00:00'))
            age_hours = (reference_time - observed).total_seconds() / 3600
            
            if age_hours > self.max_age_hours:
                self.stale = True
                return "STALE"
            elif age_hours > self.max_age_hours * 0.5:
                return "KNOWN"  # getting old but not stale
            else:
                return "KNOWN"
        except Exception:
            return "UNKNOWN"


@dataclass
class Route:
    """A real action an agent could plausibly take.
    
    This is the most important canonical output object.
    Every route MUST include evidence, freshness, and transformation lineage.
    """
    # Identity
    route_id: str
    goal: str                    # what the person wants
    route_type: RouteType
    
    # The action
    action: str                  # what to do
    target: str                  # where/how to do it
    
    # Context
    place: str = ""
    source_gardens: list = field(default_factory=list)  # which gardens contributed
    
    # Validity
    valid_from: str = ""         # ISO UTC
    expires_at: str = ""         # ISO UTC
    
    # Economics
    expected_value_gbp: float = 0
    expected_net_value_gbp: float = 0
    expected_time_hours: float = 0
    capital_required_gbp: float = 0
    
    # Capabilities
    required_capabilities: list = field(default_factory=list)
    useful_capabilities: list = field(default_factory=list)
    
    # Constraints
    hard_constraints: list = field(default_factory=list)
    uncertainties: list = field(default_factory=list)
    
    # Why this route for this person
    why_now: list = field(default_factory=list)
    why_person: list = field(default_factory=list)
    
    # Evidence chain
    evidence: list = field(default_factory=list)  # list of Evidence objects
    
    # Execution
    execution_type: ExecutionType = ExecutionType.APPROVAL
    execution_target: str = ""   # URL, form, phone number
    
    # Success proof
    success_proof: ProofRule = ProofRule.SUBMISSION_ACKNOWLEDGED
    
    # Quality
    confidence: float = 0.0      # 0-1
    
    # Freshness
    freshness: Freshness = field(default_factory=Freshness)
    
    # Transformation lineage
    transform_id: str = ""
    transform_version: str = ""
    input_observations: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "goal": self.goal,
            "route_type": self.route_type.value,
            "action": self.action,
            "target": self.target,
            "place": self.place,
            "source_gardens": self.source_gardens,
            "valid_from": self.valid_from,
            "expires_at": self.expires_at,
            "expected_value_gbp": self.expected_value_gbp,
            "expected_net_value_gbp": self.expected_net_value_gbp,
            "expected_time_hours": self.expected_time_hours,
            "capital_required_gbp": self.capital_required_gbp,
            "required_capabilities": self.required_capabilities,
            "useful_capabilities": self.useful_capabilities,
            "hard_constraints": self.hard_constraints,
            "uncertainties": self.uncertainties,
            "why_now": self.why_now,
            "why_person": self.why_person,
            "evidence": [e.__dict__ for e in self.evidence],
            "execution_type": self.execution_type.value,
            "execution_target": self.execution_target,
            "success_proof": self.success_proof.value,
            "confidence": self.confidence,
            "freshness": self.freshness.__dict__,
            "transform_id": self.transform_id,
            "transform_version": self.transform_version,
        }
