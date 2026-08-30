# MPLADS AI RiskIntel — AI-Powered MPLADS Anomaly, Fraud & Inefficiency Detection Platform

**Smart India Hackathon 2026 — Problem Statement 102**

An AI-powered monitoring, anomaly detection, cost benchmarking, duplicate work detection, and decision-support analytics platform for the **Members of Parliament Local Area Development Scheme (MPLADS)**, benchmarked against the official **eSAKSHI digital ecosystem** (`https://mplads.mospi.gov.in/`).

> **Key Philosophy**: This platform **NEVER** accuses anyone of fraud. All findings are scored and classified as **"Potential Anomaly / Verification Required"** with multi-signal evidence, serving to guide government officials on where to direct field verification and audit resources.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                                │
│   eSAKSHI CSV/JSON → Synthetic Generator (10,000 records) → Validation     │
├──────────────────────────────────────────────────────────────────────────────┤
│                    MULTI-SIGNAL AI ANALYTICS ENGINE                         │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Rule Engine  │ │ ML Anomaly   │ │ NLP Duplicate│ │ GIS Proximity    │    │
│  │ (5 Rules)    │ │ (Iso Forest) │ │ (TF-IDF+Emb) │ │ (Haversine)      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Agency Risk │ │ Payment vs   │ │ GIS Spiral   │ │ Cost Intelligence│    │
│  │ Profiler    │ │ Progress     │ │ Intelligence │ │ (Market Bench.)  │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Network     │ │ Time Anomaly │ │ Predictive   │ │ Document & Cert. │    │
│  │ Anomaly     │ │ Detection    │ │ AI Forecast  │ │ Intelligence     │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘    │
│  ┌─────────────┐ ┌──────────────┐                                          │
│  │ Image Reuse │ │ National Map │                                          │
│  │ Detection   │ │ Risk Agg.    │                                          │
│  └──────────────┘ └──────────────┘                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│               CENTRAL RISK ENGINE v2.0 (11 Weighted Signals)               │
│          Risk Score (0–100) → Severity Classification → Alerts             │
├──────────────────────────────────────────────────────────────────────────────┤
│                      INTELLIGENCE & UX LAYER                               │
│   Explainable Alerts │ AI Copilot │ National Map │ Investigation Drawer    │
├──────────────────────────────────────────────────────────────────────────────┤
│                    HUMAN-IN-THE-LOOP VERIFICATION                          │
│          Officer Review → Audit Trail → Action Logging                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 All Features (Existing + Planned v2.0)

### ✅ Built & Operational Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Data Quality Engine** | Evaluates raw work records for missing coordinates, sanction dates, incomplete descriptions. Outputs Data Quality Score (0–100%): `Reliable`, `Warning`, `Invalid`. |
| 2 | **Evidence Confidence Score** | Evaluates input data quality, photo proof count, coordinate validity, and multi-signal consensus. Indicates how reliable the evidence is (0–100%). |
| 3 | **Rule-Based Compliance Engine** | 5 deterministic rules: Expenditure > Sanction, Progress Mismatch (>35% gap), Invalid Timeline, Excessive Delay (>180 days), Missing Mandatory Docs. |
| 4 | **ML Statistical Outlier Detection** | Scikit-Learn **Isolation Forest** + **Local Outlier Factor (LOF)** trained on cost deviation ratios, spending velocity, financial-physical gap, and duration ratios. |
| 5 | **NLP Duplicate Work Detection** | TF-IDF N-gram vectorization with cosine similarity. Detects semantically similar work descriptions within geographic proximity. Labels: *"Potentially Similar/Duplicate Work — Verification Required"*. |
| 6 | **GIS Spatial Proximity Engine** | Haversine distance calculation to detect works of identical categories located within 300m. Flags suspicious geographic co-location. |
| 7 | **Implementing Agency Risk Profiler** | **Headline Feature** — Pattern analysis aggregating delay counts, cost anomalies, and financial mismatches across ALL projects managed by an agency. Systemic risk scoring. |
| 8 | **Configurable Risk Policy Engine** | Computes composite Risk Score (0–100) using configurable policy weights. Risk levels: Low (0–25), Medium (26–50), High (51–75), Critical (76–100). |
| 9 | **Explainable Alert Engine** | Generates structured, human-readable narrative explanations for every flagged alert with specific triggering evidence. |
| 10 | **AI Investigation Copilot (सक्षम AI)** | Natural language investigation assistant powered by Google Gemini API with local RAG fallback. Answers queries about works, agencies, risk patterns. |
| 11 | **eSAKSHI-Style Government Dashboard** | Premium, information-dense government UI with hero landing, KPI cards, alerts feed, investigation drawer, agency matrix, and official branding. |
| 12 | **Citizen Request Portal** | Public-facing form for citizens to submit infrastructure complaints and requests. |
| 13 | **Official MP Allocation Database** | Ingests and displays official allocated limits for all 543 Lok Sabha MPs from government Excel data. |
| 14 | **Append-Only Audit Trail** | Immutable log of all officer review actions: Escalated for Inspection, Verified Valid, False Positive, Closed with Notice. |
| 15 | **Multi-Stakeholder Persona Views** | Role-based access for Ministry, State Nodal Authority, District Collector, and MP personas. |

