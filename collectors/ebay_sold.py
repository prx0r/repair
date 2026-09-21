"""
Breadup — eBay Sold Collector (Apify free tier)

Apify gives $5/mo free credit — no card needed.
Each listing costs ~$2/1K, so $5 = ~2,500 listings/month.
That's enough for 50 categories × 50 items = 2,500/month.
"""

import os
import json
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'

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


def collect_sold(query: str, count: int = 50) -> list:
    """Collect sold listings from eBay UK via Apify free tier."""
    try:
        from apify_client import ApifyClient
    except ImportError:
        print("  Install: pip install apify-client")
        return []

    token = os.environ.get('APIFY_TOKEN')
    if not token:
        print("  Set APIFY_TOKEN in .env (free at apify.com)")
        return []

    client = ApifyClient(token)

    run_input = {
        'keyword': query,
        'condition': 'used',
        'daysToScrape': 60,
        'count': count,
    }

    try:
        run = client.actor('tnodes/ebay-sold-scraper').call(run_input=run_input)
        items = client.dataset(run['defaultDatasetId']).list_items().items
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
                'itemId': item.get('itemId', ''),
                'title': item.get('title', ''),
                'soldPrice': item.get('soldPrice', 0),
                'soldCurrency': item.get('soldCurrency', 'GBP'),
                'endedAt': item.get('endedAt', ''),
                'condition': item.get('condition', ''),
                'keyword': query,
                'collected_at': datetime.now().isoformat(),
            }
            f.write(json.dumps(record) + '\n')
            count += 1

    return count


def main():
    """Run collector for categories."""
    import argparse

    parser = argparse.ArgumentParser(description='eBay Sold Collector (Apify free tier)')
    parser.add_argument('--query', type=str, help='Single search query')
    parser.add_argument('--count', type=int, default=50, help='Results per query')
    args = parser.parse_args()

    categories = [args.query] if args.query else DEFAULT_CATEGORIES

    print(f"eBay Sold Collector — {len(categories)} categories")
    print(f"Using Apify free tier ($5/mo credit)")
    print("=" * 50)

    total = 0
    for i, query in enumerate(categories):
        print(f"  [{i+1}/{len(categories)}] {query}...", end=' ')
        items = collect_sold(query, count=args.count)
        saved = save_results(query, items)
        total += saved
        print(f"{saved} items")

    print(f"\nDone. {total} items collected.")
    print(f"Data: {DATA_DIR}")


if __name__ == '__main__':
    main()
