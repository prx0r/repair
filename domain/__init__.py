"""Domain — the five gardens of Repair."""

from .gardens import (
    AssetPassport, Component, SubstitutionEdge,
    FaultRecord,
    PartOffer,
    ListingState, MarketListing,
    OutcomeReceipt, RepairCase,
)
from .capability import Capability, CapabilityOntology, CAPABILITY_REGISTRY
from .geography import Geography, GeographyResolver, UK_GEOGRAPHY
from .contracts import Observation, DerivedFact, EconomicEvent, Relationship

__all__ = [
    # Asset Garden
    "AssetPassport", "Component", "SubstitutionEdge",
    # Failure Garden
    "FaultRecord",
    # Parts Garden
    "PartOffer",
    # Market Garden
    "ListingState", "MarketListing",
    # Outcome Garden
    "OutcomeReceipt", "RepairCase",
    # Shared
    "Observation", "DerivedFact", "EconomicEvent", "Relationship",
    "Capability", "Geography",
]
