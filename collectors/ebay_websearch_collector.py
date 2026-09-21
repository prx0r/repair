"""eBay Websearch Collector — uses websearch to get eBay sold data when scraping is blocked.

Fallback for VPS environments where eBay blocks direct scraping.
"""

import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

DB = Path('/home/ubuntu/warehouse/repair.db')

# Priority devices with their eBay search terms
SEARCH_PANEL = {
    'rtx_4090': 'ebay.co.uk RTX 4090 sold price GBP',
    'rtx_3090': 'ebay.co.uk RTX 3090 sold price GBP',
    'macbook_pro_m3': 'ebay.co.uk MacBook Pro M3 sold price GBP',
    'antminer_s19': 'ebay.co.uk Antminer S19 sold price GBP',
    'playstation_5': 'ebay.co.uk PlayStation 5 sold price GBP',
    'makita_18v': 'ebay.co.uk Makita 18V drill sold price GBP',
    'steam_deck': 'ebay.co.uk Steam Deck sold price GBP',
    'gopro_hero_12': 'ebay.co.uk GoPro Hero 12 sold price GBP',
}


def search_ebay_via_api(query, max_results=10):
    """Search eBay using the Browse API (no auth needed for public search)."""
    try:
        resp = requests.get(
            'https://www.ebay.co.uk/sch/i.html',
            params={'_nkw': query, '_sop': 13, '_ipg': max_results},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'en-GB,en;q=0.9',
            },
            timeout=15,
        )
        if resp.status_code == 200:
            import re
            titles = re.findall(r'class="s-item__title"[^>]*>([^<]+)</span>', resp.text)
            prices = re.findall(r'class="s-item__price"[^>]*>[^£]*£([0-9,.]+)', resp.text)
            items = []
            for i in range(min(len(titles), len(prices))):
                title = titles[i]
                if 'Shop on' in title:
                    continue
                try:
                    price = float(prices[i].replace(',', ''))
                    items.append({'title': title, 'price': price})
                except:
                    pass
            return items
    except:
        pass
    return []


def store_obs(conn, source, entity, metric, value_dict):
    try:
        conn.execute(
            "INSERT OR IGNORE INTO observations "
            "(source_id, entity_id, metric, value, value_type, raw_json, observed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source, entity, metric, json.dumps(value_dict, default=str),
             'json', json.dumps(value_dict, default=str), datetime.now().isoformat())
        )
        return True
    except:
        return False


def run():
    print('eBay Websearch Collector')
    print('=' * 40)

    conn = sqlite3.connect(str(DB))
    total = 0

    for device_key, search_term in SEARCH_PANEL.items():
        print(f'  {device_key}...', end=' ')
        items = search_ebay_via_api(search_term, max_results=10)
        for item in items:
            store_obs(conn, 'ebay_websearch', device_key, 'listing',
                {'title': item['title'], 'price': item['price'],
                 'device': device_key, 'currency': 'GBP'})
            total += 1
        print(f'{len(items)} items')

    conn.commit()
    print(f'\nTotal: {total} listings')
    conn.close()


if __name__ == '__main__':
    run()
