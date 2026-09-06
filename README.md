# MPLADS AI RiskIntel — AI-Powered MPLADS Anomaly, Fraud & Inefficiency Detection Platform

**Smart India Hackathon 2026 — Problem Statement 102**

An AI-powered monitoring, anomaly detection, cost benchmarking, duplicate work detection, and decision-support analytics platform for the **Members of Parliament Local Area Development Scheme (MPLADS)**, running on the **REAL eSAKSHI dataset scraped from the official portal** (`https://mplads.mospi.gov.in/`).

> **Key Philosophy**: This platform **NEVER** accuses anyone of fraud. All findings are scored and classified as **"Potential Anomaly / Verification Required"** with multi-signal evidence, serving to guide government officials on where to direct field verification and audit resources.

> **Real Data**: No synthetic/test records. The platform operates on the genuine scraped eSAKSHI dataset: **1,28,670 works** (Lok Sabha + Rajya Sabha, all tenures), **1,07,828 vendor payment records**, **776 MP allocation records** (543 Lok Sabha + 233 Rajya Sabha), and **27,961 unique vendors**, served from a persistent SQLite database on a long-lived server (Docker deployment) — the dataset is far too large for serverless functions.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    REAL DATA INGESTION LAYER (eSAKSHI CSVs)                  │
│  works_recommended / sanctioned / completed / expenditure (LS + RS)          │
│  → ETL (backend/app/etl.py) → SQLite: works | payments | vendors | mps        │
├──────────────────────────────────────────────────────────────────────────────┤
│                    MULTI-SIGNAL AI ANALYTICS ENGINE                          │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐      │
│  │ Rule Engine  │ │ ML Anomaly   │ │ NLP Duplicate│ │ Vendor Concentr. │      │
│  │ (9 Rules)    │ │ (Iso Forest) │ │ (TF-IDF+Hash) │ │ (Nexus Signal)   │      │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘      │
│  ┌─────────────┐ ┌──────────────┐                                    │
│  │ Agency Risk │ │ Data Quality │                                     │
│  │ Profiler    │ │ + Confidence │                                     │
│  └─────────────┘ └──────────────┘                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│           CENTRAL RISK ENGINE (5 Weighted Signals, 0–100 Score)             │
│          Risk Score → Severity Classification → Explainable Alerts          │
│                     (persisted to SQLite alerts table)                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                      INTELLIGENCE & UX LAYER                                │
│   Explainable Alerts │ AI Copilot (सक्षम AI) │ Investigation Drawer         │
├──────────────────────────────────────────────────────────────────────────────┤
│                    HUMAN-IN-THE-LOOP VERIFICATION                          │
│       Officer Review → Persistent Audit Trail (SQLite) → Action Log          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Features (All Operational on Real Data)

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Real eSAKSHI Data Pipeline** | ETL joins works recommended → sanctioned → completed → vendor payments on `WORK_RECOMMENDATION_DTL_ID`; cleans scraped fields (embedded tabs, broken multiline dates); parses districts from IDA names. |
| 2 | **Data Quality Engine** | Evaluates real records for missing descriptions, absent sanction dates on advanced stages, non-positive amounts, missing completion dates. Outputs Data Quality Score (0–100%): `Reliable`, `Warning`, `Invalid`. |
| 3 | **Evidence Confidence Score** | Factors payment-trail richness, attached sanction files, and multi-signal consensus (0–100%). |
| 4 | **Rule-Based Compliance Engine** | 9 deterministic rules on real fields: disbursed > sanction, multi-vendor splitting of a single sanction, completion cost overrun, sanction ≤ recommendation date, completion < sanction date, zombie works (>2yr stalled), completed with zero payments, advanced stage without file evidence, unverified completions (no rating). |
| 5 | **Multi-Vendor Splitting Detection** | Flags single sanctions paid to 4+ distinct vendors — cost-splitting to circumvent procurement thresholds (real signal found in the live dataset). |
| 6 | **ML Statistical Outlier Detection** | Scikit-Learn **Isolation Forest** trained on real features: sanction cost deviation vs (activity × state) median, disbursal ratio, actual-vs-sanction deviation, sanction/completion durations, payment concentration. |
| 7 | **NLP Duplicate Work Detection** | Exact normalized-description grouping + TF-IDF n-gram cosine similarity, blocked by (state, district); amount-proximity boosted scoring. Labels: *"Potentially Similar/Duplicate Work — Verification Required"*. **18K+ real candidates detected.** |
| 8 | **Vendor Concentration (Contractor Nexus)** | Profiles all 27,961 vendors from the real payment ledger — e.g. a single vendor paid across **785 distinct works** is surfaced as a priority procurement-fairness verification signal. |
| 9 | **District Authority Risk Profiler** | **Headline Feature** — pattern analysis aggregating stalled works, cost variance, and anomaly counts across ALL projects under an Integrated District Authority (IDA). |
| 10 | **Configurable Risk Policy Engine** | Composite Risk Score (0–100) from weighted signals. Risk levels: Low (0–25), Medium (26–50), High (51–75), Critical (76–100). |
| 11 | **Explainable Alert Engine** | Structured narrative explanations with exact amounts, dates, stages, and evidence for every flagged alert. |
| 12 | **AI Investigation Copilot (सक्षम AI)** | Natural language assistant over the real dataset (states, districts, agencies, vendors, duplicates) powered by Google Gemini API with deterministic SQL-backed local fallback. |
| 13 | **eSAKSHI-Style Government Dashboard** | Premium information-dense government UI with hero landing, KPI cards, alerts feed, investigation drawer, agency matrix, dark-navy collapsible sidebar, and official branding. |
| 19 | **Geographic Risk Map (Leaflet)** | Interactive national risk map over all 36 states/UTs — state-level markers sized/colored by real multi-signal aggregates from `/api/v1/geo/risk-zones` (works monitored, high-risk flags, avg composite score, disbursements, districts); street/satellite/OSM tiles; click-through drill-down into each state's highest-risk work dossier. |
| 14 | **Citizen Request Portal** | Public form with real state/MP dropdowns loaded live from the MP allocation database. |
| 15 | **Official MP Allocation Database** | Real allocated limits for 776 MP records (543 Lok Sabha + 233 Rajya Sabha, including 11 Nominated RS members) from the eSAKSHI dataset. |
| 16 | **Persistent Append-Only Audit Trail** | Officer reviews recorded in SQLite — survives server restarts. Actions: Escalated for Inspection, Verified Valid, False Positive, Closed with Notice. |
| 17 | **Vendor Payment Ledger Dossier** | Every investigation drawer shows the actual eSAKSHI vendor payment rows (date, vendor, amount, status) for the work. |
| 18 | **Persistent Server Deployment** | Docker + docker-compose (FastAPI + nginx) with volume-persisted SQLite — sized for the real 128K-work dataset. |

