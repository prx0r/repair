"""
France Repairability Index collector — follows canonical collector contract.
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


class FranceRepairabilityCollector(Collector):
    source_id = "france_repairability"
    
    def collect(self) -> RawBatch:
        """Fetch France repairability index data."""
        url = "https://schema.data.gouv.fr/etalab/schema-indice-reparabilite/0.1.1/"
        req = urllib.request.Request(url, headers={"User-Agent": "repair-garden/1.0"})
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        
        return RawBatch(
            source_id=self.source_id,
            dataset="france_repairability_schema",
            data=data,
            record_count=1,
            metadata={"url": url}
        )
    
    def normalize(self, raw: RawBatch) -> list:
        observations = []
        obs = Observation(
            observation_id="",
            garden="repair",
            source_id=self.source_id,
            entity_id="france_repairability_schema",
            metric="schema_size_bytes",
            value_numeric=float(len(raw.data)),
            unit="bytes",
            event_time=datetime.now(timezone.utc).isoformat(),
            truth_class=TruthClass.OBSERVED,
            recoverability=Recoverability.CANONICAL,
        )
        observations.append(obs)
        return observations


def run_collector():
    init_db()
    collector = FranceRepairabilityCollector()
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
