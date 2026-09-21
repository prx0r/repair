"""
OPSS Product Recalls collector — follows canonical collector contract.
"""

import json
import urllib.request
from typing import List
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.collector_contract import Collector, RawBatch
from shared.schema import Observation, Entity, Fault, TruthClass, Recoverability
from shared.storage import (
    archive_raw, store_entity, store_observation, store_raw_ingest,
    store_collector_run, get_db, init_db
)


class OPSSCollector(Collector):
    source_id = "opss_recalls"
    
    def collect(self) -> RawBatch:
        """Fetch OPSS product safety alerts."""
        url = "https://www.gov.uk/product-safety-alerts-reports-recalls"
        req = urllib.request.Request(url, headers={"User-Agent": "repair-garden/1.0"})
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        
        # Count recalls (approximate from HTML)
        record_count = data.count(b'product-safety-alerts') // 2
        
        return RawBatch(
            source_id=self.source_id,
            dataset="opss_alerts",
            data=data,
            record_count=record_count,
            metadata={"url": url}
        )
    
    def normalize(self, raw: RawBatch) -> list:
        observations = []
        obs = Observation(
            observation_id="",
            garden="repair",
            source_id=self.source_id,
            entity_id="opss_dataset",
            metric="opss_recall_page_size_bytes",
            value_numeric=float(len(raw.data)),
            unit="bytes",
            event_time=datetime.now(timezone.utc).isoformat(),
            truth_class=TruthClass.OBSERVED,
            recoverability=Recoverability.SNAPSHOT,
        )
        observations.append(obs)
        return observations


def run_collector():
    init_db()
    collector = OPSSCollector()
    manifest = collector.run()
    with get_db() as conn:
        store_collector_run(conn, manifest.run_id, manifest.source_id,
                          manifest.raw_records, manifest.normalized_records,
                          manifest.new_observations, manifest.status, manifest.error)
    print(json.dumps({"source": manifest.source_id, "status": manifest.status,
                      "raw": manifest.raw_records, "norm": manifest.normalized_records}, indent=2))
    return manifest


if __name__ == "__main__":
    run_collector()
