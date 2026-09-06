-- MPLADS Anomaly Detection & Risk Intelligence Database Schema
-- Database: SQLite 3

-- 1. Projects Master Table
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY,
    work_category TEXT,
    activity_name TEXT,
    state_name TEXT,
    constituency TEXT,
    constituency_id INTEGER,
    ida_name TEXT,
    ia_name TEXT,
    mp_name TEXT,
    tenure TEXT,
    house_of_parliament INTEGER,
    work_description TEXT,
    letter_no TEXT,
    recommendation_date TEXT,
    sanction_date TEXT,
    actual_completion_date TEXT,
    recommended_amount REAL,
    sanction_amount REAL,
    actual_amount REAL,
    total_expenditure REAL,
    max_single_payment REAL,
    payment_count INTEGER,
    first_expenditure_date TEXT,
    last_expenditure_date TEXT,
    vendor_name TEXT,
    vendor_id INTEGER,
    unique_vendors INTEGER,
    work_stage TEXT,
    work_status_exp TEXT,
    file_status TEXT,
    average_rating REAL,
    mp_allocated_amount REAL,
    is_completed INTEGER DEFAULT 0,
    has_expenditure INTEGER DEFAULT 0,
    attach_id_rec REAL,
    latitude TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    longitude TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    physical_progress_pct TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    financial_progress_pct TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    photo_count TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    expected_completion_date TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    created_at TEXT DEFAULT (datetime('now'))
);

-- 2. Project Expenditure Detail
CREATE TABLE IF NOT EXISTS project_expenditure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    state_name TEXT,
    activity_name TEXT,
    vendor_name TEXT,
    vendor_id INTEGER,
    expenditure_date TEXT,
    fund_disbursed_amt REAL,
    constituency TEXT,
    work_status TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 3. Implementing Agency Risk Profiles
CREATE TABLE IF NOT EXISTS agencies (
    ida_name TEXT PRIMARY KEY,
    total_projects INTEGER,
    completed_projects INTEGER,
    stalled_projects INTEGER,
    cost_anomaly_projects INTEGER,
    total_expenditure REAL,
    total_sanction REAL,
    completion_rate REAL,
    stall_rate REAL,
    cost_anomaly_rate REAL,
    avg_rule_risk REAL,
    delay_risk_normalized REAL,
    cost_risk_normalized REAL,
    historical_anomaly_risk REAL,
    agency_risk REAL,
    agency_risk_confidence TEXT,
    agency_risk_category TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 4. Project Feature Matrix
CREATE TABLE IF NOT EXISTS project_features (
    project_id INTEGER PRIMARY KEY,
    cost_deviation REAL,
    cost_deviation_pct REAL,
    expenditure_ratio REAL,
    rec_san_ratio REAL,
    sanction_delay_days INTEGER,
    completion_duration_days INTEGER,
    project_age_days INTEGER,
    spending_velocity REAL,
    velocity_ratio REAL,
    payment_frequency INTEGER,
    payment_concentration REAL,
    vendor_constituency_count INTEGER,
    category_cost_ratio REAL,
    expenditure_spread_days INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 5. Rule Results
CREATE TABLE IF NOT EXISTS rule_results (
    project_id INTEGER PRIMARY KEY,
    rule_risk REAL,
    applicable_rules INTEGER,
    triggered_rules INTEGER,
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 6. ML Anomaly Results
CREATE TABLE IF NOT EXISTS ml_results (
    project_id INTEGER PRIMARY KEY,
    ml_anomaly_risk REAL,
    ml_prediction TEXT,
    ml_decision_score REAL,
    model_version TEXT DEFAULT 'v1',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 7. Composite Risk Scores
CREATE TABLE IF NOT EXISTS risk_scores (
    project_id INTEGER PRIMARY KEY,
    risk_score REAL,
    risk_category TEXT,
    data_quality_score REAL,
    confidence TEXT,
    rule_risk REAL,
    ml_anomaly_risk REAL,
    duplicate_risk REAL,
    agency_risk REAL,
    evidence_count INTEGER,
    top_reasons TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 8. Model Version History
CREATE TABLE IF NOT EXISTS model_versions (
    version_id TEXT PRIMARY KEY,
    algorithm TEXT,
    hyperparameters TEXT,
    number_of_records INTEGER,
    number_of_features INTEGER,
    anomalies_detected INTEGER,
    anomaly_rate REAL,
    training_timestamp TEXT,
    notes TEXT
);

-- 9. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    project_id INTEGER,
    details TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- INDEXES for fast lookup
CREATE INDEX IF NOT EXISTS idx_projects_state ON projects(state_name);
CREATE INDEX IF NOT EXISTS idx_projects_constituency ON projects(constituency);
CREATE INDEX IF NOT EXISTS idx_projects_mp ON projects(mp_name);
CREATE INDEX IF NOT EXISTS idx_projects_ida ON projects(ida_name);
CREATE INDEX IF NOT EXISTS idx_risk_scores_category ON risk_scores(risk_category);
CREATE INDEX IF NOT EXISTS idx_risk_scores_score ON risk_scores(risk_score DESC);
