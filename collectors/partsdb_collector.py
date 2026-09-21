"""PartsDB.io Collector — free component data (100 requests/day).

European electronics distributor data with pricing.
"""

import json
import os
import time
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record

# Electronics baseline cohort — NOT repair-derived yet.
# This is a control group of common components for price tracking.
# A true repair-derived cohort would come from: device → fault → failed component → MPN.
MPN_BASELINE = [
    'STM32F407VGT6', 'STM32F103C8T6', 'ATmega328P',
    'ESP32-WROOM-32', 'ESP32-S3-WROOM-1',
    'RP2040', 'nRF52840',
    'LM7805', 'LM317', 'AMS1117-3.3',
    'NE555', 'LM358', 'TL072',
    '2N2222', 'IRF540N', 'IRFZ44N',
    '1N4148', '1N4007', 'BZX84C5V1',
    '0805 100nF', '0805 10uF', '0805 1k',
]

HEADERS = {
    'User-Agent': 'RepairGarden/1.0',
    'Accept': 'application/json',
}


class PartsDBCollector(BaseCollector):
    SOURCE_ID = 'partsdb'
    DATASET = 'eu_components'
    PARSER_ID = 'partsdb_api_v1'

    API_BASE = 'https://api.partsdb.io/v1'

    def __init__(self, api_key=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get('PARTSDB_API_KEY', '')

    def fetch(self):
        """Fetch component data for MPN cohort."""
        all_items = []
        for mpn in MPN_BASELINE:
            items = self._search_mpn(mpn)
            all_items.extend(items)
            time.sleep(1)
        return json.dumps(all_items).encode()

    def _search_mpn(self, mpn):
        """Search for a specific MPN."""
        try:
            url = f'{self.API_BASE}/search?q={mpn}&limit=5'
            self._last_url = url
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            resp = self._fetch_url(url, timeout=15)
            if resp and resp.status_code == 200:
                self._last_status = resp.status_code
                self._last_final_url = str(resp.url)
                self._last_content_type = resp.headers.get('content-type', '')
                data = resp.json()
                return data.get('results', [])
        except Exception as e:
            print(f'    PartsDB error for {mpn}: {e}')
        return []

    def parse(self, raw_content, raw_hash, result):
        """Parse PartsDB items. Mutates result — does not return a new one."""
        items = json.loads(raw_content)
        for item in items:
            native_id = item.get('mpn', '') or item.get('id', '')
            if not native_id:
                result.records_invalid += 1
                continue
            normalized = {
                'source_native_id': native_id,
                'mpn': item.get('mpn', ''),
                'manufacturer': item.get('manufacturer', ''),
                'description': item.get('description', ''),
                'price_eur': item.get('price'),  # None, not 0
                'stock': item.get('stock'),  # None, not 0
                'lifecycle': item.get('lifecycle', ''),
                'category': item.get('category', ''),
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
    PartsDBCollector().run()