> **Not applicable to current data**: GPS-based GIS proximity and physical/financial progress-percentage rules were part of the v1 synthetic prototype; the real eSAKSHI extracts contain no coordinates or progress percentages, so those engines were replaced with the real-data detectors above (multi-vendor splitting, vendor concentration, stage-stalled analytics).

---

## 📊 Risk Score Formula

The central Risk Engine computes a composite score from **5 weighted signal groups**:

```
Risk Score = 0.35·Rule + 0.25·ML + 0.20·Duplicate + 0.10·Timeline + 0.10·Authority
```

| Signal Group | Engine Module | Weight |
|--------|---------------|--------|
| Rule Compliance (top rule score) | `rule_engine.py` | 0.35 |
| ML Statistical Outlier | `ml_anomaly.py` | 0.25 |
| NLP Duplicate Score | `nlp_duplicate.py` | 0.20 |
| Timeline Risk (zombie/impossible dates) | `rule_engine.py` | 0.10 |
| District Authority Risk | `agency_risk.py` | 0.10 |

**Risk Level Classification**:
| Score Range | Level | Action |
|-------------|-------|--------|
| 0–25 | 🟢 Low | Normal monitoring |
| 26–50 | 🟡 Medium | Enhanced monitoring |
| 51–75 | 🟠 High | Priority Review Recommended |
| 76–100 | 🔴 Critical | Immediate Verification Required |

---

## 📈 Real Dataset Scale & Detected Signals

| Metric | Value |
|--------|-------|
| **Total Works Monitored** | 1,28,670 (1,03,554 Lok Sabha + 25,116 Rajya Sabha) |
| **Vendor Payment Records** | 1,07,828 |
| **Total Vendor Disbursements** | ₹3,969 Crore |
| **MP Allocation Records** | 776 (543 Lok Sabha + 233 Rajya Sabha) |
| **Unique Vendors** | 27,961 |
| **States / UTs Covered** | 36 |
| **Districts Covered** | 773 |
| **District Authorities Profiled** | 776 |
| **Explainable Alerts Generated** | 48,305 |
| **NLP Duplicate Candidates** | 18,133 (7,654 duplicate clusters) |
| **Zombie Works (2+ yrs stalled)** | 5,523 |
| **Impossible Timelines Detected** | 246 |
| **Completed Without Payments** | 832 |
| **ML Statistical Outliers** | 500 |
| **Unverified Completions (no rating)** | 14,266 |
| **Advanced Stage Without File Evidence** | 27,412 |
| **Multi-Vendor Splitting Sanctions** | 1,351 |
| **Top Vendor Concentration** | 1 vendor paid across 785 distinct works |

