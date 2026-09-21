"""Source Registry — machine-readable source definitions."""

SOURCES = [
    {
        'id': 'open_repair',
        'domain': 'repair_failure',
        'name': 'Open Repair Alliance',
        'status': 'backfilling',
        'cadence': 'weekly',
        'url': 'https://raw.githubusercontent.com/openrepair/data/master/aggregated/202507/OpenRepairData_v0.3_aggregate_202507.csv',
    },
    {
        'id': 'opss_recalls',
        'domain': 'safety',
        'name': 'UK OPSS Product Recalls',
        'status': 'backfilling',
        'cadence': 'daily',
        'url': 'https://www.gov.uk/guidance/product-recalls-and-alerts',
    },
    {
        'id': 'ebay_3market',
        'domain': 'market_tape',
        'name': 'eBay UK 3-Market',
        'status': 'blocked_vps',
        'cadence': '6-hourly',
    },
    {
        'id': 'planning_data',
        'domain': 'demand',
        'name': 'UK Planning Applications',
        'status': 'working',
        'cadence': 'daily',
    },
    {
        'id': 'octopus',
        'domain': 'energy_prices',
        'name': 'Octopus Energy',
        'status': 'working',
        'cadence': 'daily',
    },
    {
        'id': 'openalex',
        'domain': 'research',
        'name': 'OpenAlex',
        'status': 'working',
        'cadence': 'weekly',
    },
    {
        'id': 'companies_house',
        'domain': 'businesses',
        'name': 'Companies House',
        'status': 'working',
        'cadence': 'daily',
    },
]
