"""Screwfix/Toolstation Collector — UK trade pricing for power tools and electrical.

These are the UK's primary trade suppliers. Prices here = real installed cost.
Narrowed to repair-relevant goods: batteries, motors, switches, tools.
"""

import json
import re
import time
import requests
from datetime import datetime, timezone
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record, store_market_observation

# Trade product categories — narrowed to repair-relevant
TRADE_CATEGORIES = {
    'power_tools': ['makita drill', 'bosch drill', 'dewalt drill', 'milwaukee drill',
                    'angle grinder', 'circular saw', 'jigsaw'],
    'batteries': ['makita battery', 'bosch battery', 'dewalt battery', 'milwaukee battery',
                  '18v li-ion battery', 'power tool battery charger'],
    'motors': ['universal motor', 'brush motor', 'replacement motor', 'fan motor'],
    'electrical': ['rcbo', 'mcb', 'contactor', 'switch socket', 'light switch',
                   'junction box', 'wago connector'],
    'consumables': ['saw blade', 'grinding disc', 'drill bit set', 'solder',
                    'heat shrink', 'cable tie', ' electrical tape'],
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
            acq = self._fetch_url(search_url, timeout=15)
            if acq and acq.status == 200:
                html = acq.content.decode('utf-8', errors='replace')
                items = []
                json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
                for block in json_ld:
                    try:
                        data = json.loads(block)
                        if isinstance(data, dict) and data.get('@type') == 'Product':
                            offers = data.get('offers', {})
                            # Extract product code from URL or data
                            url_val = data.get('url', '')
                            # Screwfix URLs end with product code: /p/xxx_123
                            code_match = re.search(r'/p/(\w+)', url_val) if url_val else None
                            product_code = code_match.group(1) if code_match else ''
                            items.append({
                                'product_code': product_code,
                                'name': data.get('name', ''),
                                'price': float(offers.get('price', 0)) if offers.get('price') else None,
                                'currency': offers.get('priceCurrency', 'GBP'),
                                'availability': offers.get('availability', ''),
                                'brand': data.get('brand', {}).get('name', ''),
                                'category': category,
                                'site': site_name,
                                'url': url_val,
                            })
                    except:
                        pass
                return items
        except Exception as e:
            print(f'    {site_name} error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash, result):
        """Parse trade items. Mutates result — does not return a new one."""
        items = json.loads(raw_content)
        for item in items:
            # Stable identity: product_code + site (no price in identity)
            product_code = item.get('product_code', '')
            site = item.get('site', '')
            native_id = f"{site}:{product_code}" if product_code else item.get('name', '')
            if not native_id:
                result.records_invalid += 1
                continue

            normalized = {
                'source_native_id': native_id,
                'product_code': product_code,
                'name': item.get('name', ''),
                'price': item.get('price'),
                'currency': item.get('currency', 'GBP'),
                'availability': item.get('availability', ''),
                'brand': item.get('brand', ''),
                'category': item.get('category', ''),
                'site': site,
                'url': item.get('url', ''),
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

            # Always store market observation
            price = item.get('price')
            if price is not None:
                store_market_observation(
                    source_record_id=ir.record_id,
                    observed_at=datetime.now(timezone.utc).isoformat(),
                    price=price,
                    currency=item.get('currency', 'GBP'),
                    availability=item.get('availability', ''),
                    market=site,
                )


if __name__ == '__main__':
    ScrewfixToolstationCollector().run()
