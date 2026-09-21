"""Open Repair Alliance — ACTUAL historical dataset ingestion.

Downloads the complete CSV from GitHub, not the website.
Target: 300K+ records with full provenance.
"""

import csv
import gzip
import hashlib
import io
import json
import sqlite3
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.db import get_db, get_db_path

SOURCE_ID = 'open_repair'
DATASET = 'open_repair_complete'
PARSER_ID = 'open_repair_csv'
PARSER_VERSION = '1.0.0'

# The actual data URL (from their GitHub, not the website)
DATA_URL = 'https://raw.githubusercontent.com/openrepair/data/master/aggregated/202507/OpenRepairData_v0.3_aggregate_202507.csv'


def fetch_raw():
    """Download the actual CSV dataset."""
    print(f'  Fetching {DATA_URL}...')
    resp = requests.get(DATA_URL, timeout=120)
    if resp.status_code != 200:
        raise Exception(f'HTTP {resp.status_code}')

    content = resp.content
    sha256 = hashlib.sha256(content).hexdigest()

    # Store raw blob using canonical path
    raw_dir = get_db_path().parent / 'raw' / SOURCE_ID
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f'{sha256}.csv.gz'

    if not raw_path.exists():
        with gzip.open(raw_path, 'wb') as f:
            f.write(content)

    # Store acquisition receipt
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO raw_blob (sha256, source_id, content_type, content_length, storage_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (sha256, SOURCE_ID, 'text/csv', len(content), str(raw_path))
    )
    conn.execute(
        "INSERT INTO raw_acquisition (source_id, dataset, retrieved_at, request_url, http_status, "
        "content_type, content_length, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (SOURCE_ID, DATASET, datetime.now(timezone.utc).isoformat(), DATA_URL, 200,
         'text/csv', len(content), sha256)
    )
    conn.commit()
    print(f'  Raw stored: {sha256[:12]}... ({len(content):,} bytes)')
    return raw_path, sha256


def parse_and_store(raw_path, raw_sha256):
    """Parse CSV and store as source_records."""
    conn = get_db()

    # Check cursor for resumability
    cursor_row = conn.execute(
        "SELECT cursor_value FROM source_cursor WHERE source_id=? AND dataset=?",
        (SOURCE_ID, DATASET)
    ).fetchone()
    skip_count = int(cursor_row[0]) if cursor_row else 0

    print(f'  Parsing CSV (skip={skip_count})...')
    count = 0
    skipped = 0

    with gzip.open(raw_path, 'rt', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < skip_count:
                skipped += 1
                continue

            # Create source_record_id from source-native fields
            native_id = row.get('id', f'row_{i}')
            record_id = f'{SOURCE_ID}:{native_id}'

            # Normalize the record
            normalized = {
                'source_native_id': native_id,
                'event_date': row.get('event_date', ''),
                'country': row.get('country', ''),
                'product_category': row.get('product_category', ''),
                'brand': row.get('brand', ''),
                'model': row.get('model', ''),
                'problem': row.get('problem', ''),
                'repair_status': row.get('repair_status', ''),
                'repair_barrier': row.get('repair_barrier', ''),
                'data_provider': row.get('data_provider', ''),
                'group_identifier': row.get('group_identifier', ''),
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
                     row.get('event_date', ''), datetime.now(timezone.utc).isoformat(),
                     json.dumps(normalized, default=str), payload_hash,
                     raw_sha256, PARSER_ID, PARSER_VERSION)
                )
                count += 1
            except sqlite3.IntegrityError:
                pass  # duplicate, skip

            if count % 10000 == 0 and count > 0:
                conn.commit()
                print(f'    ...{count:,} records')

    # Update cursor
    conn.execute(
        "INSERT OR REPLACE INTO source_cursor (source_id, dataset, cursor_type, cursor_value, updated_at) "
        "VALUES (?, ?, 'row_count', ?, ?)",
        (SOURCE_ID, DATASET, str(i + 1), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

    print(f'  Stored {count:,} source records (skipped {skipped:,})')
    return count


def run():
    print(f'Open Repair Alliance — Historical Ingestion')
    print(f'URL: {DATA_URL}')
    print('=' * 60)

    raw_path, sha256 = fetch_raw()
    count = parse_and_store(raw_path, sha256)

    print(f'\nDone. {count:,} records ingested.')
    print(f'Target: 300K+ records')


if __name__ == '__main__':
    run()
