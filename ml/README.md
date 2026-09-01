# MPLADS Anomaly Detection & Risk Intelligence ML Pipeline

**Smart India Hackathon 2026 — Problem Statement PS-102**

An unsupervised machine learning and compliance intelligence pipeline designed for eSAKSHI/MPLADS public dataset analysis.

> **IMPORTANT DISCLAIMER**: The system does NOT claim to prove fraud or establish illegal activity automatically. Its objective is to detect unusual/anomalous project patterns, combine multi-source evidence signals, calculate an explainable 0–100 risk score, and prioritize projects for human government officer review.

---

## 🏗 Architecture & Core Design

```
eSAKSHI CSV Data
     │
     ▼
Data Ingestion & Cleaning (data_cleaning.py)
     │
     ▼
Unified Master Project Table (data_integration.py)
     │
     ▼
Feature Engineering (feature_engineering.py)
     │
 ┌───┴────────────────────────┬────────────────────────┬────────────────────────┐
 │                            │                        │                        │
 ▼                            ▼                        ▼                        ▼
Rule Engine             Isolation Forest         NLP Similarity          Agency Profiler
(rule_engine.py)        (train_isolation...)    (nlp_similarity.py)     (agency_profiler.py)
 │                            │                        │                        │
 └───────────┬────────────────┴────────────────────────┴────────────────────────┘
             │
             ▼
Composite Risk Fusion Engine (risk_engine.py)
             │
             ▼
Explainable 0–100 Risk Score + Data Quality Score + Top Reasons
             │
             ▼
FastAPI REST API Service (api_server.py) / PostgreSQL DB (schema.sql)
```

---

## 📊 Dataset Overview (Audited Real eSAKSHI Data)

- **Total CSV Files**: 14 files (~160 MB CSV / ~310 MB JSON)
- **Works Recommended**: 131,049 records
- **Works Sanctioned**: 100,038 records
- **Works Completed**: 45,472 records
- **Expenditure Records**: 107,828 disbursement records
- **Primary Common Identifier**: `WORK_RECOMMENDATION_DTL_ID` (75.4% overlap between recommendations and sanctions)

### ⚠️ Field Availability Matrix

| Feature / Field | Status | Source Column |
|-----------------|--------|---------------|
| Sanctioned Amount | Available | `SANCTION_AMOUNT` |
| Recommended Amount | Available | `RECOMMENDED_AMOUNT` |
| Total Expenditure | Available | `FUND_DISBURSED_AMT` (aggregated) |
| Recommendation Date | Available | `RECOMMENDATION_DATE` |
| Sanction Date | Available | `SANCTION_DATE` |
| Actual Completion Date | Available | `ACTUAL_END_DATE` |
| Vendor Name / ID | Available | `VENDOR_NAME`, `VENDOR_ID` |
| District Authority | Available | `IDA_NAME` |
| Work Description | Available | `WORK_DESCRIPTION` |
| **GPS Coordinates** | **UNAVAILABLE** | *Marked unavailable — GIS module stubbed* |
| **Physical Progress %** | **UNAVAILABLE** | *Marked unavailable* |
| **Financial Progress %**| **UNAVAILABLE** | *Marked unavailable* |
| **Photo Count** | **UNAVAILABLE** | *Marked unavailable* |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r ml/requirements.txt
```

### 2. Run the Full ML Pipeline

```bash
python ml/run_pipeline.py
```

Options:
- `--skip-audit`: Skip dataset audit step
- `--skip-nlp`: Skip NLP text similarity step (for faster runs)

### 3. Run FastAPI Service

```bash
python ml/src/api_server.py
```

Interactive API documentation available at: `http://localhost:8000/docs`

---

## 📐 Mathematical Formulas

### 1. Cost Deviation
$$\text{CostDeviation} = \frac{\text{TotalExpenditure} - \text{SanctionAmount}}{\text{SanctionAmount}}$$

### 2. Expenditure Ratio
$$\text{ExpenditureRatio} = \frac{\text{TotalExpenditure}}{\text{SanctionAmount}}$$

### 3. Peer-Relative Spending Velocity Ratio
$$\text{VelocityRatio} = \frac{\text{SpendingVelocity}_{\text{project}}}{\text{Median}(\text{SpendingVelocity}_{\text{peer group}})}$$

### 4. TF-IDF Text Vectorization
$$\text{TF-IDF}(t,d) = \text{TF}(t,d) \times \log\left(\frac{N}{\text{DF}(t)}\right)$$

