"""POWUK Domain — the four native economic primitives.

CAPABILITY  — Who can perform a physical task now?
PIPELINE    — Who is likely to become capable later?
DEMAND      — How much demand for that capability is appearing?
FRICTION    — What prevents capacity from responding?

Everything resolves onto: CAPABILITY × GEOGRAPHY × TIME
"""

from .capability import (
    Capability, CapabilityType, Qualification, CertificationScheme,
    CapabilityOntology, CAPABILITY_REGISTRY,
)
from .geography import (
    Geography, GeoLevel, GeographyResolver, UK_GEOGRAPHY,
)
from .contracts import (
    Observation, DerivedFact, EconomicEvent, Relationship,
    TruthClass, Recoverability, TemporalSemantic,
)
from .entities import (
    Provider, Company, TrainingProvider, WorkforcePopulation,
    DemandEvent, PolicyEvent, ProcurementOpportunity,
)

__all__ = [
    "Capability", "CapabilityType", "Qualification", "CertificationScheme",
    "CapabilityOntology", "CAPABILITY_REGISTRY",
    "Geography", "GeoLevel", "GeographyResolver", "UK_GEOGRAPHY",
    "Observation", "DerivedFact", "EconomicEvent", "Relationship",
    "TruthClass", "Recoverability", "TemporalSemantic",
    "Provider", "Company", "TrainingProvider", "WorkforcePopulation",
    "DemandEvent", "PolicyEvent", "ProcurementOpportunity",
]
