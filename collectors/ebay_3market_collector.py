"""eBay 3-Market Collector — tracks broken, working, and parts markets separately.

Priority universe: GPUs, consoles, laptops, PC hardware, PSUs, miners, homelab.
Each search term specifies condition via eBay filter keywords.
"""

import os
import re
import json
import time
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

DB = Path(__file__).parent.parent / 'warehouse' / 'repair.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

# Priority universe × 3 market segments
SEARCH_PANEL = {
    # --- GPUs ---
    'rtx 4090': {'domain': 'gpu', 'tier': 1},
    'rtx 3090': {'domain': 'gpu', 'tier': 1},
    'rtx 3080': {'domain': 'gpu', 'tier': 1},
    'rtx 4080': {'domain': 'gpu', 'tier': 1},
    'rx 7900 xtx': {'domain': 'gpu', 'tier': 2},
    'a100': {'domain': 'gpu', 'tier': 2},

    # --- Laptops ---
    'macbook pro m3': {'domain': 'laptop', 'tier': 1},
    'macbook pro m2': {'domain': 'laptop', 'tier': 1},
    'macbook air m2': {'domain': 'laptop', 'tier': 1},
    'thinkpad x1 carbon': {'domain': 'laptop', 'tier': 2},
    'dell xps 15': {'domain': 'laptop', 'tier': 2},

    # --- Consoles ---
    'playstation 5': {'domain': 'console', 'tier': 1},
    'xbox series x': {'domain': 'console', 'tier': 1},
    'nintendo switch oled': {'domain': 'console', 'tier': 1},
    'steam deck': {'domain': 'console', 'tier': 1},

    # --- Crypto miners ---
    'antminer s19': {'domain': 'miner', 'tier': 1},
    'antminer s21': {'domain': 'miner', 'tier': 1},
    'whatsminer m50': {'domain': 'miner', 'tier': 2},
    'antminer l7': {'domain': 'miner', 'tier': 2},

    # --- Power tools ---
    'makita 18v': {'domain': 'power_tool', 'tier': 1},
    'bosch 18v': {'domain': 'power_tool', 'tier': 1},
    'dewalt 20v': {'domain': 'power_tool', 'tier': 1},
    'milwaukee m18': {'domain': 'power_tool', 'tier': 1},

    # --- Homelab / Server ---
    'synology nas': {'domain': 'homelab', 'tier': 2},
    'ubiquiti': {'domain': 'homelab', 'tier': 2},
    'raspberry pi 5': {'domain': 'homelab', 'tier': 2},

    # --- Camera / Drone ---
    'gopro hero 12': {'domain': 'camera', 'tier': 2},
    'dji mini 4': {'domain': 'camera', 'tier': 2},
    'sony a7 iv': {'domain': 'camera', 'tier': 2},
}

# Condition keywords to separate markets
CONDITIONS = {
    'broken': ['for parts', 'not working', 'faulty', 'spares', 'as is', 'broken', 'damaged', 'broken screen'],
    'working': [],  # no condition keyword = general used
    'parts': ['parts only', 'for spares', 'board only', 'motherboard only', 'gpu only'],
}


def search_ebay(query, condition_filter=None, max_results=25):
    """Search eBay UK. condition_filter: 'broken', 'working', or 'parts'."""
    search_term = query
    if condition_filter and condition_filter in CONDITIONS:
        keywords = CONDITIONS[condition_filter]
        if keywords:
            search_term = f"{query} {keywords[0]}"

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.get('https://www.ebay.co.uk', timeout=10)
        time.sleep(1)
        resp = session.get('https://www.ebay.co.uk/sch/i.html', params={
            '_nkw': search_term, '_sop': 15, '_ipg': min(max_results, 120),
        }, timeout=20)
        if resp.status_code != 200:
            return []

        html = resp.text
        titles = re.findall(r'class="s-item__title"[^>]*>([^<]+)</span>', html)
        prices = re.findall(r'class="s-item__price"[^>]*>[^£]*£([0-9,.]+)', html)

        items = []
        for i in range(min(len(titles), len(prices))):
            title = titles[i]
            if 'Shop on' in title or 'Results' in title:
                continue
            try:
                price = float(prices[i].replace(',', ''))
            except:
                continue
            items.append({'title': title, 'price': price, 'search_term': search_term})
        return items
    except:
        return []


def store_obs(conn, source, entity, metric, value_dict, raw=None):
    """Insert observation into SQLite."""
    try:
        conn.execute(
            'INSERT OR IGNORE INTO observations '
            '(source_id, entity_id, metric, value, value_type, raw_json, observed_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (source, entity, metric, json.dumps(value_dict, default=str),
             'json', json.dumps(raw or value_dict, default=str), datetime.now().isoformat())
        )
        return True
    except:
        return False


def run():
    print('eBay 3-Market Collector')
    print(f'Priority universe: {len(SEARCH_PANEL)} devices')
    print('=' * 60)

    conn = sqlite3.connect(str(DB))
    total = 0

    for search_term, meta in SEARCH_PANEL.items():
        domain = meta['domain']
        tier = meta['tier']

        for condition in ['broken', 'working', 'parts']:
            print(f'  [{condition:8s}] {search_term}...', end=' ')
            items = search_ebay(search_term, condition_filter=condition, max_results=15)
            count = 0
            for item in items:
                store_obs(conn, 'ebay_3market', f"{domain}:{search_term}", 'listing',
                    {'title': item['title'], 'price': item['price'], 'condition': condition,
                     'domain': domain, 'tier': tier, 'search': search_term, 'currency': 'GBP'},
                    item)
                count += 1
            total += count
            print(f'{count} items')
            time.sleep(2)

        conn.commit()

    conn.commit()
    print(f'\nTotal: {total} listings across {len(SEARCH_PANEL)} devices × 3 markets')
    conn.close()


if __name__ == '__main__':
    run()
