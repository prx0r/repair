"""Entities — domain objects that get observed over time.

Provider, Company, TrainingProvider, WorkforcePopulation,
DemandEvent, PolicyEvent, ProcurementOpportunity.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Provider:
    """A registered provider (installer, contractor, etc.)."""
    provider_id: str
    name: str
    provider_type: str           # "individual", "company", "sole_trader"

    # Company linkage
    company_number: str = ""
    company_name: str = ""

    # Geography
    geo_id: str = ""             # canonical geography ID
    postcode: str = ""

    # Capabilities
    capability_ids: list = field(default_factory=list)
    qualification_ids: list = field(default_factory=list)
    certification_ids: list = field(default_factory=list)

    # Certifiers
    certifier: str = ""          # "MCS", "OZEV", "Competent Person", etc.

    # Status
    status: str = "active"       # "active", "inactive", "revoked"
    first_seen: str = ""
    last_seen: str = ""


@dataclass
class Company:
    """A registered company."""
    company_number: str
    company_name: str
    status: str = "active"       # "active", "dissolved", "liquidation"
    company_type: str = ""       # "ltd", "plc", etc.
    sic_codes: list = field(default_factory=list)
    date_of_creation: str = ""

    # Geography
    registered_address: dict = field(default_factory=dict)
    geo_id: str = ""

    # Capabilities (derived from SIC codes + provider linkage)
    capability_ids: list = field(default_factory=list)

    # SIC to capability mapping
    relevant_sics: list = field(default_factory=list)


@dataclass
class TrainingProvider:
    """An education/training provider."""
    provider_id: str
    name: str
    provider_type: str           # "college", "training_org", "university"

    geo_id: str = ""
    postcode: str = ""

    # What they teach
    qualification_ids: list = field(default_factory=list)
    capability_ids: list = field(default_factory=list)

    # Capacity
    max_students: int = 0
    current_students: int = 0


@dataclass
class WorkforcePopulation:
    """A population of workers in a capability × geography."""
    population_id: str           # "{capability_id}:{geo_id}:{date}"
    capability_id: str
    geo_id: str
    date: str

    # Supply breakdown
    registered_count: int = 0    # from competent person registers
    mcs_count: int = 0           # MCS certified
    ozev_count: int = 0          # OZEV approved
    estimated_sole_trader: int = 0
    employed_workforce: int = 0

    # Pipeline
    apprenticeship_starts: int = 0
    apprenticeship_achievements: int = 0
    training_providers: int = 0
    expected_completions_12m: int = 0


@dataclass
class DemandEvent:
    """A demand signal for a capability in a geography."""
    event_id: str
    capability_id: str
    geo_id: str
    date: str

    # Demand breakdown
    vacancies: int = 0
    procurement_value_gbp: float = 0
    planning_derived_workload: int = 0
    policy_shocks: list = field(default_factory=list)


@dataclass
class PolicyEvent:
    """A policy change that creates or removes demand."""
    event_id: str
    title: str
    description: str

    capability_ids: list = field(default_factory=list)
    geo_ids: list = field(default_factory=list)

    direction: str = "demand_increase"  # "demand_increase", "demand_decrease"
    magnitude: str = ""          # "major", "minor", "unclear"

    effective_date: str = ""
    published_date: str = ""

    source_url: str = ""


@dataclass
class ProcurementOpportunity:
    """A public procurement opportunity."""
    opportunity_id: str
    title: str
    buyer: str

    capability_ids: list = field(default_factory=list)
    geo_id: str = ""

    value_gbp: float = 0
    published_date: str = ""
    closing_date: str = ""

    source_url: str = ""
    source_system: str = ""      # "contracts_finder", "find_a_tender"
