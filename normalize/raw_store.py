"""Raw Storage — immutable, content-addressed, append-only.

Every collector run produces:
  raw/{source_id}/{YYYY}/{MM}/{DD}/{HHMMSS}-{sha256}.json.gz

The raw payload is never overwritten. The database stores a reference.
"""

import gzip
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


RAW_ROOT = Path(__file__).parent.parent / 'warehouse' / 'raw'


def store_raw(source_id: str, dataset_id: str, payload: dict, metadata: dict = None) -> dict:
    """Store raw payload immutably. Returns storage manifest."""
    now = datetime.now(timezone.utc)
    date_path = now.strftime("%Y/%m/%d")
    time_prefix = now.strftime("%H%M%S")

    content = json.dumps(payload, default=str, sort_keys=True).encode()
    sha256 = hashlib.sha256(content).hexdigest()

    filename = f"{time_prefix}-{sha256[:12]}.json.gz"
    storage_dir = RAW_ROOT / source_id / date_path
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / filename

    with gzip.open(storage_path, 'wb') as f:
        f.write(content)

    manifest = {
        'source_id': source_id,
        'dataset_id': dataset_id,
        'retrieved_at': now.isoformat(),
        'sha256': sha256,
        'storage_uri': str(storage_path.relative_to(RAW_ROOT.parent)),
        'content_length': len(content),
        'content_type': 'application/json',
        'compressed': True,
    }
    if metadata:
        manifest.update(metadata)

    return manifest
