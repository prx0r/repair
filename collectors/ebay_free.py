"""
Breadup — Free eBay UK Sold Collector

Uses eBay's public search with sold/completed filter.
No API key, no Apify needed. Just requests + parsing.
"""

import os
import re
import json
import time
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

DEFAULT_CATEGORIES = [
    'technics turntable',
    'sony amplifier',
    'nikon camera',
    'makita drill',
    'lego star wars',
    'fender amp',
    'nintendo switch',
    'macbook pro',
    'dyson vacuum',
    'kitchenaid mixer',
    'herman miller chair',
    'polaroid camera',
    'espresso machine',
    'mountain bike',
    'rtx 4090',
    'vintage watch',
    'le creuset',
    'smeg fridge',
    'roomba',
    'road bike',
]


def search_ebay_sold(query: str, max_results: int = 50) -> list:
    """Search eBay UK sold listings via public search."""
    url = 'https://www.ebay.co.uk/sch/i.html'
    params = {
        '_nkw': query,
        'LH_Sold': 1,
        'LH_Complete': 1,
        '_sop': 13,  # Sort by recently sold
        '_ipg': min(max_results, 240),
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # First hit the homepage to get cookies
        session.get('https://www.ebay.co.uk', timeout=15)
        time.sleep(1)

        resp = session.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            return []

        # Parse items from HTML
        items = []
        html = resp.text

        # Extract sold items using regex patterns
        # Item titles
        titles = re.findall(r'class="s-item__title"[^>]*>([^<]+)</span>', html)
        # Prices
        prices = re.findall(r'class="s-item__price"[^>]*>[^£]*£([0-9,.]+)', html)
        # Sold dates
        dates = re.findall(r'class="POSITIVE"[^>]*>([^<]+)</span>', html)

        for i in range(min(len(titles), len(prices), max_results)):
            title = titles[i] if i < len(titles) else ''
            price_str = prices[i] if i < len(prices) else '0'
            sold_date = dates[i] if i < len(dates) else ''

            # Skip "Shop on eBay" type entries
            if 'Shop on' in title or 'Results' in title:
                continue

            try:
                price = float(price_str.replace(',', ''))
            except:
                price = 0

            items.append({
                'title': title,
                'soldPrice': price,
                'soldCurrency': 'GBP',
                'soldDate': sold_date,
                'keyword': query,
            })

        return items

    except Exception as e:
        print(f"  Error: {e}")
        return []


def save_results(query: str, items: list) -> int:
    """Save results to daily JSONL file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"

    count = 0
    with open(filepath, 'a') as f:
        for item in items:
            record = {
                'itemId': f"free_{hash(item['title'] + str(item['soldPrice']))}",
                'title': item['title'],
                'soldPrice': item['soldPrice'],
                'soldCurrency': item.get('soldCurrency', 'GBP'),
                'soldDate': item.get('soldDate', ''),
                'keyword': item['keyword'],
                'collected_at': datetime.now().isoformat(),
                'source': 'ebay_public_search',
            }
            f.write(json.dumps(record) + '\n')
            count += 1

    return count


def main():
    """Run free eBay collector."""
    import argparse

    parser = argparse.ArgumentParser(description='Free eBay UK Sold Collector')
    parser.add_argument('--query', type=str, help='Single search query')
    parser.add_argument('--count', type=int, default=50, help='Results per query')
    args = parser.parse_args()

    categories = [args.query] if args.query else DEFAULT_CATEGORIES

    print(f"Free eBay UK Sold Collector — {len(categories)} categories")
    print("=" * 50)

    total = 0
    for i, query in enumerate(categories):
        print(f"  [{i+1}/{len(categories)}] {query}...", end=' ')
        items = search_ebay_sold(query, max_results=args.count)
        saved = save_results(query, items)
        total += saved
        print(f"{saved} items")
        time.sleep(2)  # Rate limit

    print(f"\nDone. {total} total items.")
    print(f"Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
