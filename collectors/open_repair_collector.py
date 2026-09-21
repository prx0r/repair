"""Open Repair Alliance — historical dataset collector.

Downloads the complete CSV from GitHub.
Target: 300K+ records with full provenance.

What: Real repair attempts from community repair cafés across Europe.
Why: Empirical fault/success/failure data for electronics repair.
"""

import csv
import hashlib
import json
import gzip
import io
from .base import BaseCollector


class OpenRepairCollector(BaseCollector):
    SOURCE_ID = 'open_repair'
    DATASET = 'open_repair_complete'
    PARSER_ID = 'open_repair_csv_v1'

    DATA_URL = 'https://raw.githubusercontent.com/openrepair/data/master/aggregated/202507/OpenRepairData_v0.3_aggregate_202507.csv'

    def fetch(self):
        resp = self._fetch_url(self.DATA_URL, timeout=120)
        if resp and resp.status_code == 200:
            return resp.content
        return None

    def parse(self, raw_content, raw_hash):
        # Decompress if gzipped
        try:
            content = gzip.decompress(raw_content).decode('utf-8', errors='replace')
        except:
            content = raw_content.decode('utf-8', errors='replace')

        reader = csv.DictReader(io.StringIO(content))
        count = 0
        for row in reader:
            native_id = row.get('id', f'row_{count}')
            normalized = {
                'source_native_id': native_id,
                'event_date': row.get('event_date', ''),
                'country': row.get('country', ''),
                'product_category': row.get('product_category', ''),
                'brand': row.get('brand', ''),
                'model': row.get('model', ''),
                'problem': row.get('problem', ''),
                'repair_status': row.get('repair_status', ''),
                'repair_barrier': row.get('repair_barrier', ''),
                'data_provider': row.get('data_provider', ''),
                'group_identifier': row.get('group_identifier', ''),
            }
            if self._store_source_record(native_id, normalized, raw_hash):
                count += 1
        return count


if __name__ == '__main__':
    OpenRepairCollector().run()
