"""OPSS Product Recalls Collector — safety defect / recall layer.

Fetches UK Office for Product Safety and Standards recalls.
"""

import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

DB = Path(__file__).parent.parent / 'warehouse' / 'repair.db'


def fetch_opss():
    """Fetch OPSS recalls."""
    items = []
    # OPSS RSS feed
    try:
        resp = requests.get('https://www.gov.uk/government/publications/product-safety-alerts-and-recalls-notifications.rss',
                           timeout=15, headers={'Accept': 'application/rss+xml'})
        if resp.status_code == 200:
            # Parse RSS items
            import re
            entries = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            for entry in entries:
                title = re.search(r'<title>(.*?)</title>', entry)
                link = re.search(r'<link>(.*?)</link>', entry)
                pubdate = re.search(r'<pubDate>(.*?)</pubDate>', entry)
                desc = re.search(r'<description>(.*?)</description>', entry, re.DOTALL)
                items.append({
                    'title': title.group(1) if title else '',
                    'url': link.group(1) if link else '',
                    'date': pubdate.group(1) if pubdate else '',
                    'description': desc.group(1)[:500] if desc else '',
                })
    except Exception as e:
        print(f'  RSS error: {e}')

    # Also try the JSON endpoint
    try:
        resp = requests.get('https://www.gov.uk/api/content/guidance/product-recalls-and-alerts',
                           timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            details = data.get('details', {}).get('child_sections', [])
            for section in details:
                items.append({
                    'title': section.get('title', ''),
                    'url': section.get('url', ''),
                    'description': section.get('body', '')[:500],
                })
    except Exception as e:
        print(f'  JSON error: {e}')

    return items


def run():
    print('OPSS Product Recalls Collector')
    print('=' * 40)

    conn = sqlite3.connect(str(DB))
    items = fetch_opss()
    print(f'  Fetched {len(items)} recall items')

    count = 0
    for item in items:
        store_obs(conn, 'opss_recalls', item.get('title', '')[:50], 'recall',
            {'title': item.get('title'), 'url': item.get('url'),
             'date': item.get('date'), 'description': item.get('description')}, item)
        count += 1
    conn.commit()

    print(f'  Stored {count} recalls')
    conn.close()


def store_obs(conn, source, entity, metric, value_dict, raw=None):
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


if __name__ == '__main__':
    run()
