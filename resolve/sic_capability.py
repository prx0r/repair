"""SIC → Capability Mapping — links Companies House SIC codes to POWUK capabilities.

This is the bridge that makes Companies House data useful for repair/trades.
"""

# UK SIC 2007 codes relevant to physical capability
SIC_TO_CAPABILITY = {
    # --- Electrical ---
    '43210': ['electrical_domestic_installation', 'electrical_commercial_installation'],
    '43220': ['electrical_domestic_installation', 'electrical_commercial_installation'],
    '43310': ['electrical_domestic_installation'],
    '43320': ['electrical_commercial_installation'],
    '43290': ['electrical_domestic_installation'],

    # --- Solar / Renewable ---
    '43330': ['solar_pv_installation', 'battery_storage_installation'],
    '43340': ['solar_pv_installation'],

    # --- HVAC / Heat Pumps ---
    '43220': ['heat_pump_installation', 'f_gas_refrigeration'],
    '43290': ['heat_pump_installation'],
    '33200': ['heat_pump_installation', 'f_gas_refrigeration'],

    # --- EV ---
    '43320': ['ev_chargepoint_installation'],
    '45320': ['ev_chargepoint_installation'],

    # --- Plumbing / Heating ---
    '43220': ['heat_pump_installation'],
    '43390': ['heat_pump_installation'],

    # --- General Building / Retrofit ---
    '41200': ['retrofit_assessment'],
    '43399': ['retrofit_assessment'],

    # --- Electronics Repair ---
    '95210': ['electronics_repair'],
    '95220': ['electronics_repair'],
    '95290': ['electronics_repair'],

    # --- Computer Repair ---
    '95110': ['electronics_repair'],

    # --- Appliance Repair ---
    '95220': ['electronics_repair'],
}

# SIC code descriptions for reference
SIC_DESCRIPTIONS = {
    '43210': 'Electrical installation',
    '43220': 'Plumbing, heat and air-conditioning installation',
    '43290': 'Other construction installation',
    '43310': 'Plastering',
    '43320': 'Joinery installation',
    '43330': 'Floor and wall tiling',
    '43340': 'Painting',
    '43390': 'Other building completion and finishing',
    '43399': 'Other building completion and finishing n.e.c.',
    '43999': 'Other construction installation n.e.c.',
    '41200': 'Construction of residential and non-residential buildings',
    '45320': 'Retail sale of motor vehicle parts and accessories',
    '33200': 'Reassembly of prefabricated structures',
    '95110': 'Repair and maintenance of computers and peripheral equipment',
    '95210': 'Repair and maintenance of consumer electronics',
    '95220': 'Repair and maintenance of household appliances and home and garden equipment',
    '95290': 'Repair and maintenance of other personal and household goods',
}

# Device category → Capability mapping (for Open Repair data)
REPAIR_ITEM_TO_CAPABILITY = {
    'telephone': ['electronics_repair'],
    'smartphone': ['electronics_repair'],
    'laptop': ['electronics_repair'],
    'computer': ['electronics_repair'],
    'tablet': ['electronics_repair'],
    'monitor': ['electronics_repair'],
    'printer': ['electronics_repair'],
    'camera': ['electronics_repair'],
    'headphones': ['electronics_repair'],
    'speaker': ['electronics_repair'],
    'router': ['electronics_repair'],
    'game_console': ['electronics_repair'],
    'tv': ['electronics_repair'],
    'microwave': ['electronics_repair'],
    'washing_machine': ['electronics_repair'],
    'dishwasher': ['electronics_repair'],
    'fridge': ['electronics_repair'],
    'vacuum': ['electronics_repair'],
    'power_tool': ['electronics_repair'],
    'drill': ['electronics_repair'],
    'solar_panel': ['solar_pv_installation'],
    'inverter': ['solar_pv_installation'],
    'battery': ['battery_storage_installation'],
    'ev_charger': ['ev_chargepoint_installation'],
    'heat_pump': ['heat_pump_installation'],
}


def sic_to_capabilities(sic_codes: list) -> list:
    """Map SIC codes to capability IDs."""
    caps = set()
    for sic in sic_codes:
        if sic in SIC_TO_CAPABILITY:
            caps.update(SIC_TO_CAPABILITY[sic])
    return list(caps)


def item_type_to_capability(item_type: str) -> list:
    """Map Open Repair item_type to capability IDs."""
    item_lower = item_type.lower().strip()
    for key, caps in REPAIR_ITEM_TO_CAPABILITY.items():
        if key in item_lower:
            return caps
    return ['electronics_repair']  # default