### Detected Signals by Engine (live database)

| Signal Type | Works Flagged | Engine |
|-------------|---------------|--------|
| `RULE_MISSING_EVIDENCE` — advanced stage without file evidence | 27,412 | Rule Engine |
| `NLP_DUPLICATE_WORK` — potentially similar/duplicate works | 18,133 | NLP Engine |
| `RULE_UNVERIFIED_COMPLETION` — completed with no rating | 14,266 | Rule Engine |
| `RULE_ZOMBIE_WORK` — stage-stuck > 2 years | 5,523 | Rule Engine |
| `RULE_VENDOR_SPLITTING` — single sanction, 4+ vendors | 1,351 | Rule Engine |
| `RULE_COMPLETED_NO_PAYMENTS` — completed, zero vendor payments | 832 | Rule Engine |
| `ML_STATISTICAL_OUTLIER` — multivariate cost/duration outlier | 500 | Isolation Forest |
| `RULE_TIMELINE_INCONSISTENT` — impossible sanction/completion dates | 246 | Rule Engine |

**Risk-level distribution across all 1,28,670 works**: 🟢 Low: 87,250 · 🟡 Medium: 38,378 · 🟠 High: 3,036 · 🔴 Critical: 6

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.12** | Core language |
| **FastAPI** | REST API framework |
| **SQLite (WAL)** | Persistent storage for the real dataset — scales to millions of rows, zero admin |
| **Scikit-Learn** | Isolation Forest anomaly detection + TF-IDF vectorization |
| **NumPy / Pandas** | Feature engineering |
| **Pydantic** | Data validation & schema enforcement |
| **httpx** | Async HTTP client for Gemini API |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **Vite** | Build tool & dev server |
| **Vanilla CSS** | Custom government-style design system |
| **Lucide React** | Icon library |

### AI
| Technology | Purpose |
|------------|---------|
| **Google Gemini API** | AI Copilot natural language intelligence (optional; local engine works without it) |
| **TF-IDF + Cosine Similarity** | Duplicate description detection |
| **Isolation Forest** | Unsupervised multivariate anomaly detection |

### Deployment
| Technology | Purpose |
|------------|---------|
| **Docker + docker-compose** | Persistent server deployment (dataset too large for serverless) |
| **nginx** | Static frontend hosting + reverse proxy to API |

---

## 📁 Repository Structure

```text
SIH2026/
├── backend/
│   ├── app/
│   │   ├── db.py                         # SQLite schema + connection layer
│   │   ├── etl.py                        # Real eSAKSHI CSV → SQLite ETL + analytics
│   │   ├── main.py                       # FastAPI application
│   │   ├── engine/
│   │   │   ├── data_quality.py           # Data Quality & Evidence Confidence
│   │   │   ├── rule_engine.py            # 9 real-data compliance rules
│   │   │   ├── ml_anomaly.py             # Isolation Forest on real features
│   │   │   ├── nlp_duplicate.py          # Exact-hash + TF-IDF duplicate detection
│   │   │   ├── agency_risk.py            # District Authority risk profiler
│   │   │   ├── risk_engine.py            # Central weighted risk engine
│   │   │   └── explainability.py         # Narrative explanation generator
│   │   ├── schemas/mplads.py             # Pydantic schemas (real fields)
│   │   └── services/llm_service.py       # AI Copilot (Gemini + local SQL engine)
│   └── data/                             # Built mplads.db (gitignored; built by ETL)
├── data/
│   └── mplads_data/csv/                  # REAL eSAKSHI scraped dataset (14 CSVs)
├── frontend/                             # Vite + React government UI
│   ├── nginx.conf                        # Static hosting + /api/ reverse proxy
│   └── src/components/                   # HeroLanding, OverviewCards, RiskAlertsFeed,
│       │                                 #   InvestigationDrawer, AgencyRiskMatrix,
│       │                                 #   MPAllocatedLimitsTable, AICopilotModal,
│       │                                 #   CitizenRequestModal, LoginModal
│       └── apiConfig.js                  # Dev/prod API base routing
├── scripts/
│   └── generate_pdf_dossier.py           # Problem-statement dossier generator
├── tests/
│   └── test_platform.py                  # Engine + database + API test suite
├── docs/
│   └── MPLADS_AI_RiskIntel_SIH2026_PS102_Dossier.pdf
├── Dockerfile                            # Backend (FastAPI + SQLite + ETL entrypoint)
├── frontend/Dockerfile                   # Frontend (nginx static + API proxy)
├── docker-compose.yml                    # Persistent-server deployment
├── implementation_plan.md                # v2.0 planning document
└── requirements.txt
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (for deployment)

### 1. Build the database from the real CSVs (one-time, ~3 minutes)

```bash
pip install -r requirements.txt
PYTHONPATH=backend python -m app.etl
```

This parses the 14 real eSAKSHI CSVs, builds `backend/data/mplads.db`, and runs the full multi-signal analytics pipeline (rules + Isolation Forest + NLP duplicates + authority profiling) over all 128K works.

### 2. Run the backend

```bash
PYTHONPATH=backend python -m uvicorn app.main:app --port 8000
```

- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

- **Dashboard UI**: `http://localhost:5173`

