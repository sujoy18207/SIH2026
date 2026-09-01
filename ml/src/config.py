"""
CENTRALIZED CONFIGURATION
==========================
All configurable paths, thresholds, weights, and parameters for the
MPLADS Anomaly Detection Pipeline.

Override any value via environment variable:
    MPLADS_DATA_DIR=...  python ml/src/data_audit.py
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Directory Layout
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent          # ml/
WORKSPACE_ROOT = PROJECT_ROOT.parent                           # SIH 2026/

# Data directories — try multiple possible locations
_candidate_data_dirs = [
    WORKSPACE_ROOT / "mplads_data" / "csv",                    # actual location
    WORKSPACE_ROOT / "data" / "mplads_data" / "csv",           # alternate
    PROJECT_ROOT / "data" / "raw",                             # fallback
]

if os.environ.get("MPLADS_DATA_DIR"):
    DATA_DIR = Path(os.environ["MPLADS_DATA_DIR"])
else:
    DATA_DIR = next((d for d in _candidate_data_dirs if d.exists()), _candidate_data_dirs[0])

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
OUTPUT_DIR = PROJECT_ROOT / "data"
MODEL_BASE_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments"

# Ensure directories exist
for d in [CLEANED_DIR, OUTPUT_DIR, MODEL_BASE_DIR, REPORT_DIR, EXPERIMENT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Join Key
# ---------------------------------------------------------------------------
JOIN_KEY = "WORK_RECOMMENDATION_DTL_ID"

# ---------------------------------------------------------------------------
# Reference Date  (for age calculations — update periodically)
# ---------------------------------------------------------------------------
REFERENCE_DATE = "2026-09-01"

# ---------------------------------------------------------------------------
# Data Cleaning
# ---------------------------------------------------------------------------
CHUNK_SIZE = 50_000  # rows per chunk for large files
MIN_DESCRIPTION_LENGTH = 15

# ---------------------------------------------------------------------------
# Rule Engine — weights must be configurable
# ---------------------------------------------------------------------------
RULE_WEIGHTS = {
    "R01": 30,   # Expenditure > Sanctioned Amount
    "R02": 15,   # Invalid chronology (sanction before recommendation)
    "R03": 25,   # High expenditure ratio on incomplete works
    "R04": 20,   # Stalled project (old, low expenditure)
    "R05": 10,   # Completion before sanction (impossible chronology)
}

# ---------------------------------------------------------------------------
# Isolation Forest
# ---------------------------------------------------------------------------
PRIMARY_CONTAMINATION = 0.05
PRIMARY_N_ESTIMATORS = 200
RANDOM_STATE = 42
CONTAMINATION_VALUES = [0.01, 0.02, 0.05, 0.10]
N_ESTIMATORS_VALUES = [100, 200]

CANDIDATE_FEATURES = [
    "cost_deviation",
    "expenditure_ratio",
    "rec_san_ratio",
    "sanction_delay_days",
    "spending_velocity",
    "velocity_ratio",
    "payment_frequency",
    "payment_concentration",
    "category_cost_ratio",
    "expenditure_spread_days",
    "vendor_constituency_count",
    "completion_duration_days",
]

# ---------------------------------------------------------------------------
# NLP Similarity
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD = 0.70
MAX_PAIRS_PER_BLOCK = 5000

# ---------------------------------------------------------------------------
# Agency Profiler
# ---------------------------------------------------------------------------
MIN_PROJECTS_RELIABLE = 10
COST_ANOMALY_THRESHOLD = 1.2   # Expenditure > 120% of sanction

AGENCY_RISK_WEIGHTS = {
    "delay_risk": 0.40,
    "cost_risk": 0.30,
    "historical_anomaly_risk": 0.30,
}

# ---------------------------------------------------------------------------
# Composite Risk Engine — weights
# ---------------------------------------------------------------------------
RISK_COMPONENT_WEIGHTS = {
    "rule_risk": 0.30,
    "ml_anomaly_risk": 0.30,
    "duplicate_risk": 0.20,
    "agency_risk": 0.20,
}

# Risk category thresholds
RISK_THRESHOLDS = {
    "LOW": (0, 29),
    "MEDIUM": (30, 59),
    "HIGH": (60, 79),
    "CRITICAL": (80, 100),
}

# ---------------------------------------------------------------------------
# Data Quality Score — penalties for missing critical fields
# ---------------------------------------------------------------------------
DATA_QUALITY_PENALTIES = {
    "sanction_amount": 20,
    "recommendation_date": 15,
    "sanction_date": 15,
    "work_description": 15,
    "ida_name": 10,
    "total_expenditure": 15,
    "work_category": 10,
}

UNAVAILABLE_FIELD_PENALTY = 2.5
UNAVAILABLE_FIELDS = [
    "latitude", "longitude", "physical_progress_pct",
    "financial_progress_pct", "photo_count", "expected_completion_date",
]

# ---------------------------------------------------------------------------
# GIS Analysis
# ---------------------------------------------------------------------------
GIS_MAX_DISTANCE_KM = 1.0
GIS_TEXT_WEIGHT = 0.65
GIS_GEO_WEIGHT = 0.35

# ---------------------------------------------------------------------------
# Model Versioning
# ---------------------------------------------------------------------------
def get_current_model_dir(version: str = "v1") -> Path:
    """Return the model directory for a given version."""
    d = MODEL_BASE_DIR / version
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_next_model_version() -> str:
    """Auto-detect next model version directory."""
    existing = [d.name for d in MODEL_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("v")]
    if not existing:
        return "v1"
    nums = [int(v.lstrip("v")) for v in existing if v.lstrip("v").isdigit()]
    return f"v{max(nums) + 1}" if nums else "v1"
