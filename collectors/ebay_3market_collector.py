"""eBay 3-Market Collector — tracks broken, working, and parts markets separately.

Priority universe: GPUs, consoles, laptops, PC hardware, PSUs, miners, homelab.
Each search term specifies condition via eBay filter keywords.

Uses BaseCollector contract. Identity is stable (no price in native_id).
"""

import json
import os
import re
import time
import requests
from datetime import datetime, timezone
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record, store_market_observation

# Priority universe × 3 market segments
SEARCH_PANEL = {
    # --- GPUs ---
    'rtx 4090': {'domain': 'gpu', 'tier': 1, 'model': 'RTX 4090'},
    'rtx 3090': {'domain': 'gpu', 'tier': 1, 'model': 'RTX 3090'},
    'rtx 3080': {'domain': 'gpu', 'tier': 1, 'model': 'RTX 3080'},
    'rtx 4080': {'domain': 'gpu', 'tier': 1, 'model': 'RTX 4080'},
    'rx 7900 xtx': {'domain': 'gpu', 'tier': 2, 'model': 'RX 7900 XTX'},
    'a100': {'domain': 'gpu', 'tier': 2, 'model': 'A100'},

    # --- Laptops ---
    'macbook pro m3': {'domain': 'laptop', 'tier': 1, 'model': 'MacBook Pro M3'},
    'macbook pro m2': {'domain': 'laptop', 'tier': 1, 'model': 'MacBook Pro M2'},
    'macbook air m2': {'domain': 'laptop', 'tier': 1, 'model': 'MacBook Air M2'},
    'thinkpad x1 carbon': {'domain': 'laptop', 'tier': 2, 'model': 'ThinkPad X1 Carbon'},
    'dell xps 15': {'domain': 'laptop', 'tier': 2, 'model': 'Dell XPS 15'},

    # --- Consoles ---
    'playstation 5': {'domain': 'console', 'tier': 1, 'model': 'PS5'},
    'xbox series x': {'domain': 'console', 'tier': 1, 'model': 'Xbox Series X'},
    'nintendo switch oled': {'domain': 'console', 'tier': 1, 'model': 'Switch OLED'},
    'steam deck': {'domain': 'console', 'tier': 1, 'model': 'Steam Deck'},

    # --- Crypto miners ---
    'antminer s19': {'domain': 'miner', 'tier': 1, 'model': 'Antminer S19'},
    'antminer s21': {'domain': 'miner', 'tier': 1, 'model': 'Antminer S21'},
    'whatsminer m50': {'domain': 'miner', 'tier': 2, 'model': 'Whatsminer M50'},
    'antminer l7': {'domain': 'miner', 'tier': 2, 'model': 'Antminer L7'},

    # --- Power tools ---
    'makita 18v': {'domain': 'power_tool', 'tier': 1, 'model': 'Makita 18V'},
    'bosch 18v': {'domain': 'power_tool', 'tier': 1, 'model': 'Bosch 18V'},
    'dewalt 20v': {'domain': 'power_tool', 'tier': 1, 'model': 'DeWalt 20V'},
    'milwaukee m18': {'domain': 'power_tool', 'tier': 1, 'model': 'Milwaukee M18'},

    # --- Homelab / Server ---
    'synology nas': {'domain': 'homelab', 'tier': 2, 'model': 'Synology NAS'},
    'raspberry pi 5': {'domain': 'homelab', 'tier': 2, 'model': 'Raspberry Pi 5'},

    # --- Camera / Drone ---
    'gopro hero 12': {'domain': 'camera', 'tier': 2, 'model': 'GoPro Hero 12'},
    'dji mini 4': {'domain': 'camera', 'tier': 2, 'model': 'DJI Mini 4'},
    'sony a7 iv': {'domain': 'camera', 'tier': 2, 'model': 'Sony A7 IV'},
}

