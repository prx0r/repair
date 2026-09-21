"""CeX UK Collector — buy/sell prices for used electronics.

CeX is the UK's biggest used electronics dealer.
They publish buy and sell prices for phones, laptops, consoles, GPUs.
This is the UK's most important secondary market price signal.
"""

import json
import re
import time
import requests
from datetime import datetime, timezone
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record, store_market_observation

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
            acq = self._fetch_url(url, timeout=15)
            if acq and acq.status == 200:
                data = json.loads(acq.content)
                items = data.get('response', {}).get('data', {}).get('boxes', [])
                results = []
                for item in items:
                    results.append({
                        'box_id': item.get('boxId', ''),
                        'category_id': item.get('categoryId', ''),
                        'ean': item.get('ean', ''),
                        'name': item.get('boxName', ''),
                        'sell_price': item.get('sellPrice', None),
                        'buy_price': item.get('buyPrice', None),
                        'exchange_price': item.get('exchangePrice', None),
                        'category': category,
                        'ceiling': item.get('ceilingPrice', None),
                        'boxed': item.get('boxed', False),
                        'grade': item.get('gradeName', ''),
                    })
                return results
        except Exception as e:
            print(f'    CeX error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash, result):
        """Parse CeX items. Mutates result — does not return a new one."""
        items = json.loads(raw_content)
        for item in items:
            # Stable identity: box_id is the CeX-native product identifier
            native_id = str(item.get('box_id', ''))
            if not native_id:
                # Fallback: name only (no price in identity)
                native_id = item.get('name', '')
            if not native_id:
                result.records_invalid += 1
                continue

            normalized = {
                'source_native_id': native_id,
                'box_id': item.get('box_id', ''),
                'category_id': item.get('category_id', ''),
                'ean': item.get('ean', ''),
                'name': item.get('name', ''),
                'sell_price': item.get('sell_price'),
                'buy_price': item.get('buy_price'),
                'exchange_price': item.get('exchange_price'),
                'category': item.get('category', ''),
                'ceiling_price': item.get('ceiling'),
                'boxed': item.get('boxed', False),
                'grade': item.get('grade', ''),
                'currency': 'GBP',
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

            # Always store market observation (even when unchanged)
            # CeX gives us 3 prices: sell (ask), buy (bid), exchange
            sell_price = item.get('sell_price')
            buy_price = item.get('buy_price')
            exchange_price = item.get('exchange_price')
            if sell_price is not None or buy_price is not None:
                store_market_observation(
                    source_record_id=ir.record_id,
                    observed_at=datetime.now(timezone.utc).isoformat(),
                    price=float(sell_price) if sell_price is not None else None,
                    bid_price=float(buy_price) if buy_price is not None else None,
                    exchange_price=float(exchange_price) if exchange_price is not None else None,
                    currency='GBP',
                    condition=item.get('grade', ''),
                    market='cex',
                    observation_type='cex_quote',
                    source_native_id=native_id,
                )


if __name__ == '__main__':
    CexCollector().run()
