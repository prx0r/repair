"""CeX UK Collector — buy/sell prices for used electronics.

CeX is the UK's biggest used electronics dealer.
They publish buy and sell prices for phones, laptops, consoles, GPUs.
This is the UK's most important secondary market price signal.
"""

import json
import re
import time
import requests
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record

# CeX categories to track
CEX_CATEGORIES = {
    'phones': ['apple-iphones', 'samsung-galaxy-s', 'google-pixel'],
    'laptops': ['macbook-pro', 'macbook-air', 'thinkpad', 'dell-xps'],
    'consoles': ['playstation-5', 'xbox-series', 'nintendo-switch', 'steam-deck'],
    'gpus': ['nvidia-geforce-rtx-3090', 'nvidia-geforce-rtx-4090', 'nvidia-geforce-rtx-3080'],
    'power_tools': ['makita', 'bosch', 'dewalt', 'milwaukee'],
    'cameras': ['nikon-dslr', 'canon-dslr', 'sony-alpha', 'gopro'],
    'audio': ['sony-headphones', 'airpods', 'bose', 'jbl'],
    'tablets': ['ipad', 'samsung-galaxy-tab'],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'en-GB,en;q=0.9',
}


class CexCollector(BaseCollector):
    SOURCE_ID = 'cex'
    DATASET = 'uk_buy_sell'
    PARSER_ID = 'cex_web_v1'

    def fetch(self):
        """CeX doesn't have a public API, so we scrape the search pages."""
        # CeX search endpoint
        all_items = []
        for category, queries in CEX_CATEGORIES.items():
            for query in queries:
                items = self._search_cex(query, category)
                all_items.extend(items)
                time.sleep(1)
        return json.dumps(all_items).encode()

    def _search_cex(self, query, category):
        """Search CeX for a product."""
        try:
            url = f'https://wss2.cex.uk.webuy.io/v3/boxes?q={query}&firstRecord=1&count=10&sortBy=relevance&sortOrder=desc'
            resp = self._fetch_url(url, timeout=15)
            if resp and resp.status_code == 200:
                data = resp.json()
                items = data.get('response', {}).get('data', {}).get('boxes', [])
                results = []
                for item in items:
                    results.append({
                        'name': item.get('boxName', ''),
                        'sell_price': item.get('sellPrice', 0),
                        'buy_price': item.get('buyPrice', 0),
                        'exchange_price': item.get('exchangePrice', 0),
                        'category': category,
                        'ceiling': item.get('ceilingPrice', 0),
                        'boxed': item.get('boxed', False),
                    })
                return results
        except Exception as e:
            print(f'    CeX error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash):
        result = CollectorResult()
        items = json.loads(raw_content)
        for item in items:
            native_id = f"{item.get('name', '')}_{item.get('sell_price', 0)}"
            normalized = {
                'source_native_id': native_id,
                'name': item.get('name', ''),
                'sell_price': item.get('sell_price', 0),
                'buy_price': item.get('buy_price', 0),
                'exchange_price': item.get('exchange_price', 0),
                'category': item.get('category', ''),
                'ceiling_price': item.get('ceiling', 0),
                'boxed': item.get('boxed', False),
                'currency': 'GBP',
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
    CexCollector().run()
