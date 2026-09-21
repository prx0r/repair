"""Companies House Collector — proper implementation with API key.

Searches for repair/electronics businesses and fetches full profiles.
Uses HTTP basic auth: API key as username, blank password.
Rate limit: 600 requests per 5 minutes.
"""

import os
import sys
import json
import time
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY', 'd284d51e-b98b-4517-861d-0f8b2273ceeb')
API_BASE = 'https://api.company-information.service.gov.uk'
DB_PATH = Path(__file__).parent.parent / 'warehouse' / 'repair.db'

# Search terms mapped to repair garden domains
SEARCH_QUERIES = [
    # Electronics repair
    ('electronics repair', 'electronics_repair'),
    ('phone repair', 'phone_repair'),
    ('laptop repair', 'laptop_repair'),
    ('computer repair', 'computer_repair'),
    ('tablet repair', 'tablet_repair'),
    ('camera repair', 'camera_repair'),

    # Power tools
    ('power tool repair', 'power_tool_repair'),
    ('tool hire', 'tool_hire'),

    # Solar / Energy
    ('solar panel installation', 'solar_installation'),
    ('solar energy', 'solar_energy'),
    ('heat pump', 'heat_pump'),
    ('battery storage', 'battery_storage'),
    ('ev charger installation', 'ev_charger'),

    # Robotics / Automation
    ('robot', 'robotics'),
    ('automation', 'automation'),
    ('3d printing', 'fabrication'),

    # Mining / Compute
    ('cryptocurrency mining', 'crypto_mining'),
    ('data centre', 'data_centre'),
    ('computer hardware', 'hardware'),

    # General repair / resale
    ('electrical contractor', 'electrical'),
    ('appliance repair', 'appliance_repair'),
    ('white goods repair', 'appliance_repair'),
    ('refurbished electronics', 'refurbishment'),
    ('used electronics', 'resale'),
]


def search_companies(query, items_per_page=20):
    """Search Companies House for companies matching a query."""
    try:
        resp = requests.get(
            f'{API_BASE}/search/companies',
            params={'q': query, 'items_per_page': items_per_page},
            auth=(API_KEY, ''),
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get('items', [])
        elif resp.status_code == 429:
            print(f'    Rate limited, waiting 60s...')
            time.sleep(60)
            return search_companies(query, items_per_page)
        else:
            print(f'    HTTP {resp.status_code}')
            return []
    except Exception as e:
        print(f'    Error: {e}')
        return []


def get_company_profile(company_number):
    """Get full company profile."""
    try:
        resp = requests.get(
            f'{API_BASE}/company/{company_number}',
            auth=(API_KEY, ''),
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except:
        return None


def get_company_officers(company_number):
    """Get company officers."""
    try:
        resp = requests.get(
            f'{API_BASE}/company/{company_number}/officers',
            auth=(API_KEY, ''),
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get('items', [])
        return []
    except:
        return []


def store_company(conn, company_data, query_category):
    """Store a company in SQLite."""
    try:
        conn.execute(
            'INSERT OR IGNORE INTO observations (source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                'companies_house',
                company_data.get('company_number', ''),
                'company_profile',
                json.dumps({
                    'name': company_data.get('company_name', ''),
                    'status': company_data.get('company_status', ''),
                    'type': company_data.get('type', ''),
                    'sic_codes': company_data.get('sic_codes', []),
                    'address': company_data.get('registered_office_address', {}),
                    'created': company_data.get('date_of_creation', ''),
                    'category': query_category,
                }, default=str),
                'json',
                json.dumps(company_data, default=str),
                datetime.now().isoformat(),
            )
        )
        return True
    except Exception as e:
        print(f'    Store error: {e}')
        return False


def main():
    print('Companies House Collector')
    print(f'API Key: {API_KEY[:8]}...')
    print(f'Database: {DB_PATH}')
    print('=' * 60)

    conn = sqlite3.connect(str(DB_PATH))

    total_companies = 0
    total_profiles = 0

    for query, category in SEARCH_QUERIES:
        print(f'\n  [{category}] Searching: "{query}"...')
        companies = search_companies(query, items_per_page=20)
        print(f'    Found {len(companies)} companies')

        for company in companies:
            company_number = company.get('company_number', '')
            if not company_number:
                continue

            # Store search result
            store_company(conn, company, category)
            total_companies += 1

            # Get full profile (rate limit: 1 per second)
            time.sleep(1.1)
            profile = get_company_profile(company_number)
            if profile:
                store_company(conn, profile, category)
                total_profiles += 1

            # Get officers (rate limit: 1 per second)
            time.sleep(1.1)
            officers = get_company_officers(company_number)
            if officers:
                for officer in officers[:5]:  # limit to 5 per company
                    try:
                        conn.execute(
                            'INSERT OR IGNORE INTO observations (source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
                            'VALUES (?, ?, ?, ?, ?, ?, ?)',
                            (
                                'companies_house',
                                company_number,
                                'officer',
                                json.dumps({
                                    'name': officer.get('name', ''),
                                    'role': officer.get('officer_role', ''),
                                    'appointed': officer.get('appointed_on', ''),
                                    'category': category,
                                }, default=str),
                                'json',
                                json.dumps(officer, default=str),
                                datetime.now().isoformat(),
                            )
                        )
                    except:
                        pass

        conn.commit()
        print(f'    Total so far: {total_companies} companies, {total_profiles} profiles')

    conn.commit()

    print(f'\n{"=" * 60}')
    print(f'Final: {total_companies} companies, {total_profiles} profiles')

    # Summary
    sources = conn.execute(
        'SELECT source_id, COUNT(*) FROM observations WHERE source_id="companies_house" GROUP BY source_id'
    ).fetchall()
    for s in sources:
        print(f'  {s[0]}: {s[1]} rows')

    conn.close()


if __name__ == '__main__':
    main()