### 4. Run the test suite (15 tests: engines + real database + API)

```bash
PYTHONPATH=backend:. python -m pytest tests/test_platform.py -s
```

### 5. Production deployment (persistent server)

```bash
docker compose up --build -d
```

- **Frontend**: `http://<host>:3000`
- **API**: `http://<host>:8000` (also proxied at `http://<host>:3000/api/`)

On first boot the API container runs the ETL automatically (if the database volume is empty) and then serves; subsequent boots start instantly from the persisted SQLite volume. Set `GEMINI_API_KEY` in the environment (or a `.env` file) to enable the Gemini-powered copilot.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Service health check with real dataset counts |
| `GET` | `/api/v1/overview` | Executive overview KPI statistics |
| `GET` | `/api/v1/works` | Filtered list of works (state, district, house, status, risk level, search, pagination) |
| `GET` | `/api/v1/works/{work_id}` | Full work detail |
| `GET` | `/api/v1/works/{work_id}/investigation` | Investigation dossier: work + alert + duplicate candidate + authority profile + **vendor payment ledger** + review history |
| `GET` | `/api/v1/alerts` | Paginated risk alerts feed (filter by risk level / signal type) |
| `POST` | `/api/v1/alerts/{alert_id}/review` | Officer review submission (persisted) |
| `GET` | `/api/v1/audit-logs` | Append-only audit trail |
| `GET` | `/api/v1/agencies` | District authority risk profiles |
| `GET` | `/api/v1/geo/risk-zones` | State-level risk aggregates for the National Risk Map (works, high-risk flags, avg score, disbursements, districts) |
| `GET` | `/api/v1/vendors/top` | Vendor payment concentration (contractor nexus signal) |
| `POST` | `/api/v1/analytics/run` | Re-run the analytics pipeline in the background |
| `GET` | `/api/v1/analytics/status` | Analytics job status |
| `POST` | `/api/v1/copilot/query` | AI Copilot natural language query |
| `GET` | `/api/v1/mps/allocated-limits` | Official MP allocation database (both houses, filterable) |

---

## 🤖 AI Copilot (सक्षम AI) — Query Examples

| Query | What It Does |
|-------|--------------|
| "Show all high-risk works" | Lists critical/high risk works with real evidence |
| "Analysis for Uttar Pradesh" | State-level real aggregates + drill-down |
| "Analysis for Jaunpur district" | District-level risk and financial summary |
| "Which authorities are risky?" | District authority risk profiler summary |
| "Vendor concentration analysis" | Contractor nexus — top vendors by works paid |
| "Show duplicate works" | NLP duplicate candidates with scores |

---

## 📋 MPLADS Scheme Context

- **Full Name**: Members of Parliament Local Area Development Scheme
- **Ministry**: Ministry of Statistics and Programme Implementation (MoSPI)
- **Annual Fund**: ₹5 Crore per MP per year
- **Eligible MPs**: 543 Lok Sabha + 245 Rajya Sabha = 788 MPs (the scraped allocation extract covers 776: 543 LS + 233 RS, including 11 Nominated members)
- **Digital Portal**: eSAKSHI (`https://mplads.mospi.gov.in/`)
- **Work Stages** (as recorded in the real dataset): Pending for Sanction → Sanction → Vendor Identification → Physical Inspection → Time Estimation → Work partially Completed / Work Completed

---

## 👥 Team

**Smart India Hackathon 2026 — Problem Statement 102**

---

## 📄 License

This project is developed for the Smart India Hackathon 2026 competition. All rights reserved.