### 🔴 New v2.0 AI Intelligence Modules (To Be Built)

| # | Feature | Description |
|---|---------|-------------|
| 16 | **AI Risk Score with Explanation** | Structured risk score card with radar chart breakdown showing each signal's % contribution. Natural language "Why This Score?" explanation. |
| 17 | **Payment vs Progress Intelligence** | Detects disproportionate financial disbursements vs physical construction progress. Tracks spending velocity, last-minute spikes, and early exhaustion patterns. |
| 18 | **Enhanced Duplicate Detection** | Multi-modal: Sentence-Transformer embeddings + geo-proximity + cost similarity + agency match. Cross-constituency duplicate checking. Side-by-side comparison dossier. |
| 19 | **GIS Spiral Intelligence** | Detects when same type of projects keep getting sanctioned in same area repeatedly — area saturation, temporal spirals, cost escalation spirals, beneficiary overlap. |
| 20 | **Cost Intelligence Engine** | Market rate benchmarking database per category per state. Detects inflated estimates, cost splitting to avoid thresholds, and district-level cost discrepancies. |
| 21 | **Network Anomaly (Contractor Nexus)** | Graph-based analysis detecting agency monopolies (>40% district projects), concurrent overload (>10 simultaneous projects), cross-district nexus, and shell agency patterns. |
| 22 | **Time Anomaly Detection** | Detects impossible timelines, instant completions (<7 days), zombie projects (no update >180 days), fiscal year boundary gaming, backdated sanctions, seasonal impossibilities. |
| 23 | **Predictive AI (Completion Forecast)** | ML-based probability of on-time completion. Predicts expected completion date with confidence interval. Classifications: On Track, At Risk, Likely Delayed, Likely Abandoned. |
| 24 | **Enhanced AI Copilot v2.0** | Structured context retrieval, comparative analysis, drill-down commands, proactive insights, and PDF report generation. Integrates all new engine outputs. |
| 25 | **Document Intelligence** | Verifies mandatory MPLADS paperwork at each stage: MP Recommendation, Sanction Order, Work Order, Utilization Certificate, Completion Report. Detects missing/suspect documents. |
| 26 | **Certificate & Letter Handling** | Tracks lifecycle of official certificates (UCs, NOCs, Completion Certs). Detects duplicate certificate numbers, expired certs, and UC submission gaps. |
| 27 | **Construction Image Analysis** | Perceptual hashing (pHash) for cross-project image reuse detection. Optional progress estimation from photos. EXIF GPS/timestamp validation. |
| 28 | **National Risk Map** | Interactive choropleth map with Green (Low Risk) / Yellow (Watch) / Red (Priority Audit) zone classification per district. Click-to-drill-down: State → District → Projects. |

---

## 📊 Risk Score Formula (v2.0)

The central Risk Engine computes a composite score from **11 weighted signals**:

```
Risk Score = Σ(wᵢ × Sᵢ) for i = 1 to 11
```

