"""
UKGraph Core — DecisionSpec.

From SPEC.md section 20:
"Every Jev operation is versioned."
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Primitive(Enum):
    NOUL = "noul"      # yes/no
    CHOICE = "choice"  # select from options
    SCORE = "score"    # rate on rubric


class Consequence(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Fallback(Enum):
    CODE = "CODE"
    HUMAN = "HUMAN"
    DEEP_MODEL = "DEEP_MODEL"
    UNKNOWN = "UNKNOWN"


@dataclass
class DecisionSpec:
    """A versioned specification for a Jev semantic transformation.
    
    From SPEC.md:
    - version
    - eval set
    - accuracy/calibration metric
    - fallback
    - confidence threshold
    """
    id: str
    version: str = "1.0"
    
    # Jev configuration
    primitive: str = "noul"  # noul, choice, score
    question: str = ""
    allowed_outputs: list = field(default_factory=list)
    
    # Risk
    consequence: str = "LOW"  # LOW, MEDIUM, HIGH
    
    # Quality
    confidence_threshold: float = 0.5
    fallback: str = "UNKNOWN"  # CODE, HUMAN, DEEP_MODEL, UNKNOWN
    
    # Evaluation
    eval_set: str = ""  # path to eval fixtures
    accuracy: float = 0.0
    calibration: float = 0.0
    
    # Metadata
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "primitive": self.primitive,
            "question": self.question,
            "allowed_outputs": self.allowed_outputs,
            "consequence": self.consequence,
            "confidence_threshold": self.confidence_threshold,
            "fallback": self.fallback,
            "eval_set": self.eval_set,
            "accuracy": self.accuracy,
            "calibration": self.calibration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# Predefined DecisionSpecs for UKOpportunity

CAPABILITY_CLASSIFICATION = DecisionSpec(
    id="opportunity.capability_classification",
    version="1.0",
    primitive="choice",
    question="What capability dominates this opportunity?",
    allowed_outputs=["ELECTRICAL", "PLUMBING", "BUILDING", "IT", "CLEANING", "DRIVING", "OTHER"],
    consequence="LOW",
    confidence_threshold=0.6,
    fallback="CODE",
)

SOLE_TRADER_ACCESS = DecisionSpec(
    id="opportunity.sole_trader_access",
    version="1.0",
    primitive="noul",
    question="Could a sole trader plausibly perform this?",
    consequence="LOW",
    confidence_threshold=0.7,
    fallback="CODE",
)

WEEKEND_COMPATIBLE = DecisionSpec(
    id="opportunity.weekend_compatible",
    version="1.0",
    primitive="noul",
    question="Is this weekend-compatible work?",
    consequence="LOW",
    confidence_threshold=0.7,
    fallback="CODE",
)

REPAIRABLE_FAULT = DecisionSpec(
    id="product.repairable_fault",
    version="1.0",
    primitive="noul",
    question="Does this listing describe a repairable fault?",
    consequence="MEDIUM",
    confidence_threshold=0.6,
    fallback="HUMAN",
)

FAMILY_CLASSIFICATION = DecisionSpec(
    id="product.fault_family",
    version="1.0",
    primitive="choice",
    question="What fault family appears most likely?",
    allowed_outputs=["POWER", "MECHANICAL", "COSMETIC", "SOFTWARE", "UNKNOWN"],
    consequence="LOW",
    confidence_threshold=0.5,
    fallback="UNKNOWN",
)
