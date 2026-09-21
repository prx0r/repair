"""eBay UK Sold Collector — adapted from datagarden/collectors/ebay_free.py"""

import os
import re
import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'resale' / 'ebay_sold'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

DEFAULT_CATEGORIES = [
    'macbook pro', 'iphone', 'ipad', 'rtx 4090', 'rtx 3080',
    'nikon camera', 'makita drill', 'sony amplifier', 'dyson vacuum',
    'nintendo switch', 'esp32', 'raspberry pi', 'solar panel',
    'battery 18650', 'brushless motor', 'servo motor',
    'mppt controller', 'inverter',
]


def search_ebay_sold(query, max_results=50):
    url = 'https://www.ebay.co.uk/sch/i.html'
    params = {'_nkw': query, 'LH_Sold': 1, 'LH_Complete': 1, '_sop': 13, '_ipg': min(max_results, 240)}
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get('https://www.ebay.co.uk', timeout=15)
        time.sleep(1)
        resp = session.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            return []
        items = []
        html = resp.text
        titles = re.findall(r'class="s-item__title"[^>]*>([^<]+)</span>', html)
        prices = re.findall(r'class="s-item__price"[^>]*>[^£]*£([0-9,.]+)', html)
        dates = re.findall(r'class="POSITIVE"[^>]*>([^<]+)</span>', html)
        for i in range(min(len(titles), len(prices), max_results)):
            title = titles[i] if i < len(titles) else ''
            price_str = prices[i] if i < len(prices) else '0'
            sold_date = dates[i] if i < len(dates) else ''
            if 'Shop on' in title or 'Results' in title:
                continue
            try:
                price = float(price_str.replace(',', ''))
            except:
                price = 0
            items.append({'title': title, 'soldPrice': price, 'soldCurrency': 'GBP',
                          'soldDate': sold_date, 'keyword': query})
        return items
    except Exception as e:
        print(f"  Error: {e}")
        return []


def save_results(query, items):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"
    count = 0
    with open(filepath, 'a') as f:
        for item in items:
            record = {**item, 'collected_at': datetime.now().isoformat(), 'source': 'ebay_public_search',
                      'itemId': f"free_{hash(item['title'] + str(item['soldPrice']))}"}
            f.write(json.dumps(record) + '\n')
            count += 1
    return count


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str)
    parser.add_argument('--count', type=int, default=50)
    args = parser.parse_args()
    categories = [args.query] if args.query else DEFAULT_CATEGORIES
    print(f"eBay UK Sold — {len(categories)} categories")
    total = 0
    for i, q in enumerate(categories):
        print(f"  [{i+1}/{len(categories)}] {q}...", end=' ')
        items = search_ebay_sold(q, max_results=args.count)
        saved = save_results(q, items)
        total += saved
        print(f"{saved} items")
        time.sleep(2)
    print(f"Done. {total} total items. Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
