"""Screwfix/Toolstation Collector — UK trade pricing for power tools and electrical.

These are the UK's primary trade suppliers. Prices here = real installed cost.
"""

import json
import re
import time
import requests
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record

# Trade product categories
TRADE_CATEGORIES = {
    'power_tools': ['makita drill', 'bosch drill', 'dewalt drill', 'milwaukee drill',
                    'makita saw', 'angle grinder', 'circular saw', 'jigsaw'],
    'electrical': ['consumer unit', 'rcbo', 'mcb', 'mcbo', 'contactor',
                   'switch socket', 'light switch', 'junction box'],
    'ev_charging': ['ev charger', 'tethered ev cable', 'untethered ev cable',
                    'ev consumer unit', 'commando socket'],
    'solar': ['solar panel', 'solar inverter', 'mppt controller',
              'battery storage', 'solar cable'],
    'heating': ['heat pump', 'oil radiator', 'electric heater', 'storage heater'],
}

SITES = {
    'screwfix': 'https://www.screwfix.com',
    'toolstation': 'https://www.toolstation.com',
}


class ScrewfixToolstationCollector(BaseCollector):
    SOURCE_ID = 'trade_pricing'
    DATASET = 'uk_trade'
    PARSER_ID = 'trade_web_v1'

    def fetch(self):
        """Fetch trade pricing from Screwfix and Toolstation."""
        all_items = []
        for site_name, site_url in SITES.items():
            for category, queries in TRADE_CATEGORIES.items():
                for query in queries[:2]:  # limit to 2 per category
                    items = self._search_site(site_name, site_url, query, category)
                    all_items.extend(items)
                    time.sleep(2)
        return json.dumps(all_items).encode()

    def _search_site(self, site_name, site_url, query, category):
        """Search a trade site."""
        try:
            search_url = f'{site_url}/search?search={query.replace(" ", "+")}'
            resp = self._fetch_url(search_url, timeout=15)
            if resp and resp.status_code == 200:
                html = resp.text
                items = []
                # Extract JSON-LD product data
                json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
                for block in json_ld:
                    try:
                        data = json.loads(block)
                        if isinstance(data, dict) and data.get('@type') == 'Product':
                            offers = data.get('offers', {})
                            items.append({
                                'name': data.get('name', ''),
                                'price': float(offers.get('price', 0)),
                                'currency': offers.get('priceCurrency', 'GBP'),
                                'availability': offers.get('availability', ''),
                                'brand': data.get('brand', {}).get('name', ''),
                                'category': category,
                                'site': site_name,
                                'url': data.get('url', ''),
                            })
                    except:
                        pass
                return items
        except Exception as e:
            print(f'    {site_name} error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash):
        result = CollectorResult()
        items = json.loads(raw_content)
        for item in items:
            native_id = f"{item.get('site', '')}_{item.get('name', '')}_{item.get('price', 0)}"
            normalized = {
                'source_native_id': native_id,
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'currency': item.get('currency', 'GBP'),
                'availability': item.get('availability', ''),
                'brand': item.get('brand', ''),
                'category': item.get('category', ''),
                'site': item.get('site', ''),
                'url': item.get('url', ''),
            }
            ir = insert_source_record(
                self.SOURCE_ID, self.DATASET, native_id,
                normalized, raw_hash, self.PARSER_ID, self.PARSER_VERSION
            )
            if ir.inserted:
                result.records_new += 1
            else:
                result.records_unchanged += 1
        return result


if __name__ == '__main__':
    ScrewfixToolstationCollector().run()
