"""
Open Repair collector — follows canonical collector contract.

Collects repair data from Open Repair Alliance.
Normalizes to canonical Observation/Entity types.
"""

import json
import urllib.request
from typing import List
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.collector_contract import Collector, RawBatch
from shared.schema import (
    Observation, Entity, AssetFamily, AssetModel, Fault, FaultObservation,
    TruthClass, Recoverability
)
from shared.storage import (
    archive_raw, store_entity, store_observation, store_raw_ingest,
    store_collector_run, get_db, init_db
)


class OpenRepairCollector(Collector):
    source_id = "open_repair"
    
    def collect(self) -> RawBatch:
        """Fetch Open Repair Alliance data."""
        url = "https://openrepair.org/open-data/downloads/"
        req = urllib.request.Request(url, headers={"User-Agent": "repair-garden/1.0"})
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        
        # Count approximate records (HTML page, actual data needs parsing)
        record_count = data.count(b'"repair"') + data.count(b'"fault"')
        
        return RawBatch(
            source_id=self.source_id,
            dataset="open_repair_page",
            data=data,
            record_count=record_count,
            metadata={"url": url}
        )
    
    def normalize(self, raw: RawBatch) -> list:
        """Normalize raw data to canonical types.
        
        Note: This is a simplified version. Real implementation would
        parse the actual Open Repair CSV/JSON data.
        """
        observations = []
        
        # For now, create a summary observation
        obs = Observation(
            observation_id="",
            garden="repair",
            source_id=self.source_id,
            entity_id="open_repair_dataset",
            metric="repair_data_size_bytes",
            value_numeric=float(len(raw.data)),
            unit="bytes",
            event_time=datetime.now(timezone.utc).isoformat(),
            truth_class=TruthClass.OBSERVED,
            recoverability=Recoverability.SNAPSHOT,
        )
        observations.append(obs)
        
        return observations


def run_collector():
    """Run the Open Repair collector."""
    init_db()
    collector = OpenRepairCollector()
    manifest = collector.run()
    
    # Store in DB
    with get_db() as conn:
        store_collector_run(
            conn,
            run_id=manifest.run_id,
            source_id=manifest.source_id,
            raw_records=manifest.raw_records,
            normalized_records=manifest.normalized_records,
            new_observations=manifest.new_observations,
            status=manifest.status,
            error=manifest.error,
        )
    
    print(json.dumps({
        "source": manifest.source_id,
        "status": manifest.status,
        "raw_records": manifest.raw_records,
        "normalized": manifest.normalized_records,
        "error": manifest.error,
    }, indent=2))
    
    return manifest


if __name__ == "__main__":
    run_collector()
