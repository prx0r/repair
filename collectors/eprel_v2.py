"""
EPREL collector — EU energy product registry.
Follows canonical collector contract.
"""

import json
import urllib.request
from typing import List
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.collector_contract import Collector, RawBatch
from shared.schema import Observation, Entity, TruthClass, Recoverability
from shared.storage import (
    archive_raw, store_entity, store_observation, store_raw_ingest,
    store_collector_run, get_db, init_db
)


class EPRELCollector(Collector):
    source_id = "eprel"
    
    def collect(self) -> RawBatch:
        """Fetch EPREL data."""
        # EPREL has a public search - we'll collect energy-efficient products
        url = "https://energy-efficient-products.ec.europa.eu/api/v1/products?limit=10"
        req = urllib.request.Request(url, headers={"User-Agent": "repair-garden/1.0"})
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        except Exception:
            # Fallback to HTML page
            url = "https://energy-efficient-products.ec.europa.eu/eprel_en"
            req = urllib.request.Request(url, headers={"User-Agent": "repair-garden/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        
        return RawBatch(
            source_id=self.source_id,
            dataset="eprel_products",
            data=data,
            record_count=data.count(b'"product_id"'),
            metadata={"url": url}
        )
    
    def normalize(self, raw: RawBatch) -> list:
        observations = []
        obs = Observation(
            observation_id="",
            garden="repair",
            source_id=self.source_id,
            entity_id="eprel_dataset",
            metric="eprel_data_size_bytes",
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
    collector = EPRELCollector()
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