### 5. Cosine Similarity
$$\text{CosineSimilarity}(A,B) = \frac{A \cdot B}{\|A\| \|B\|}$$

### 6. Isolation Forest Normalization
$$\text{MLAnomalyRisk} = 100 \times \left(1 - \frac{s - s_{\min}}{s_{\max} - s_{\min}}\right)$$
*where $s$ is the decision function score (more negative = more anomalous).*

### 7. Dynamic Composite Risk Score
$$\text{FinalRisk} = \frac{\sum_{i \in \text{Available}} w_i \times S_i}{\sum_{i \in \text{Available}} w_i}$$
*Weights: RuleRisk (0.30), MLAnomalyRisk (0.30), DuplicateRisk (0.20), AgencyRisk (0.20).*

---

## 🚦 Risk Categories & Interpretation

| Risk Range | Category | Interpretation | Recommended Action |
|------------|----------|----------------|-------------------|
| **0 – 29** | 🟢 **LOW** | Normal patterns | Routine monitoring |
| **30 – 59** | 🟡 **MEDIUM** | Minor compliance indicators | Soft alert |
| **60 – 79** | 🟠 **HIGH** | Significant statistical anomaly | Prioritized review |
| **80 – 100** | 🔴 **CRITICAL** | Multiple severe indicators | Immediate desk audit |

---

## 📡 API Endpoints

- `GET /health` — Service health check
- `GET /projects/{project_id}/risk` — Detailed risk breakdown for single project
- `GET /risks/high` — List high-risk projects with optional state filter
- `GET /risks/critical` — List critical-risk projects
- `GET /analytics/summary` — Aggregate portfolio risk summary
- `POST /model/retrain` — Trigger model retraining pipeline (requires secret header `X-Api-Key`)

---

## 🗄 Zero-Setup SQLite Database Integration

The pipeline includes built-in SQLite database support requiring **zero server setup**.

### 1. Populate Local SQLite Database (`ml/data/mplads.db`)

```bash
python ml/src/db_loader.py
```

This creates a single-file SQLite database at [`ml/data/mplads.db`](file:///c:/SIH%202026/ml/data/mplads.db) containing all 6 tables and 128,081 records with optimized SQL indexes.

### 2. Optional: Load into PostgreSQL / MySQL

If you prefer PostgreSQL or another RDBMS, use the SQLAlchemy DB URL flag:

```bash
python ml/src/db_loader.py --db-url postgresql://user:password@localhost:5432/mplads_db
```

---

## 📂 Project Structure

```
ml/
├── data/                    # Processed CSVs & features
│   ├── cleaned/             # Cleaned eSAKSHI datasets
│   ├── master_projects.csv  # Unified project master table
│   ├── features.csv         # Feature matrix
│   ├── rule_results.csv     # Rule engine output
│   ├── ml_anomaly_scores.csv# Isolation Forest scores
│   ├── nlp_duplicate_risk.csv# Duplicate text scores
│   └── risk_scores.csv      # Composite final risk scores
├── experiments/             # Hyperparameter tuning logs
├── models/                  # Versioned trained model artifacts
│   └── v1/
│       ├── isolation_forest.joblib
│       ├── preprocessing_scaler.joblib
│       ├── preprocessing_imputer.joblib
│       ├── feature_config.json
│       └── model_metadata.json
├── reports/                 # JSON/CSV audit & evaluation reports
├── src/                     # Core Python modules
│   ├── config.py            # Centralized configuration
│   ├── data_audit.py        # Data audit script
│   ├── data_cleaning.py     # Data cleaning pipeline
│   ├── data_integration.py # Master table builder
│   ├── feature_engineering.py# Feature calculation
│   ├── rule_engine.py       # Deterministic rule engine
│   ├── nlp_similarity.py    # TF-IDF duplicate text detection
│   ├── gis_analysis.py      # Spatial analysis stub (no GPS in data)
│   ├── agency_profiler.py   # Agency historical risk profiler
│   ├── train_isolation_forest.py # Model trainer
│   ├── evaluate_model.py    # Model evaluation & stability
│   ├── predict_risk.py      # Inference predictor
│   ├── risk_engine.py       # Composite risk fusion engine
│   ├── api_server.py        # FastAPI server
│   └── db_loader.py         # PostgreSQL loader
├── schema.sql               # PostgreSQL DDL
├── run_pipeline.py          # End-to-end pipeline runner
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```
