"""Entity Resolver — links providers to companies across systems.

Competent Person Register ↔ Companies House ↔ MCS ↔ OZEV

Uses name + postcode + company_number for matching.

NOTE: This module still references the legacy `observations` table.
It needs rewriting to use source_record via shared/persist.py.
For now, fix imports and paths so it doesn't crash.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.db import get_db


class EntityResolver:
    """Resolves providers across multiple data sources."""

    def _conn(self):
        return get_db()

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

        # Search Companies House (via source_record, not legacy observations)
        if company_number:
            row = conn.execute(
                "SELECT normalized_json FROM source_record WHERE source_id='companies_house' "
                "AND source_native_id=? AND valid=1 LIMIT 1",
                (company_number,)
            ).fetchone()
            if row:
                try:
                    data = json.loads(row[0])
                    results['matches']['companies_house'] = {
                        'name': data.get('name'),
                        'status': data.get('status'),
                        'sic_codes': data.get('sic', []),
                        'created': data.get('created'),
                    }
                    results['confidence'] = max(results['confidence'], 0.9)
                except:
                    pass

        conn.close()
        return results
