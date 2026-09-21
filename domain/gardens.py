"""Five Gardens — the complete Repair data model.

1. ASSET GARDEN    — identity, model, revision, composition
2. FAILURE GARDEN  — symptoms, defects, recalls, diagnosis
3. PARTS GARDEN    — MPNs, substitutes, donors, stock, price
4. MARKET GARDEN   — broken / working / parts marketplace tape
5. OUTCOME GARDEN  — intervention → result → survival → economics
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


# ============================================================
# 1. ASSET GARDEN
# ============================================================

@dataclass
class AssetPassport:
    """Continuously evolving passport for a physical object."""
    asset_id: str

    # Identity
    manufacturer: str = ""
    model: str = ""
    model_family: str = ""
    generation: str = ""
    revision: str = ""
    board_ids: list = field(default_factory=list)  # board revisions, subsystem IDs
    aliases: list = field(default_factory=list)     # marketplace identities, variant names

    # Physical composition
    assemblies: list = field(default_factory=list)  # sub-assemblies
    components: list = field(default_factory=list)  # MPNs of installed components
    substitutes: list = field(default_factory=list) # known compatible substitutes
    donor_devices: list = field(default_factory=list) # devices this can donate parts to

    # History
    manufacture_date: str = ""
    ownership_history: list = field(default_factory=list)  # where permissioned
    failure_history: list = field(default_factory=list)
    repair_history: list = field(default_factory=list)
    modification_history: list = field(default_factory=list)
    test_history: list = field(default_factory=list)

    # Current state
    condition: str = ""          # new/like_new/excellent/good/fair/poor/broken/for_parts
    faults: list = field(default_factory=list)
    performance_metrics: dict = field(default_factory=dict)
    energy_use_watts: float = 0
    safety_status: str = ""     # safe/recalled/unknown

    # Economics
    working_value_gbp: float = 0
    broken_value_gbp: float = 0
    donor_value_gbp: float = 0
    parts_value_gbp: float = 0
    replacement_cost_gbp: float = 0
    deployment_value_gbp: float = 0  # value if used for mining/inference/etc

    # Possible transitions
    possible_actions: list = field(default_factory=list)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class Component:
    """A component within an asset."""
    component_id: str
    mpn: str                     # manufacturer part number
    description: str = ""
    manufacturer: str = ""
    category: str = ""           # "capacitor", "ic", "connector", etc.

    # Installed in
    asset_id: str = ""
    position: str = ""           # "U1", "C42", "J3", etc.

    # Substitutes
    compatible_mpns: list = field(default_factory=list)
    donor_assets: list = field(default_factory=list)  # devices this can be harvested from

    # Supply
    stock_status: str = ""       # in_stock, low_stock, out_of_stock, discontinued
    price_gbp: float = 0
    lead_time_days: int = 0


@dataclass
class SubstitutionEdge:
    """A proven substitution relationship."""
    original_mpn: str
    substitute_mpn: str
    relation: str                # "electrical_equivalent", "mechanical_equivalent",
                                 # "firmware_compatible", "salvaged_from", "3d_printable"

    asset_revision: str = ""     # specific device this was proven in
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0

    evidence: list = field(default_factory=list)  # source_record_ids


# ============================================================
# 2. FAILURE GARDEN
# ============================================================

@dataclass
class FaultRecord:
    """A fault observed on an asset."""
    fault_id: str
    asset_id: str

    # What happened
    symptom: str                 # "black screen", "won't power on", "overheating"
    fault_type: str              # "electrical", "mechanical", "firmware", "cosmetic"
    severity: str                # "critical", "major", "minor"

    # Diagnosis
    diagnosis: str = ""          # "VRAM failure", "capacitor bulge", "broken trace"
    failed_component_mpn: str = ""  # specific component that failed
    failure_mode: str = ""       # "open_circuit", "short", "degradation", "physical_damage"

    # Context
    device_age_years: float = 0
    usage_hours: float = 0
    environment: str = ""        # "indoor", "outdoor", "industrial", "mining"

    # Source
    source_record_id: str = ""
    observed_at: str = ""

    # Recall link
    recall_reference: str = ""   # if this is a known recalled defect


# ============================================================
# 3. PARTS GARDEN
# ============================================================

@dataclass
class PartOffer:
    """A specific part available from a supplier."""
    offer_id: str
    mpn: str
    supplier: str

    # Price
    unit_price_gbp: float = 0
    price_breaks: list = field(default_factory=list)  # [{qty: 10, price: 1.20}]

    # Availability
    stock_qty: int = 0
    lead_time_days: int = 0
    in_stock: bool = True

    # Lifecycle
    lifecycle_status: str = ""   # "active", "nrnd", "end_of_life", "discontinued"
    last_order_date: str = ""

    # Substitutes
    superseded_by: str = ""      # MPN of replacement
    cross_references: list = field(default_factory=list)

    # Source
    source_record_id: str = ""
    observed_at: str = ""


# ============================================================
# 4. MARKET GARDEN
# ============================================================

class ListingState(Enum):
    FIRST_SEEN = "first_seen"
    ACTIVE = "active"
    PRICE_CHANGED = "price_changed"
    DISAPPEARED = "disappeared"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    RELISTED = "relisted"
    UNKNOWN = "unknown"


@dataclass
class MarketListing:
    """A marketplace listing with lifecycle tracking."""
    listing_id: str
    platform: str                # "ebay", "cex", "back_market", etc.

    # Asset identity
    title: str = ""
    asset_id: str = ""           # resolved asset (if identified)
    device_model: str = ""
    condition: str = ""          # "new", "like_new", "good", "fair", "broken", "for_parts"

    # Pricing
    asking_price_gbp: float = 0
    sold_price_gbp: float = 0
    currency: str = "GBP"

    # State machine
    state: ListingState = ListingState.FIRST_SEEN
    first_seen_at: str = ""
    last_seen_at: str = ""
    disappeared_at: str = ""
    sold_at: str = ""

    # Seller
    seller_id: str = ""
    seller_rating: float = 0
    location: str = ""

    # Listing details
    listing_url: str = ""
    shipping_cost_gbp: float = 0
    collection_only: bool = False
    item_specifics: dict = field(default_factory=dict)

    # Observation history (for state transitions)
    observations: list = field(default_factory=list)  # [{price, state, observed_at}]


# ============================================================
# 5. OUTCOME GARDEN
# ============================================================

@dataclass
class OutcomeReceipt:
    """The shared primitive across all POW systems.

    prediction → execution → proof → outcome
    """
    receipt_id: str

    # What was predicted
    predicted_success_prob: float = 0
    predicted_parts_cost: float = 0
    predicted_labour_minutes: int = 0
    predicted_working_value: float = 0
    predicted_resale_days: int = 0
    predicted_ev: float = 0

    # What actually happened
    actual_success: bool = False
    actual_parts_cost: float = 0
    actual_labour_minutes: int = 0
    actual_working_value: float = 0
    actual_sold_price: float = 0
    actual_days_to_sale: int = 0

    # Error metrics
    prediction_error: float = 0
    cost_error: float = 0
    duration_error: float = 0
    valuation_error: float = 0

    # Resources used
    tools_required: list = field(default_factory=list)
    skills_required: list = field(default_factory=list)
    certifications_required: list = field(default_factory=list)

    # Context
    asset_id: str = ""
    fault_id: str = ""
    intervention: str = ""       # what was done
    part_mpn: str = ""           # part used
    substitute_mpn: str = ""     # if substitute was used

    # Timing
    intervention_date: str = ""
    outcome_date: str = ""
    survival_days: int = 0       # how long the fix lasted

    # Source
    source_record_id: str = ""


@dataclass
class RepairCase:
    """A complete repair case from diagnosis to outcome."""
    case_id: str
    asset_id: str

    # Diagnosis
    symptom: str = ""
    diagnosis: str = ""
    fault_id: str = ""

    # Decision
    repair_chosen: bool = True
    repair_cost_quoted: float = 0
    replacement_cost: float = 0
    decision_reason: str = ""    # "cheaper", "preference", "parts_available", etc.

    # Intervention
    intervention: str = ""
    part_mpn: str = ""
    substitute_mpn: str = ""
    tools_used: list = field(default_factory=list)
    labour_minutes: int = 0

    # Outcome
    success: bool = False
    retest_passed: bool = False
    sold_price: float = 0
    days_to_sale: int = 0
    survival_days: int = 0

    # Economics
    total_cost: float = 0
    total_revenue: float = 0
    profit: float = 0
    roi_pct: float = 0

    # Counterfactual
    alternative_action: str = ""  # what they could have done instead
    alternative_cost: float = 0
    alternative_revenue: float = 0

    # Source
    source_record_ids: list = field(default_factory=list)