| Signal | Engine Module | Weight |
|--------|---------------|--------|
| Rule Compliance | `rule_engine.py` | 0.15 |
| ML Statistical Outlier | `ml_anomaly.py` | 0.12 |
| Payment vs Progress Gap | `payment_progress.py` | 0.12 |
| NLP Duplicate Score | `nlp_duplicate.py` | 0.10 |
| Cost Deviation | `cost_intelligence.py` | 0.10 |
| Delay Risk | `risk_engine.py` | 0.08 |
| Agency Risk | `agency_risk.py` | 0.08 |
| Network Anomaly | `network_anomaly.py` | 0.08 |
| Time Anomaly | `time_anomaly.py` | 0.07 |
| GIS Spiral | `gis_spiral.py` | 0.05 |
| Document Compliance | `document_intelligence.py` | 0.05 |

**Risk Level Classification**:
| Score Range | Level | Action |
|-------------|-------|--------|
| 0–25 | 🟢 Low | Normal monitoring |
| 26–50 | 🟡 Medium | Enhanced monitoring |
| 51–75 | 🟠 High | Priority Review Recommended |
| 76–100 | 🔴 Critical | Immediate Verification Required |

---

## 📈 Empirical Evaluation Metrics

Tested on synthetic dataset with ground-truth labeled anomaly cases:

| Metric | Value |
|--------|-------|
| **Precision** | 0.7607 (76.07%) |
| **Recall** | 0.4837 |
| **F1 Score** | 0.5914 |
| **Total Works Monitored** | 10,000 |
| **Anomaly Detection Rate** | 5% (injected ground truth) |

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **FastAPI** | REST API framework |
| **Scikit-Learn** | Isolation Forest, LOF anomaly detection |
| **Sentence-Transformers** | Semantic text embedding for duplicate detection |
| **NumPy / Pandas** | Data processing & feature engineering |
| **Haversine** | Geospatial distance calculations |
| **Pydantic** | Data validation & schema enforcement |
| **httpx** | Async HTTP client for Gemini API |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool & dev server |
| **Vanilla CSS** | Custom government-style design system |
| **Lucide React** | Icon library |
| **Leaflet.js** | Interactive map rendering |
| **Chart.js / Recharts** | Data visualization charts |
| **D3.js / vis-network** | Force-directed network graph |

### AI & ML
| Technology | Purpose |
|------------|---------|
| **Google Gemini API** | AI Copilot natural language intelligence |
| **TF-IDF + Cosine** | Text similarity baseline |
| **Isolation Forest** | Unsupervised anomaly detection |
| **Random Forest / XGBoost** | Predictive completion forecasting |
| **Perceptual Hashing (pHash)** | Image fingerprinting & reuse detection |

---

## 📁 Repository Structure