# Condition keywords to separate markets
CONDITIONS = {
    'broken': ['for parts', 'not working', 'faulty', 'spares', 'as is', 'broken', 'damaged'],
    'working': [],  # no condition keyword = general used
    'parts': ['parts only', 'for spares', 'board only', 'motherboard only', 'gpu only'],
}


class Ebay3MarketCollector(BaseCollector):
    SOURCE_ID = 'ebay_3market'
    DATASET = 'uk_3market'
    PARSER_ID = 'ebay_html_v1'

    def fetch(self):
        """Fetch eBay UK search results for all devices × conditions."""
        all_items = []
        for search_term, meta in SEARCH_PANEL.items():
            for condition in ['broken', 'working', 'parts']:
                items = self._search_ebay(search_term, condition, meta)
                all_items.extend(items)
                time.sleep(2)
        return json.dumps(all_items).encode()

    def _search_ebay(self, query, condition_filter, meta):
        """Search eBay UK for a product in a specific condition."""
        search_term = query
        if condition_filter and condition_filter in CONDITIONS:
            keywords = CONDITIONS[condition_filter]
            if keywords:
                search_term = f"{query} {keywords[0]}"

        try:
            url = f'https://www.ebay.co.uk/sch/i.html'
            self._last_url = url
            params = {
                '_nkw': search_term, '_sop': 15, '_ipg': 25,
            }
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
            session.get('https://www.ebay.co.uk', timeout=10)
            time.sleep(1)
            resp = session.get(url, params=params, timeout=20)

            self._last_status = resp.status_code
            self._last_final_url = str(resp.url)
            self._last_content_type = resp.headers.get('content-type', '')

            if resp.status_code != 200:
                return []

            html = resp.text
            titles = re.findall(r'class="s-item__title"[^>]*>([^<]+)</span>', html)
            prices = re.findall(r'class="s-item__price"[^>]*>[^£]*£([0-9,.]+)', html)
            item_ids = re.findall(r'data-item-id="(\d+)"', html)

            items = []
            for i in range(min(len(titles), len(prices))):
                title = titles[i]
                if 'Shop on' in title or 'Results' in title:
                    continue
                try:
                    price = float(prices[i].replace(',', ''))
                except:
                    continue

                item_id = item_ids[i] if i < len(item_ids) else ''

                items.append({
                    'ebay_item_id': item_id,
                    'title': title,
                    'price': price,
                    'condition': condition_filter,
                    'domain': meta['domain'],
                    'model': meta['model'],
                    'tier': meta['tier'],
                    'search_term': query,
                })
            return items
        except Exception as e:
            print(f'    eBay error for {query}/{condition_filter}: {e}')
        return []

    def parse(self, raw_content, raw_hash, result):
        """Parse eBay items. Mutates result — does not return a new one."""
        items = json.loads(raw_content)
        for item in items:
            # Stable identity: ebay_item_id only (condition is an attribute, not identity)
            ebay_id = item.get('ebay_item_id', '')
            condition = item.get('condition', '')
            native_id = f"ebay:{ebay_id}" if ebay_id else ''
            if not native_id:
                # Fallback: quarantine — don't silently collapse listings
                native_id = f"ebay:unknown:{item.get('title', '')[:40]}"
                result.records_invalid += 1
                continue

            normalized = {
                'source_native_id': native_id,
                'ebay_item_id': ebay_id,
                'title': item.get('title', ''),
                'price': item.get('price'),
                'condition': condition,
                'domain': item.get('domain', ''),
                'model': item.get('model', ''),
                'tier': item.get('tier', 0),
                'search_term': item.get('search_term', ''),
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

            # Always store market observation
            price = item.get('price')
            if price is not None:
                store_market_observation(
                    source_record_id=ir.record_id,
                    observed_at=datetime.now(timezone.utc).isoformat(),
                    price=float(price),
                    currency='GBP',
                    condition=condition,
                    market=f'ebay_{condition}',
                )


if __name__ == '__main__':
    Ebay3MarketCollector().run()
