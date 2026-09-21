"""Open Repair Alliance — historical dataset collector.

Downloads the complete CSV from GitHub.
Uses shared persistence functions. Idempotent.
"""

import csv
import gzip
import io
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record


class OpenRepairCollector(BaseCollector):
    SOURCE_ID = 'open_repair'
    DATASET = 'open_repair_complete'
    PARSER_ID = 'open_repair_csv_v1'

    DATA_URL = 'https://raw.githubusercontent.com/openrepair/data/master/aggregated/202507/OpenRepairData_v0.3_aggregate_202507.csv'

    def fetch(self):
        acq = self._fetch_url(self.DATA_URL, timeout=120)
        if acq and acq.status == 200:
            return acq.content
        return None

    def parse(self, raw_content, raw_hash, result):
        """Parse Open Repair CSV. Mutates result — does not return a new one."""
        try:
            content = gzip.decompress(raw_content).decode('utf-8', errors='replace')
        except:
            content = raw_content.decode('utf-8', errors='replace')

        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            native_id = row.get('id', '')
            if not native_id:
                result.records_invalid += 1
                continue

            normalized = {
                'source_native_id': native_id,
                'event_date': row.get('event_date', ''),
                'country': row.get('country', ''),
                'product_category': row.get('product_category', ''),
                'product_category_id': row.get('product_category_id', ''),
                'brand': row.get('brand', ''),
                'model': row.get('model', ''),
                'problem': row.get('problem', ''),
                'repair_status': row.get('repair_status', ''),
                'repair_barrier': row.get('repair_barrier', ''),
                'data_provider': row.get('data_provider', ''),
                'group_identifier': row.get('group_identifier', ''),
                'estimated_product_age': row.get('estimated_product_age', ''),
            }

            ir = insert_source_record(
                self.SOURCE_ID, self.DATASET, native_id,
                normalized, raw_hash, self.PARSER_ID, self.PARSER_VERSION
            )

            if ir.inserted:
                if ir.duplicate_of:
                    result.records_changed += 1
                else:
                    result.records_new += 1
            else:
                result.records_unchanged += 1


if __name__ == '__main__':
    OpenRepairCollector().run()