```text
SIH 2026/
├── backend/
│   ├── app/
│   │   ├── api/                          # FastAPI REST endpoints
│   │   ├── engine/                       # Multi-Signal AI & Risk Engine Modules
│   │   │   ├── data_quality.py           # ✅ Data Quality & Evidence Confidence
│   │   │   ├── rule_engine.py            # ✅ 5 Compliance Rules
│   │   │   ├── ml_anomaly.py             # ✅ Isolation Forest Statistical Model
│   │   │   ├── nlp_duplicate.py          # ✅ TF-IDF + Semantic Duplicate Detection
│   │   │   ├── gis_proximity.py          # ✅ Haversine Spatial Proximity
│   │   │   ├── agency_risk.py            # ✅ Agency Risk Profiler
│   │   │   ├── risk_engine.py            # ✅ Central Policy Risk Engine (v2.0)
│   │   │   ├── explainability.py         # ✅ Narrative Explanation Generator
│   │   │   ├── payment_progress.py       # 🔴 Payment vs Progress Analyzer
│   │   │   ├── gis_spiral.py             # 🔴 GIS Spiral Intelligence
│   │   │   ├── cost_intelligence.py      # 🔴 Market Cost Benchmarking
│   │   │   ├── network_anomaly.py        # 🔴 Contractor Nexus Detection
│   │   │   ├── time_anomaly.py           # 🔴 Time Anomaly Detection
│   │   │   ├── predictive_ai.py          # 🔴 Completion Forecasting
│   │   │   ├── document_intelligence.py  # 🔴 Document Completeness Checker
│   │   │   ├── certificate_handler.py    # 🔴 Certificate Lifecycle Tracker
│   │   │   ├── image_intelligence.py     # 🔴 Image Analysis & Reuse Detection
│   │   │   └── national_risk_map.py      # 🔴 District/State Risk Aggregation
│   │   ├── schemas/                      # Pydantic data schemas
│   │   ├── services/                     # LLM RAG & Copilot service
│   │   └── main.py                       # FastAPI application entrypoint
│   ├── data/                             # Generated synthetic dataset
│   └── tests/                            # Pytest suite & evaluation metrics
├── frontend/                             # Vite + React + Government UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── AICopilotModal.jsx        # ✅ AI Investigation Copilot
│   │   │   ├── AgencyRiskMatrix.jsx      # ✅ Agency Risk Analytics Table
│   │   │   ├── AshokaStambhaLogo.jsx     # ✅ Official Emblem Component
│   │   │   ├── CitizenRequestModal.jsx   # ✅ Public Citizen Request Form
│   │   │   ├── Footer.jsx               # ✅ Official Government Footer
│   │   │   ├── Header.jsx               # ✅ eSAKSHI Navigation Header
│   │   │   ├── HeroLanding.jsx          # ✅ Hero Landing Page
│   │   │   ├── InvestigationDrawer.jsx  # ✅ Deep-Dive Investigation Panel
│   │   │   ├── LoginModal.jsx           # ✅ eSAKSHI Officer Login
│   │   │   ├── MPAllocatedLimitsTable.jsx # ✅ MP Allocation Database
│   │   │   ├── OverviewCards.jsx        # ✅ Executive KPI Cards
│   │   │   ├── RiskAlertsFeed.jsx       # ✅ Risk Alert Feed Table
│   │   │   ├── RiskScoreCard.jsx        # 🔴 Risk Score Radar Breakdown
│   │   │   ├── PaymentProgressChart.jsx # 🔴 Payment vs Progress Viz
│   │   │   ├── DuplicateComparisonView.jsx # 🔴 Side-by-Side Duplicate View
│   │   │   ├── SpiralMapView.jsx        # 🔴 GIS Spiral Map
│   │   │   ├── CostIntelligencePanel.jsx # 🔴 Cost Benchmark Dashboard
│   │   │   ├── NetworkGraphView.jsx     # 🔴 Agency Nexus Graph
│   │   │   ├── TimelineAnomalyView.jsx  # 🔴 Gantt Timeline Anomalies
│   │   │   ├── PredictiveInsightsPanel.jsx # 🔴 Completion Probability Gauge
│   │   │   ├── DocumentChecklist.jsx    # 🔴 Document Compliance Checklist
│   │   │   ├── CertificateTracker.jsx   # 🔴 Certificate Pipeline Viz
│   │   │   ├── ImageAnalysisPanel.jsx   # 🔴 Construction Image Analysis
│   │   │   └── NationalRiskMap.jsx      # 🔴 Choropleth National Risk Map
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css                    # Design System
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── generate_synthetic_data.py       # 10,000 record eSAKSHI data generator
├── data/                                # Synthetic MPLADS dataset & ground truth
├── docs/                                # Documentation & research
├── tests/                               # Platform-level test suite
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Backend Setup & Running

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate 10,000 realistic synthetic records (if not already generated)
python scripts/generate_synthetic_data.py

# Run FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```

- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

### 2. Frontend Setup & Running

```bash
cd frontend
npm install
npm run dev
```

- **Dashboard UI**: `http://localhost:5173`

### 3. Run Evaluation & Test Suite

```bash
python -m pytest tests/test_platform.py -s
```

---

## 🔌 API Endpoints

