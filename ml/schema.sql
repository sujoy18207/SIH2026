-- MPLADS Anomaly Detection & Risk Intelligence Database Schema
-- Database: PostgreSQL 14+

-- 1. Projects Master Table
CREATE TABLE IF NOT EXISTS projects (
    project_id BIGINT PRIMARY KEY,
    work_category VARCHAR(255),
    activity_name TEXT,
    state_name VARCHAR(100),
    constituency VARCHAR(150),
    constituency_id INT,
    ida_name VARCHAR(255),
    ia_name VARCHAR(255),
    mp_name VARCHAR(255),
    tenure VARCHAR(100),
    house_of_parliament INT,
    work_description TEXT,
    letter_no VARCHAR(255),
    recommendation_date DATE,
    sanction_date DATE,
    actual_completion_date DATE,
    recommended_amount NUMERIC(15, 2),
    sanction_amount NUMERIC(15, 2),
    actual_amount NUMERIC(15, 2),
    total_expenditure NUMERIC(15, 2),
    max_single_payment NUMERIC(15, 2),
    payment_count INT,
    first_expenditure_date DATE,
    last_expenditure_date DATE,
    vendor_name VARCHAR(255),
    vendor_id BIGINT,
    unique_vendors INT,
    work_stage VARCHAR(100),
    work_status_exp VARCHAR(100),
    file_status VARCHAR(100),
    average_rating NUMERIC(3, 2),
    mp_allocated_amount NUMERIC(15, 2),
    is_completed BOOLEAN DEFAULT FALSE,
    has_expenditure BOOLEAN DEFAULT FALSE,
    attach_id_rec FLOAT,
    latitude TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    longitude TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    physical_progress_pct TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    financial_progress_pct TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    photo_count TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    expected_completion_date TEXT DEFAULT 'NOT_AVAILABLE_IN_CURRENT_DATASET',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Project Expenditure Detail
CREATE TABLE IF NOT EXISTS project_expenditure (
    id SERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(project_id) ON DELETE CASCADE,
    state_name VARCHAR(100),
    activity_name TEXT,
    vendor_name VARCHAR(255),
    vendor_id BIGINT,
    expenditure_date DATE,
    fund_disbursed_amt NUMERIC(15, 2),
    constituency VARCHAR(150),
    work_status VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Implementing Agency Risk Profiles
CREATE TABLE IF NOT EXISTS agencies (
    ida_name VARCHAR(255) PRIMARY KEY,
    total_projects INT,
    completed_projects INT,
    stalled_projects INT,
    cost_anomaly_projects INT,
    total_expenditure NUMERIC(15, 2),
    total_sanction NUMERIC(15, 2),
    completion_rate NUMERIC(5, 4),
    stall_rate NUMERIC(5, 4),
    cost_anomaly_rate NUMERIC(5, 4),
    avg_rule_risk NUMERIC(5, 2),
    delay_risk_normalized NUMERIC(5, 2),
    cost_risk_normalized NUMERIC(5, 2),
    historical_anomaly_risk NUMERIC(5, 2),
    agency_risk NUMERIC(5, 2),
    agency_risk_confidence VARCHAR(20),
    agency_risk_category VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Project Feature Matrix
CREATE TABLE IF NOT EXISTS project_features (
    project_id BIGINT PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    cost_deviation NUMERIC(10, 4),
    cost_deviation_pct NUMERIC(10, 2),
    expenditure_ratio NUMERIC(10, 4),
    rec_san_ratio NUMERIC(10, 4),
    sanction_delay_days INT,
    completion_duration_days INT,
    project_age_days INT,
    spending_velocity NUMERIC(15, 2),
    velocity_ratio NUMERIC(10, 4),
    payment_frequency INT,
    payment_concentration NUMERIC(5, 4),
    vendor_constituency_count INT,
    category_cost_ratio NUMERIC(10, 4),
    expenditure_spread_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Rule Results
CREATE TABLE IF NOT EXISTS rule_results (
    project_id BIGINT PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    rule_risk NUMERIC(5, 2),
    applicable_rules INT,
    triggered_rules INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. ML Anomaly Results
CREATE TABLE IF NOT EXISTS ml_results (
    project_id BIGINT PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    ml_anomaly_risk NUMERIC(5, 2),
    ml_prediction VARCHAR(20),
    ml_decision_score NUMERIC(10, 6),
    model_version VARCHAR(50) DEFAULT 'v1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Composite Risk Scores
CREATE TABLE IF NOT EXISTS risk_scores (
    project_id BIGINT PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    risk_score NUMERIC(5, 2),
    risk_category VARCHAR(20),
    data_quality_score NUMERIC(5, 2),
    confidence VARCHAR(20),
    rule_risk NUMERIC(5, 2),
    ml_anomaly_risk NUMERIC(5, 2),
    duplicate_risk NUMERIC(5, 2),
    agency_risk NUMERIC(5, 2),
    evidence_count INT,
    top_reasons TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Model Version History
CREATE TABLE IF NOT EXISTS model_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    algorithm VARCHAR(100),
    hyperparameters JSONB,
    number_of_records INT,
    number_of_features INT,
    anomalies_detected INT,
    anomaly_rate NUMERIC(5, 2),
    training_timestamp TIMESTAMP,
    notes TEXT
);

-- 9. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    project_id BIGINT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES for fast lookup
CREATE INDEX IF NOT EXISTS idx_projects_state ON projects(state_name);
CREATE INDEX IF NOT EXISTS idx_projects_constituency ON projects(constituency);
CREATE INDEX IF NOT EXISTS idx_projects_mp ON projects(mp_name);
CREATE INDEX IF NOT EXISTS idx_projects_ida ON projects(ida_name);
CREATE INDEX IF NOT EXISTS idx_risk_scores_category ON risk_scores(risk_category);
CREATE INDEX IF NOT EXISTS idx_risk_scores_score ON risk_scores(risk_score DESC);
