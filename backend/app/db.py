"""
SQLite Data Layer for the real eSAKSHI MPLADS dataset.
Connection helpers + schema DDL. The database is built once by `python -m backend.app.etl`
from the official scraped CSVs in data/mplads_data/csv/.
"""

import os
import sqlite3
from pathlib import Path

# Repo root: backend/app/db.py -> two levels up
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_DB_PATH = REPO_ROOT / "backend" / "data" / "mplads.db"


def get_db_path() -> Path:
    """DB location overridable via MPLADS_DB env var (tests / Docker volumes)."""
    env = os.getenv("MPLADS_DB")
    return Path(env) if env else DEFAULT_DB_PATH


def get_connection(db_path=None) -> sqlite3.Connection:
    """Row-factory connection to the MPLADS SQLite database."""
    path = Path(db_path) if db_path else get_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def row_to_dict(row) -> dict:
    """Convert a sqlite3.Row to a plain dict (returns {} for None)."""
    return dict(row) if row is not None else {}


SCHEMA = """
-- ============================================================
-- works: base from works_recommended_{LS,RS}, enriched with
-- sanction/completion/expenditure joins on WORK_RECOMMENDATION_DTL_ID
-- ============================================================
CREATE TABLE IF NOT EXISTS works (
    work_id                 TEXT PRIMARY KEY,
    house                   TEXT NOT NULL,              -- 'Lok Sabha' | 'Rajya Sabha'
    state                   TEXT,
    district                TEXT,                       -- parsed from IDA_NAME prefix
    constituency            TEXT,
    constituency_id         TEXT,
    mp_name                 TEXT,
    tenure                  TEXT,
    work_category           TEXT,
    activity_name           TEXT,
    work_description        TEXT,
    ida_name                TEXT,                       -- Integrated District Authority
    letter_no               TEXT,                       -- tabs/newlines stripped
    file_status             TEXT,
    attach_id               TEXT,
    work_stage              TEXT,
    work_status             TEXT,                       -- derived: Completed/In Progress/Sanctioned/Pending Sanction
    recommendation_date     TEXT,                       -- ISO YYYY-MM-DD
    sanction_date           TEXT,
    actual_end_date         TEXT,
    recommended_amount      REAL,
    sanction_amount         REAL,
    actual_amount           REAL,                      -- from completed works
    total_disbursed        REAL,                      -- sum of vendor payments
    payment_count           INTEGER,                   -- number of vendor payment rows
    vendor_count            INTEGER,                   -- distinct vendors paid
    completion_rating       REAL,
    days_to_sanction        REAL,
    days_to_completion      REAL,
    risk_score              REAL,
    risk_level              TEXT,
    data_quality_score      REAL,
    data_quality_status     TEXT,
    evidence_confidence_score REAL,
    evidence_confidence_level TEXT,
    signals_count           INTEGER
);

-- ============================================================
-- payments: vendor disbursement rows from expenditure CSVs
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id             TEXT NOT NULL,
    house               TEXT,
    state               TEXT,
    district            TEXT,
    constituency        TEXT,
    mp_name             TEXT,
    tenure              TEXT,
    activity_name       TEXT,
    ida_name            TEXT,
    ia_name             TEXT,                          -- Implementing Agency
    vendor_id           TEXT,
    vendor_name         TEXT,
    expenditure_date    TEXT,                           -- ISO YYYY-MM-DD
    fund_disbursed_amt  REAL,
    work_status         TEXT,                          -- payment pipeline status
    letter_no           TEXT
);
CREATE INDEX IF NOT EXISTS idx_payments_work   ON payments(work_id);
CREATE INDEX IF NOT EXISTS idx_payments_vendor ON payments(vendor_name);

-- ============================================================
-- mp_allocations: official allocated limits for both houses
-- ============================================================
CREATE TABLE IF NOT EXISTS mp_allocations (
    sr_no           INTEGER PRIMARY KEY,
    state           TEXT NOT NULL,
    house           TEXT NOT NULL,                     -- 'Lok Sabha' | 'Rajya Sabha'
    tenure          TEXT,
    mp_name         TEXT NOT NULL,
    constituency    TEXT,
    allocated_amount REAL
);

-- ============================================================
-- vendors: payment concentration profile per vendor
-- ============================================================
CREATE TABLE IF NOT EXISTS vendors (
    vendor_name         TEXT PRIMARY KEY,
    total_disbursed     REAL,
    work_count          INTEGER,                      -- distinct works paid
    district_count      INTEGER,                       -- distinct districts active in
    state_count         INTEGER,
    first_payment_date  TEXT,
    last_payment_date   TEXT
);

-- ============================================================
-- alerts: persisted explainable alerts generated by the RiskEngine
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id        TEXT PRIMARY KEY,                  -- 'ALT-<work_id>'
    work_id         TEXT NOT NULL,
    work_title      TEXT,
    state           TEXT,
    district        TEXT,
    constituency    TEXT,
    mp_name         TEXT,
    agency_name     TEXT,
    created_at      TEXT,
    risk_score      REAL,
    risk_level      TEXT,
    risk_breakdown  TEXT,                             -- JSON RiskScoreBreakdown
    data_quality_score REAL,
    data_quality_status TEXT,
    evidence_confidence_score REAL,
    evidence_confidence_level TEXT,
    triggering_signals TEXT,                          -- JSON list of AnomalySignal
    narrative_explanation TEXT,
    duplicate_candidate_id TEXT,
    duplicate_risk_score  REAL,
    recommended_action TEXT,
    is_reviewed     INTEGER DEFAULT 0,
    latest_review   TEXT                              -- JSON latest review record
);
CREATE INDEX IF NOT EXISTS idx_alerts_work  ON alerts(work_id);
CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_alerts_score ON alerts(risk_score);

-- ============================================================
-- reviews: officer verification actions (human-in-the-loop)
-- ============================================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id       TEXT NOT NULL,
    work_id        TEXT NOT NULL,
    officer_name   TEXT NOT NULL,
    officer_role   TEXT NOT NULL,
    action         TEXT NOT NULL,
    remarks        TEXT NOT NULL,
    created_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_alert ON reviews(alert_id);

-- ============================================================
-- audit_logs: append-only immutable action trail
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL,
    action_type   TEXT NOT NULL,
    alert_id      TEXT,
    work_id       TEXT,
    officer      TEXT,
    action       TEXT,
    remarks      TEXT
);

-- ============================================================
-- agencies: implementing/district authority risk profiles
-- ============================================================
CREATE TABLE IF NOT EXISTS agencies (
    agency_id           TEXT PRIMARY KEY,
    agency_name         TEXT NOT NULL,
    district            TEXT,
    total_works         INTEGER,
    completed_works     INTEGER,
    delayed_works       INTEGER,
    avg_days_to_completion REAL,
    avg_cost_deviation_pct REAL,
    total_expenditure   REAL,
    anomaly_count       INTEGER,
    agency_risk_score   REAL,
    agency_risk_level   TEXT
);

-- ============================================================
-- meta: ETL / analytics run bookkeeping
-- ============================================================
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def init_schema(conn: sqlite3.Connection):
    """Create all tables & indexes if they do not exist."""
    conn.executescript(SCHEMA)
    conn.commit()