### Core Endpoints (Existing)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/overview` | Executive overview KPI statistics |
| `GET` | `/api/v1/works` | Filtered list of works with risk scores |
| `GET` | `/api/v1/works/{work_id}` | Full work detail |
| `GET` | `/api/v1/works/{work_id}/investigation` | Investigation dossier with evidence |
| `GET` | `/api/v1/alerts` | Paginated risk alerts feed |
| `POST` | `/api/v1/alerts/{alert_id}/review` | Officer review submission |
| `GET` | `/api/v1/agencies` | Agency risk profiles |
| `POST` | `/api/v1/analytics/run` | Re-run analytics pipeline |
| `POST` | `/api/v1/copilot/query` | AI Copilot natural language query |
| `GET` | `/api/v1/audit-logs` | Append-only audit trail |
| `GET` | `/api/v1/mps/allocated-limits` | Official MP allocation database |

### New v2.0 Endpoints (Planned)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/works/{id}/payment-progress` | Payment vs Progress analysis |
| `GET` | `/api/v1/works/{id}/prediction` | Predictive AI completion forecast |
| `GET` | `/api/v1/works/{id}/documents` | Document intelligence checklist |
| `GET` | `/api/v1/works/{id}/certificates` | Certificate lifecycle status |
| `GET` | `/api/v1/works/{id}/images` | Image analysis results |
| `GET` | `/api/v1/districts/risk-map` | District-level risk aggregation |
| `GET` | `/api/v1/agencies/{id}/network` | Network anomaly analysis |
| `GET` | `/api/v1/analytics/cost-benchmarks` | Cost intelligence benchmarks |
| `GET` | `/api/v1/analytics/time-anomalies` | Time anomaly summary |
| `GET` | `/api/v1/analytics/spiral-patterns` | GIS spiral detection results |
| `GET` | `/api/v1/analytics/duplicate-clusters` | Enhanced duplicate clusters |

---

## 🗺️ National Risk Map — Zone Classification

The National Risk Map provides a real-time geographic view of MPLADS project health:

| Zone | District Risk Index | Color | Interpretation |
|------|-------------------|-------|----------------|
| **Green Zone** | 0–25 | 🟢 | Low anomaly density. Healthy project execution. Standard monitoring sufficient. |
| **Yellow Zone** | 26–50 | 🟡 | Moderate anomaly density. Watch-list. Enhanced monitoring recommended. |
| **Red Zone** | 51–100 | 🔴 | High anomaly density. Priority audit zone. Field verification required. |

**Features**:
- State-level choropleth coloring
- Click-to-drill-down: State → District → Individual project pins
- Toggle layers: Risk zones, spending heatmap, duplicate clusters, agency footprints
- Search by MP name, constituency, or district

---

## 🤖 AI Copilot (सक्षम AI) — Query Examples

| Query | What It Does |
|-------|-------------|
| "Show all high-risk works" | Lists critical/high risk works with evidence |
| "Financial mismatch in West Bengal" | Filters progress gap anomalies by state |
| "Which agencies are risky?" | Agency risk profiler summary |
| "Compare District Nadia vs Hooghly" | Cross-district cost/risk comparison |
| "Predict completion for MPL-2024-WB-0042" | Completion probability & forecast |
| "Generate risk report for Maharashtra" | Structured state-level risk summary |
| "Network analysis for Agency AG-WB-007" | Contractor nexus investigation |

---

## 📋 MPLADS Scheme Context

- **Full Name**: Members of Parliament Local Area Development Scheme
- **Ministry**: Ministry of Statistics and Programme Implementation (MoSPI)
- **Annual Fund**: ₹5 Crore per MP per year
- **Eligible MPs**: 543 Lok Sabha + 245 Rajya Sabha = 788 MPs
- **Total Annual Outlay**: ~₹3,940 Crore
- **Digital Portal**: eSAKSHI (`https://mplads.mospi.gov.in/`)
- **Work Categories**: Roads, Bridges, Water Supply, Sanitation, Education, Community Halls, Sports Infrastructure, Health Facilities

---

## 👥 Team

**Smart India Hackathon 2026 — Problem Statement 102**

---

## 📄 License

This project is developed for the Smart India Hackathon 2026 competition. All rights reserved.
