"""
repair canonical storage — single storage layer.

Replaces: storage.py (root), core/storage.py, and JSONL files.
All collectors flow through this. Append-only. Immutable raw.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List

# ─── PATHS ────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "warehouse" / "repair.db"
RAW_DIR = ROOT / "raw"  # immutable raw archive


# ─── DB ───────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_conn():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ─── SCHEMA ───────────────────────────────────────────────────

SCHEMA = """
-- Shared entities
CREATE TABLE IF NOT EXISTS entity (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attributes_json TEXT
);

-- Observations (immutable once written)
CREATE TABLE IF NOT EXISTS observation (
    observation_id TEXT PRIMARY KEY,
    garden TEXT NOT NULL,
    source_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value TEXT,
    value_numeric REAL,
    unit TEXT,
    event_time TEXT,
    observed_at TEXT NOT NULL,
    truth_class TEXT NOT NULL DEFAULT 'observed',
    recoverability TEXT NOT NULL DEFAULT 'snapshot',
    rights TEXT NOT NULL DEFAULT 'powuk_internal',
    raw_payload_hash TEXT,
    source_native_id TEXT,
    payload_hash TEXT
);
CREATE INDEX IF NOT EXISTS idx_obs_entity ON observation(entity_id, metric);
CREATE INDEX IF NOT EXISTS idx_obs_source ON observation(source_id, observed_at);

-- Derived facts
CREATE TABLE IF NOT EXISTS derived_fact (
    derived_id TEXT PRIMARY KEY,
    garden TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value TEXT,
    value_numeric REAL,
    unit TEXT,
    computed_at TEXT NOT NULL,
    method_id TEXT NOT NULL,
    method_version TEXT NOT NULL,
    input_ids_json TEXT,
    truth_class TEXT NOT NULL DEFAULT 'derived',
    confidence REAL,
    rights TEXT NOT NULL DEFAULT 'powuk_internal'
);

-- Entity resolution
CREATE TABLE IF NOT EXISTS entity_resolution (
    resolution_id TEXT PRIMARY KEY,
    source_record_id TEXT NOT NULL,
    candidate_entity_id TEXT NOT NULL,
    match_method TEXT NOT NULL,
    match_features TEXT,
    confidence REAL NOT NULL DEFAULT 0.0,
    resolved_at TEXT NOT NULL,
    resolver_version TEXT NOT NULL DEFAULT '1.0'
);

