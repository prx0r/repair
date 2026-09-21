"""Repair Garden schemas — domain-specific data models.

Covers:
- Fault diagnosis (what broke, how to fix it)
- Part listings (compatibility, pricing, availability)
- Repair economics (cost to fix vs replace vs resale)
- Resale listings (broken/as-is/fixed pricing curves)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class Condition(Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    BROKEN = "broken"
    FOR_PARTS = "for_parts"


class RepairVerdict(Enum):
    REPAIR = "repair"           # cheaper to fix than replace
    REPLACE = "replace"         # cheaper to replace than fix
    PARTS_VALUE = "parts_value" # item worth more as parts
    SCRAP = "scrap"             # no economic value
    NO_DATA = "no_data"         # insufficient data to decide


@dataclass
class FaultRecord:
    """A known fault pattern for a device model.
    
    Accumulated knowledge: what breaks, how often, how to fix it.
    """
    fault_id: str
    device_entity_id: str       # which device
    device_model: str           # e.g. "iPhone 13 Pro", "RTX 4090"
    device_category: str        # phone, laptop, gpu, solar_panel, robot, etc.

    # The fault
    fault_type: str             # e.g. "battery_degradation", "screen_crack", "fan_failure"
    fault_description: str
    severity: str               # critical, major, minor, cosmetic
    frequency: str              # common, occasional, rare

    # Fix
    repair_method: str          # e.g. "battery_swap", "solder_replacement", "clean_and_repaste"
    difficulty: str             # easy, moderate, hard, professional_only
    estimated_time_minutes: int = 0

    # Cost
    parts_cost_gbp: float = 0
    labor_cost_gbp: float = 0
    total_repair_cost_gbp: float = 0

    # Alternatives
    replacement_cost_gbp: float = 0  # cost to buy same device used
    as_is_value_gbp: float = 0       # what broken unit sells for

    # Evidence
    source_observations: list = field(default_factory=list)
    confidence: float = 0.0
    n_cases: int = 0            # how many times we've seen this fault

    # Metadata
    first_seen: str = ""
    last_seen: str = ""
    tags: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v.value if hasattr(v, 'value') else v
                for k, v in self.__dict__.items()}


@dataclass
class PartListing:
    """A replacement part with pricing and compatibility data."""
    part_id: str
    part_name: str
    part_category: str          # battery, screen, connector, cable, chip, etc.

    # Compatibility
    compatible_devices: list = field(default_factory=list)  # entity_ids
    compatible_models: list = field(default_factory=list)   # free-text model names
    oem_part_number: str = ""
    cross_references: list = field(default_factory=list)    # alternative part numbers

    # Pricing
    price_gbp: float = 0
    price_source: str = ""      # ebay, amazon, digikey, aliexpress, etc.
    condition: str = "new"

    # Availability
    in_stock: bool = True
    stock_quantity: int = 0
    supplier: str = ""
    shipping_cost_gbp: float = 0
    shipping_days: int = 0

    # Quality
    seller_rating: float = 0
    n_sales: int = 0
    return_rate_pct: float = 0

    # Temporal
    observed_at: str = ""
    source_observations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v.value if hasattr(v, 'value') else v
                for k, v in self.__dict__.items()}


@dataclass
class RepairEconomics:
    """Economic analysis of a repair decision.
    
    The core question: should I fix it, replace it, part it out, or scrap it?
    """
    analysis_id: str
    device_entity_id: str
    device_model: str
    fault_id: str

    # Costs
    repair_cost_gbp: float = 0      # total cost to fix
    replacement_cost_gbp: float = 0  # cost to buy working used
    parts_value_gbp: float = 0      # what parts are worth separately
    scrap_value_gbp: float = 0      # metal/value recovery

    # Time
    repair_time_hours: float = 0
    downtime_days: float = 0        # how long user is without device

    # Verdict
    verdict: RepairVerdict = RepairVerdict.NO_DATA
    margin_gbp: float = 0           # replacement_cost - repair_cost (positive = save money)
    margin_pct: float = 0           # margin as % of replacement

    # Risk
    repair_success_rate: float = 0.9  # probability fix works
    expected_value_gbp: float = 0     # risk-adjusted value

    # Resale angle
    fixed_resale_value_gbp: float = 0
    broken_resale_value_gbp: float = 0
    resale_margin_gbp: float = 0      # fixed_resale - repair_cost - broken_resale

    # Evidence
    source_observations: list = field(default_factory=list)
    computed_at: str = ""

    def to_dict(self) -> dict:
        return {k: v.value if hasattr(v, 'value') else v
                for k, v in self.__dict__.items()}


@dataclass
class ResaleListing:
    """A listing for buying or selling used/broken electronics.
    
    Tracks the full lifecycle: new → used → broken → parts → scrap.
    """
    listing_id: str
    device_entity_id: str
    device_model: str
    device_category: str

    # Listing details
    platform: str               # ebay, vinted, gumtree, facebook, ceX, etc.
    listing_type: str           # buy_now, auction, collection, parts_only
    condition: Condition = Condition.GOOD

    # Pricing
    asking_price_gbp: float = 0
    sold_price_gbp: float = 0
    shipping_cost_gbp: float = 0

    # Seller info
    seller_rating: float = 0
    seller_location: str = ""
    collection_only: bool = False

    # Condition details
    fault_description: str = ""
    works_without_repair: bool = True
    includes_accessories: bool = False
    original_box: bool = False

    # Temporal
    listed_at: str = ""
    sold_at: str = ""
    observed_at: str = ""

    # Source
    source_url: str = ""
    source_observations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v.value if hasattr(v, 'value') else v
                for k, v in self.__dict__.items()}


@dataclass
class PriceHistory:
    """Price tracking for a device model across conditions and time.
    
    The core data structure for understanding depreciation curves.
    """
    history_id: str
    device_entity_id: str
    device_model: str
    device_category: str

    # Price points by condition
    new_price_gbp: float = 0
    used_good_price_gbp: float = 0
    used_fair_price_gbp: float = 0
    broken_price_gbp: float = 0
    parts_only_price_gbp: float = 0

    # Depreciation
    depreciation_pct_per_year: float = 0
    half_life_months: float = 0     # time to lose 50% of value

    # Market data
    n_listings: int = 0
    n_sold: int = 0
    median_sold_gbp: float = 0
    spread_pct: float = 0           # bid-ask spread

    # Temporal
    as_of: str = ""
    source_observations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v.value if hasattr(v, 'value') else v
                for k, v in self.__dict__.items()}
