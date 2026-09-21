"""Capability Ontology — the heart of POWUK.

A person/business might have capabilities like:
  electrical_domestic_installation
  ev_chargepoint_installation
  solar_pv_installation
  heat_pump_installation
  f_gas_refrigeration

Qualifications/certifications map onto these. Jobs, legislation,
procurement and training all point at the same capability IDs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CapabilityType(Enum):
    """What kind of capability this is."""
    INSTALLATION = "installation"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INSPECTION = "inspection"
    DESIGN = "design"
    CONSULTING = "consulting"
    OPERATIONS = "operations"


@dataclass
class Capability:
    """A specific physical task someone can perform.

    The central primitive. Everything else maps onto this.
    """
    capability_id: str           # stable ID, e.g. "electrical_domestic_installation"
    name: str                    # human-readable
    domain: str                  # "electrical", "solar", "heat_pump", "ev", "hvac", etc.
    capability_type: CapabilityType

    # What qualifications confer this capability
    qualification_ids: list = field(default_factory=list)  # IDs of qualifications
    certification_ids: list = field(default_factory=list)  # IDs of certification schemes

    # What this capability enables
    enables_actions: list = field(default_factory=list)    # e.g. ["install_charger", "wire_circuit"]

    # Dependencies
    prerequisite_capabilities: list = field(default_factory=list)  # must have these first

    # Metadata
    description: str = ""
    sco_code: str = ""           # Standard Occupational Classification code
    ons_sector: str = ""         # ONS industry sector

    def implies(self) -> list:
        """What other capabilities this one implies."""
        return self.prerequisite_capabilities.copy()


@dataclass
class Qualification:
    """A formal qualification that confers capabilities."""
    qualification_id: str
    name: str
    level: str                   # "level_2", "level_3", "level_4", etc.
    awarding_body: str = ""
    sector: str = ""
    capabilities_conferred: list = field(default_factory=list)
    duration_weeks: int = 0
    apprenticeship_standard: str = ""  # if part of an apprenticeship


@dataclass
class CertificationScheme:
    """A certification scheme (e.g. MCS, OZEV, F-Gas, TrustMark)."""
    scheme_id: str
    name: str
    authority: str               # "MCS", "OZEV", "F-Gas", "TrustMark", etc.
    capabilities_conferred: list = field(default_factory=list)
    renewal_years: int = 0       # 0 = no renewal
    url: str = ""
    requires_qualification: str = ""  # qualification_id needed first


class CapabilityOntology:
    """Registry of all capabilities, qualifications, and certifications."""

    def __init__(self):
        self.capabilities: dict[str, Capability] = {}
        self.qualifications: dict[str, Qualification] = {}
        self.certifications: dict[str, CertificationScheme] = {}

    def register_capability(self, cap: Capability):
        self.capabilities[cap.capability_id] = cap

    def register_qualification(self, qual: Qualification):
        self.qualifications[qual.qualification_id] = qual

    def register_certification(self, cert: CertificationScheme):
        self.certifications[cert.scheme_id] = cert

    def get_capability(self, capability_id: str) -> Optional[Capability]:
        return self.capabilities.get(capability_id)

    def capabilities_for_qualification(self, qual_id: str) -> list:
        """What capabilities does this qualification confer?"""
        qual = self.qualifications.get(qual_id)
        if not qual:
            return []
        return qual.capabilities_conferred

    def capabilities_for_certification(self, cert_id: str) -> list:
        """What capabilities does this certification confer?"""
        cert = self.certifications.get(cert_id)
        if not cert:
            return []
        return cert.capabilities_conferred

    def qualifications_for_capability(self, cap_id: str) -> list:
        """What qualifications are needed for this capability?"""
        cap = self.capabilities.get(cap_id)
        if not cap:
            return []
        return cap.qualification_ids

    def implied_chain(self, cap_id: str, visited=None) -> list:
        """Transitive closure of all capabilities implied by this one."""
        if visited is None:
            visited = set()
        if cap_id in visited:
            return []
        visited.add(cap_id)
        cap = self.capabilities.get(cap_id)
        if not cap:
            return []
        chain = [cap_id]
        for prereq in cap.prerequisite_capabilities:
            chain.extend(self.implied_chain(prereq, visited))
        return chain


# ============================================================
# THE REGISTRY — UK physical capability ontology
# ============================================================

CAPABILITY_REGISTRY = CapabilityOntology()

# --- ELECTRICAL ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="electrical_domestic_installation",
    name="Domestic Electrical Installation",
    domain="electrical",
    capability_type=CapabilityType.INSTALLATION,
    qualification_ids=["city_guilds_2391", "city_guilds_2399"],
    certification_ids=["competent_person_electrical"],
    enables_actions=["wire_circuit", "install_consumer_unit", "test_electrical"],
    description="Install, maintain and test electrical systems in domestic properties",
    sco_code="6131",
))

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="electrical_commercial_installation",
    name="Commercial Electrical Installation",
    domain="electrical",
    capability_type=CapabilityType.INSTALLATION,
    qualification_ids=["city_guilds_2391", "city_guilds_2399"],
    certification_ids=["competent_person_electrical"],
    prerequisite_capabilities=["electrical_domestic_installation"],
    enables_actions=["wire_three_phase", "install_industrial_panel"],
    sco_code="6131",
))

# --- EV ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="ev_chargepoint_installation",
    name="EV Chargepoint Installation",
    domain="ev",
    capability_type=CapabilityType.INSTALLATION,
    qualification_ids=["city_guilds_2919", "city_guilds_2921"],
    certification_ids=["ozev_approved_installer"],
    prerequisite_capabilities=["electrical_domestic_installation"],
    enables_actions=["install_wallbox", "install_rapid_charger"],
    description="Install, maintain and test EV charging equipment",
))

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="ev_chargepoint_maintenance",
    name="EV Chargepoint Maintenance",
    domain="ev",
    capability_type=CapabilityType.MAINTENANCE,
    certification_ids=["ozev_approved_installer"],
    prerequisite_capabilities=["ev_chargepoint_installation"],
    enables_actions=["service_charger", "diagnose_charger_fault"],
))

# --- SOLAR ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="solar_pv_installation",
    name="Solar PV Installation",
    domain="solar",
    capability_type=CapabilityType.INSTALLATION,
    qualification_ids=["city_guilds_2922", "nvq_level_3_roofing"],
    certification_ids=["mcs_solar"],
    prerequisite_capabilities=["electrical_domestic_installation"],
    enables_actions=["install_pv_array", "wire_inverter", "commission_system"],
))

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="solar_pv_maintenance",
    name="Solar PV Maintenance",
    domain="solar",
    capability_type=CapabilityType.MAINTENANCE,
    certification_ids=["mcs_solar"],
    prerequisite_capabilities=["solar_pv_installation"],
    enables_actions=["clean_panels", "test_inverter", "replace_module"],
))

# --- HEAT PUMPS ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="heat_pump_installation",
    name="Heat Pump Installation",
    domain="heat_pump",
    capability_type=CapabilityType.INSTALLATION,
    qualification_ids=["city_guilds_6281", "nvq_level_3_plumbing"],
    certification_ids=["mcs_heat_pump"],
    prerequisite_capabilities=["electrical_domestic_installation"],
    enables_actions=["install_air_source", "install_ground_source", "commission_heat_pump"],
))

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="heat_pump_maintenance",
    name="Heat Pump Maintenance",
    domain="heat_pump",
    capability_type=CapabilityType.MAINTENANCE,
    certification_ids=["mcs_heat_pump"],
    prerequisite_capabilities=["heat_pump_installation"],
    enables_actions=["service_heat_pump", "diagnose_refrigerant"],
))

# --- F-GAS ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="f_gas_refrigeration",
    name="F-Gas Refrigeration Handling",
    domain="hvac",
    capability_type=CapabilityType.OPERATIONS,
    certification_ids=["f_gas_certificate"],
    enables_actions=["handle_refrigerant", "service_ac", "service_heat_pump"],
    description="Handle fluorinated greenhouse gases in refrigeration and air conditioning",
))

# --- BATTERY / STORAGE ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="battery_storage_installation",
    name="Battery Storage Installation",
    domain="battery",
    capability_type=CapabilityType.INSTALLATION,
    certification_ids=["mcs_battery"],
    prerequisite_capabilities=["electrical_domestic_installation"],
    enables_actions=["install_home_battery", "commission_storage"],
))

# --- RETROFIT ---

CAPABILITY_REGISTRY.register_capability(Capability(
    capability_id="retrofit_assessment",
    name="Retrofit Assessment",
    domain="retrofit",
    capability_type=CapabilityType.INSPECTION,
    qualification_ids=["ocity_energy_assessor"],
    enables_actions=["assess_property", "produce_epc", "plan_retrofit"],
))

# --- QUALIFICATIONS ---

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_2391",
    name="City & Guilds 2391 - Inspection & Testing",
    level="level_3",
    awarding_body="City & Guilds",
    sector="electrical",
    capabilities_conferred=["electrical_domestic_installation", "electrical_commercial_installation"],
    duration_weeks=20,
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_2399",
    name="City & Guilds 2399 - EV Charging",
    level="level_3",
    awarding_body="City & Guilds",
    sector="ev",
    capabilities_conferred=["ev_chargepoint_installation"],
    duration_weeks=10,
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_2919",
    name="City & Guilds 2919 - EV Charging Equipment",
    level="level_3",
    awarding_body="City & Guilds",
    sector="ev",
    capabilities_conferred=["ev_chargepoint_installation"],
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_2921",
    name="City & Guilds 2921 - EV Charging Design",
    level="level_4",
    awarding_body="City & Guilds",
    sector="ev",
    capabilities_conferred=["ev_chargepoint_installation"],
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_2922",
    name="City & Guilds 2922 - Solar PV Installation",
    level="level_3",
    awarding_body="City & Guilds",
    sector="solar",
    capabilities_conferred=["solar_pv_installation"],
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="city_guilds_6281",
    name="City & Guilds 6281 - Heat Pump Systems",
    level="level_3",
    awarding_body="City & Guilds",
    sector="heat_pump",
    capabilities_conferred=["heat_pump_installation"],
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="nvq_level_3_plumbing",
    name="NVQ Level 3 - Plumbing and Heating",
    level="level_3",
    awarding_body="City & Guilds / EAL",
    sector="plumbing",
    capabilities_conferred=["heat_pump_installation"],
    duration_weeks=52,
))

CAPABILITY_REGISTRY.register_qualification(Qualification(
    qualification_id="nvq_level_3_roofing",
    name="NVQ Level 3 - Roofing (Solar)",
    level="level_3",
    awarding_body="CITB",
    sector="roofing",
    capabilities_conferred=["solar_pv_installation"],
))

# --- CERTIFICATIONS ---

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="competent_person_electrical",
    name="Competent Person Scheme (Electrical)",
    authority="Electrical Competent Person",
    capabilities_conferred=["electrical_domestic_installation", "electrical_commercial_installation"],
    renewal_years=3,
    url="https://www.electricalcompetentperson.co.uk/",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="mcs_solar",
    name="MCS Solar PV Certification",
    authority="MCS",
    capabilities_conferred=["solar_pv_installation", "solar_pv_maintenance"],
    renewal_years=3,
    url="https://mcscertified.com/",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="mcs_heat_pump",
    name="MCS Heat Pump Certification",
    authority="MCS",
    capabilities_conferred=["heat_pump_installation", "heat_pump_maintenance"],
    renewal_years=3,
    url="https://mcscertified.com/",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="mcs_battery",
    name="MCS Battery Storage Certification",
    authority="MCS",
    capabilities_conferred=["battery_storage_installation"],
    renewal_years=3,
    url="https://mcscertified.com/",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="ozev_approved_installer",
    name="OZEV Approved Chargepoint Installer",
    authority="OZEV",
    capabilities_conferred=["ev_chargepoint_installation", "ev_chargepoint_maintenance"],
    renewal_years=0,  # no renewal documented
    url="https://www.gov.uk/electric-vehicle-chargepoint-installers",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="f_gas_certificate",
    name="F-Gas Certificate",
    authority="Environment Agency",
    capabilities_conferred=["f_gas_refrigeration"],
    renewal_years=3,
    url="https://www.gov.uk/guidance/f-gas-certificate",
))

CAPABILITY_REGISTRY.register_certification(CertificationScheme(
    scheme_id="ocity_energy_assessor",
    name="OCITY Energy Assessor",
    authority="BEIS",
    capabilities_conferred=["retrofit_assessment"],
    renewal_years=5,
))