-- Repair garden specific
CREATE TABLE IF NOT EXISTS asset_family (
    family_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS asset_model (
    model_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_number TEXT,
    release_date TEXT
);

CREATE TABLE IF NOT EXISTS asset_revision (
    revision_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    revision_code TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS asset_instance (
    instance_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    revision_id TEXT,
    serial_number TEXT,
    acquired_at TEXT,
    acquisition_cost REAL,
    current_state TEXT NOT NULL DEFAULT 'unknown'
);

CREATE TABLE IF NOT EXISTS fault (
    fault_id TEXT PRIMARY KEY,
    fault_type TEXT NOT NULL,
    description TEXT,
    symptoms TEXT,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS fault_observation (
    observation_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    fault_id TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    source_id TEXT NOT NULL,
    confidence REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS part (
    part_id TEXT PRIMARY KEY,
    manufacturer TEXT NOT NULL,
    mpn TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS part_offer (
    offer_id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    price REAL,
    currency TEXT NOT NULL DEFAULT 'GBP',
    stock_quantity INTEGER,
    moq INTEGER,
    lead_time_days INTEGER,
    condition TEXT NOT NULL DEFAULT 'new',
    listing_url TEXT,
    observed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_offer_part ON part_offer(part_id, observed_at);

CREATE TABLE IF NOT EXISTS compatibility (
    compatibility_id TEXT PRIMARY KEY,
    part_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    revision_id TEXT,
    compatibility_type TEXT NOT NULL DEFAULT 'direct_fit',
    confidence REAL NOT NULL DEFAULT 1.0,
    evidence TEXT,
    valid_from TEXT,
    valid_to TEXT
);

CREATE TABLE IF NOT EXISTS intervention (
    intervention_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    fault_id TEXT NOT NULL,
    actions TEXT NOT NULL,
    parts_used TEXT,
    tools_required TEXT,
    labour_minutes INTEGER,
    skill_level TEXT
);

CREATE TABLE IF NOT EXISTS repair_attempt (
    attempt_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    fault_observations TEXT,
    condition_before TEXT,
    suspected_faults TEXT,
    diagnosis_confidence REAL,
    intervention_id TEXT,
    parts_used TEXT,
    labour_minutes INTEGER,
    tools_used TEXT,
    acquisition_cost REAL,
    parts_cost REAL,
    labour_cost REAL,
    total_cost REAL,
    repaired INTEGER,
    partially_repaired INTEGER,
    survived_7d INTEGER,
    survived_30d INTEGER,
    failed_again INTEGER,
    failure_mode TEXT,
    resale_price REAL,
    days_to_sale INTEGER,
    source_id TEXT,
    photos TEXT,
    observed_at TEXT NOT NULL
);

-- Raw ingestion tracking
CREATE TABLE IF NOT EXISTS raw_ingest (
    ingest_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    raw_hash TEXT NOT NULL,
    raw_path TEXT NOT NULL,
    row_count INTEGER,
    bytes INTEGER,
    status TEXT NOT NULL
);

-- Collector run tracking
CREATE TABLE IF NOT EXISTS collector_run (
    run_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    raw_records INTEGER DEFAULT 0,
    normalized_records INTEGER DEFAULT 0,
    resolved_entities INTEGER DEFAULT 0,
    new_observations INTEGER DEFAULT 0,
    duplicate_observations INTEGER DEFAULT 0,
    invalid_records INTEGER DEFAULT 0,
    raw_hash TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    error TEXT
);
"""


def init_db():
    with db_conn() as conn:
        conn.executescript(SCHEMA)


# ─── RAW ARCHIVE (immutable) ─────────────────────────────────

def archive_raw(source_id: str, dataset: str, data: bytes) -> str:
    """Archive raw data immutably. Returns hash-addressed path."""
    h = hashlib.sha256(data).hexdigest()
    ts = datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
    path = RAW_DIR / source_id / f"{ts}_{h[:16]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


# ─── STORE (canonical) ───────────────────────────────────────

def store_entity(conn: sqlite3.Connection, entity_type: str, entity_id: str,
                 name: str, attributes: dict = None):
    conn.execute("""
        INSERT OR REPLACE INTO entity (entity_id, entity_type, canonical_name, created_at, attributes_json)
        VALUES (?, ?, ?, ?, ?)
    """, (entity_id, entity_type, name, datetime.now(timezone.utc).isoformat(),
          json.dumps(attributes) if attributes else None))


def store_observation(conn: sqlite3.Connection, obs) -> str:
    """Store an observation. Returns observation_id."""
    record = obs if isinstance(obs, dict) else {
        "observation_id": obs.observation_id,
        "garden": obs.garden,
        "source_id": obs.source_id,
        "entity_id": obs.entity_id,
        "metric": obs.metric,
        "value": obs.value,
        "value_numeric": obs.value_numeric,
        "unit": obs.unit,
        "event_time": obs.event_time,
        "observed_at": obs.observed_at,
        "truth_class": obs.truth_class.value if hasattr(obs.truth_class, 'value') else obs.truth_class,
        "recoverability": obs.recoverability.value if hasattr(obs.recoverability, 'value') else obs.recoverability,
        "rights": obs.rights,
        "raw_payload_hash": obs.raw_payload_hash,
        "source_native_id": obs.source_native_id,
        "payload_hash": obs.payload_hash,
    }
    conn.execute("""
        INSERT OR REPLACE INTO observation
        (observation_id, garden, source_id, entity_id, metric, value, value_numeric,
         unit, event_time, observed_at, truth_class, recoverability, rights,
         raw_payload_hash, source_native_id, payload_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(record.values()))
    return record["observation_id"]


def store_observation_batch(conn: sqlite3.Connection, observations: list) -> int:
    count = 0
    for obs in observations:
        store_observation(conn, obs)
        count += 1
    return count


def store_repair_attempt(conn: sqlite3.Connection, attempt) -> str:
    """Store a repair attempt (proprietary receipt)."""
    record = attempt if isinstance(attempt, dict) else {
        "attempt_id": attempt.attempt_id,
        "instance_id": attempt.instance_id,
        "model_id": attempt.model_id,
        "fault_observations": attempt.fault_observations,
        "condition_before": attempt.condition_before,
        "suspected_faults": attempt.suspected_faults,
        "diagnosis_confidence": attempt.diagnosis_confidence,
        "intervention_id": attempt.intervention_id,
        "parts_used": attempt.parts_used,
        "labour_minutes": attempt.labour_minutes,
        "tools_used": attempt.tools_used,
        "acquisition_cost": attempt.acquisition_cost,
        "parts_cost": attempt.parts_cost,
        "labour_cost": attempt.labour_cost,
        "total_cost": attempt.total_cost,
        "repaired": attempt.repaired,
        "partially_repaired": attempt.partially_repaired,
        "survived_7d": attempt.survived_7d,
        "survived_30d": attempt.survived_30d,
        "failed_again": attempt.failed_again,
        "failure_mode": attempt.failure_mode,
        "resale_price": attempt.resale_price,
        "days_to_sale": attempt.days_to_sale,
        "source_id": attempt.source_id,
        "photos": attempt.photos,
        "observed_at": attempt.observed_at,
    }
    conn.execute("""
        INSERT OR REPLACE INTO repair_attempt
        (attempt_id, instance_id, model_id, fault_observations, condition_before,
         suspected_faults, diagnosis_confidence, intervention_id, parts_used,
         labour_minutes, tools_used, acquisition_cost, parts_cost, labour_cost,
         total_cost, repaired, partially_repaired, survived_7d, survived_30d,
         failed_again, failure_mode, resale_price, days_to_sale, source_id,
         photos, observed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(record.values()))
    return record["attempt_id"]


def store_raw_ingest(conn: sqlite3.Connection, source_id: str, dataset: str,
                     raw_path: str, raw_hash: str, row_count: int, byte_count: int):
    conn.execute("""
        INSERT OR REPLACE INTO raw_ingest
        (ingest_id, source_id, dataset, observed_at, raw_hash, raw_path, row_count, bytes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ok')
    """, (f"{source_id}_{dataset}_{raw_hash[:16]}", source_id, dataset,
          datetime.now(timezone.utc).isoformat(), raw_hash, raw_path, row_count, byte_count))


def store_collector_run(conn: sqlite3.Connection, run_id: str, source_id: str,
                        raw_records: int, normalized_records: int, new_observations: int,
                        status: str = "ok", error: str = None):
    conn.execute("""
        INSERT OR REPLACE INTO collector_run
        (run_id, source_id, started_at, completed_at, raw_records, normalized_records,
         new_observations, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (run_id, source_id, datetime.now(timezone.utc).isoformat(),
          datetime.now(timezone.utc).isoformat(), raw_records, normalized_records,
          new_observations, status, error))


# ─── QUERIES ──────────────────────────────────────────────────

def count_by_source(conn: sqlite3.Connection, source_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM observation WHERE source_id = ?",
                       (source_id,)).fetchone()[0]


def count_by_garden(conn: sqlite3.Connection, garden: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM observation WHERE garden = ?",
                       (garden,)).fetchone()[0]


def get_db_stats(conn: sqlite3.Connection) -> dict:
    tables = ["entity", "observation", "derived_fact", "entity_resolution",
              "asset_family", "asset_model", "asset_revision", "asset_instance",
              "fault", "fault_observation", "part", "part_offer", "compatibility",
              "intervention", "repair_attempt", "raw_ingest", "collector_run"]
    stats = {}
    for table in tables:
        try:
            stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except:
            stats[table] = 0
    return stats
