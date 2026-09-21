"""OPSS Product Recalls — ACTUAL historical ingestion.

Fetches real recall records from GOV.UK, not the search HTML.
"""

import hashlib
import json
import re
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.db import get_db

SOURCE_ID = 'opss_recalls'
DATASET = 'opss_historical'
PARSER_ID = 'opss_govuk'
PARSER_VERSION = '1.0.0'


def fetch_page(url):
    """Fetch a page and return content + hash."""
    resp = requests.get(url, timeout=30, headers={'Accept': 'text/html'})
    if resp.status_code == 200:
        return resp.content, resp.status_code
    return None, resp.status_code


def fetch_opss_records():
    """Fetch all OPSS recall records."""
    records = []

    # Try the GOV.UK search API
    base_url = 'https://www.gov.uk/api/content/guidance/product-recalls-and-alerts'
    try:
        resp = requests.get(base_url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # Extract sub-sections
            details = data.get('details', {})
            for section in details.get('child_sections', []):
                records.append({
                    'title': section.get('title', ''),
                    'url': section.get('url', ''),
                    'description': section.get('body', '')[:1000],
                    'date': section.get('public_updated_at', ''),
                })
    except Exception as e:
        print(f'  JSON API error: {e}')

    # Also try the search endpoint
    search_url = 'https://www.gov.uk/search/all.json?filter_content_purpose_supergroup%5B%5D=alerts_and_notifiers&filter_content_purpose_supergroup%5B%5D=guidance&organisations%5B%5D=office-for-product-safety-and-standards&order=updated_at'
    try:
        resp = requests.get(search_url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get('results', []):
                records.append({
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'description': result.get('description', ''),
                    'date': result.get('public_timestamp', ''),
                })
    except Exception as e:
        print(f'  Search API error: {e}')

    # Try RSS feed
    rss_url = 'https://www.gov.uk/government/publications/product-safety-alerts-and-recalls-notifications.rss'
    try:
        resp = requests.get(rss_url, timeout=30)
        if resp.status_code == 200:
            entries = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            for entry in entries:
                title = re.search(r'<title>(.*?)</title>', entry)
                link = re.search(r'<link>(.*?)</link>', entry)
                pubdate = re.search(r'<pubDate>(.*?)</pubDate>', entry)
                desc = re.search(r'<description>(.*?)</description>', entry, re.DOTALL)
                if title:
                    records.append({
                        'title': title.group(1),
                        'url': link.group(1) if link else '',
                        'description': desc.group(1)[:500] if desc else '',
                        'date': pubdate.group(1) if pubdate else '',
                    })
    except Exception as e:
        print(f'  RSS error: {e}')

    return records


def store_records(records):
    """Store records as source_records."""
    conn = get_db()
    count = 0
    for rec in records:
        native_id = rec.get('url', '').split('/')[-1] or rec.get('title', '')[:50]
        record_id = f'{SOURCE_ID}:{native_id}'
        normalized = {
            'source_native_id': native_id,
            'title': rec.get('title', ''),
            'url': rec.get('url', ''),
            'description': rec.get('description', ''),
            'date': rec.get('date', ''),
        }
        payload_hash = hashlib.sha256(
            json.dumps(normalized, sort_keys=True).encode()
        ).hexdigest()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO source_record "
                "(source_record_id, source_id, dataset, source_native_id, event_time, "
                "retrieved_at, normalized_json, payload_hash, raw_payload_hash, "
                "parser_id, parser_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, SOURCE_ID, DATASET, native_id,
                 rec.get('date', ''), datetime.now().isoformat(),
                 json.dumps(normalized, default=str), payload_hash,
                 '', PARSER_ID, PARSER_VERSION)
            )
            count += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return count


def run():
    print('OPSS Product Recalls — Historical Ingestion')
    print('=' * 50)

    records = fetch_opss_records()
    print(f'  Fetched {len(records)} records')

    count = store_records(records)
    print(f'  Stored {count} source records')

    # Show sample
    if records:
        print('\n  Sample:')
        for r in records[:5]:
            print(f'    {r.get("title", "?")[:60]}')
            print(f'      {r.get("date", "?")} | {r.get("url", "?")[:50]}')


if __name__ == '__main__':
    run()
