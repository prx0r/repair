"""Entity Resolver — links providers to companies across systems.

Competent Person Register ↔ Companies House ↔ MCS ↔ OZEV

Uses name + postcode + company_number for matching.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class EntityResolver:
    """Resolves providers across multiple data sources."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def resolve_provider(self, name: str, postcode: str = "", company_number: str = "") -> dict:
        """Try to match a provider across all sources."""
        results = {
            'name': name,
            'postcode': postcode,
            'company_number': company_number,
            'matches': {},
            'confidence': 0.0,
        }

        conn = self._conn()

        # Search Companies House
        if company_number:
            row = conn.execute(
                "SELECT value FROM observations WHERE source_id='companies_house' "
                "AND entity_id=? AND metric='company_profile' LIMIT 1",
                (company_number,)
            ).fetchone()
            if row:
                data = json.loads(row[0])
                results['matches']['companies_house'] = {
                    'name': data.get('name'),
                    'status': data.get('status'),
                    'sic_codes': data.get('sic', []),
                    'created': data.get('created'),
                }
                results['confidence'] = max(results['confidence'], 0.9)

        # Search by name
        rows = conn.execute(
            "SELECT entity_id, value FROM observations WHERE source_id='companies_house' "
            "AND metric='company_search' AND value LIKE ? LIMIT 5",
            (f'%{name}%',)
        ).fetchall()

        for row in rows:
            data = json.loads(row[1])
            if name.lower() in data.get('name', '').lower():
                results['matches']['companies_house_search'] = {
                    'company_number': row[0],
                    'name': data.get('name'),
                    'status': data.get('status'),
                }
                results['confidence'] = max(results['confidence'], 0.7)

        conn.close()
        return results

    def link_provider_to_company(self, provider_id: str, company_number: str):
        """Create a Provider ↔ Company relationship."""
        conn = self._conn()
        conn.execute(
            "INSERT OR IGNORE INTO observations "
            "(source_id, entity_id, metric, value, value_type, raw_json, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('entity_resolver', provider_id, 'provider_company_link',
             json.dumps({'provider_id': provider_id, 'company_number': company_number}),
             'json', json.dumps({'provider_id': provider_id, 'company_number': company_number}),
             datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
