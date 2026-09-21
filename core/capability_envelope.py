"""
UKGraph Core — CapabilityEnvelope.

From SPEC.md section 6:
"This is ephemeral task context. UKGraph should not require permanent storage of
emails, private conversations, medical information, complete purchase history,
complete calendar history, identity secrets."
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CapabilityEnvelope:
    """The minimum useful context about a person for economic routing.
    
    This is ephemeral task context, NOT a permanent profile.
    The personal agent decides what to disclose.
    """
    # Where
    place: str = ""
    radius_miles: int = 20
    
    # What they can do
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    
    # When they can do it
    available_windows: List[str] = field(default_factory=list)  # ["Saturday", "Sunday"]
    available_hours: int = 0
    
    # Resources
    capital_gbp: float = 0
    vehicle: str = ""
    
    # Goal
    target_gbp: float = 0
    deadline: str = ""
    risk_tolerance: str = "medium"  # low, medium, high
    
    # Preferences (from agent, not stored permanently)
    interests: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "place": self.place,
            "radius_miles": self.radius_miles,
            "skills": self.skills,
            "certifications": self.certifications,
            "equipment": self.equipment,
            "available_windows": self.available_windows,
            "available_hours": self.available_hours,
            "capital_gbp": self.capital_gbp,
            "vehicle": self.vehicle,
            "target_gbp": self.target_gbp,
            "deadline": self.deadline,
            "risk_tolerance": self.risk_tolerance,
            "interests": self.interests,
            "dislikes": self.dislikes,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> 'CapabilityEnvelope':
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
