"""
repair collector contract — base class for all collectors.

Every collector must:
1. collect() → fetch raw data, archive immutably
2. normalize(raw) → convert to canonical Observation/Entity types
3. Return a manifest with metrics

Collectors NEVER decide where canonical data lives.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import hashlib
import json


@dataclass
class RawBatch:
    """Raw data from a collection run."""
    source_id: str
    dataset: str
    data: bytes
    record_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def hash(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


@dataclass
class CollectorManifest:
    """Machine-readable output of a collector run."""
    source_id: str
    run_id: str
    raw_records: int = 0
    normalized_records: int = 0
    resolved_entities: int = 0
    new_observations: int = 0
    duplicate_observations: int = 0
    invalid_records: int = 0
    raw_hash: str = ""
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    status: str = "running"
    error: Optional[str] = None
    
    def complete(self, status: str = "ok"):
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.status = status


class Collector(ABC):
    """Base class for all collectors.
    
    Usage:
        class OpenRepairCollector(Collector):
            source_id = "open_repair"
            
            def collect(self) -> RawBatch:
                # Fetch data
                ...
            
            def normalize(self, raw: RawBatch) -> list:
                # Convert to Observations/Entities
                ...
    """
    
    source_id: str
    
    @abstractmethod
    def collect(self) -> RawBatch:
        """Fetch raw data. Returns RawBatch for immutable archival."""
        pass
    
    @abstractmethod
    def normalize(self, raw: RawBatch) -> List[Any]:
        """Convert raw data to canonical types (Observation, Entity, etc.)."""
        pass
    
    def run(self) -> CollectorManifest:
        """Execute the full collection pipeline."""
        manifest = CollectorManifest(source_id=self.source_id, run_id=f"{self.source_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}")
        
        try:
            # 1. Collect
            raw = self.collect()
            manifest.raw_records = raw.record_count
            manifest.raw_hash = raw.hash
            
            # 2. Normalize
            normalized = self.normalize(raw)
            manifest.normalized_records = len(normalized)
            
            # 3. Store in DB
            from shared.storage import get_db, store_observation, store_raw_ingest, archive_raw
            conn = get_db()
            
            # Archive raw data
            raw_path = archive_raw(self.source_id, raw.dataset, raw.data)
            store_raw_ingest(conn, self.source_id, raw.dataset, raw_path, raw.hash, raw.record_count, len(raw.data))
            
            # Store observations
            for obs in normalized:
                if hasattr(obs, 'observation_id'):
                    store_observation(conn, obs)
                    manifest.new_observations += 1
            
            conn.commit()
            conn.close()
            
            manifest.complete("ok")
        except Exception as e:
            manifest.complete("error")
            manifest.error = str(e)
        
        return manifest
