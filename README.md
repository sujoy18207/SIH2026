# MPLADS AI RiskIntel — AI-Powered MPLADS Anomaly, Fraud & Inefficiency Detection Platform

**Smart India Hackathon 2026 — Problem Statement 102**

An AI-powered monitoring, anomaly detection, cost benchmarking, duplicate work detection, and decision-support analytics platform for the **Members of Parliament Local Area Development Scheme (MPLADS)**, benchmarked against the official **eSAKSHI digital ecosystem** (`https://mplads.mospi.gov.in/`).

---

## 🌟 Key Architectural Refinements & Features

1. **Dashboard Data vs. Work-Level Prototype Data**:
   - **Dashboard Data**: Validated public reference / benchmark aggregate data.
   - **Work-Level Prototype Data**: High-fidelity 10,000-record synthetic dataset (95% normal, 5% injected ground-truth anomalies).
2. **Data Quality Engine**: Evaluates raw work records for missing coordinates, missing sanction dates, incomplete descriptions, and outputs a **Data Quality Score (0–100%)** (`Reliable`, `Warning`, `Invalid`).
3. **Evidence Confidence Score (0–100%)**: Evaluates input data quality, photo proof count, coordinate validity, and multi-signal consensus to indicate evidence reliability.
4. **Streamlined AI Analytics Engine**:
   - **Deterministic Rule Engine**: Compliance & financial boundary checks.
   - **ML Statistical Outlier Engine**: Scikit-Learn **Isolation Forest** trained on cost deviation ratios and spending velocity.
   - **NLP Duplicate Work Detector**: N-gram TF-IDF vectorization & cosine similarity outputting `duplicate_risk_score` and defensive label *"Potentially Similar/Duplicate Work — Verification Required"*.
   - **GIS Spatial Proximity Engine**: Haversine distance spatial clustering.
   - **Agency Risk Profiler**: **Headline Feature** — Pattern analysis aggregating total works, delay counts, cost anomalies, and financial mismatches across all projects managed by an agency.
5. **Configurable Risk Policy Engine**: Computes composite Risk Score ($0-100$) using policy weights, triggering **"Priority Review Recommended"** alerts (decision support, not autonomous decisions).
6. **Append-Only Audit Trail**: Immutable log recording officer verification actions (*Escalated for Site Inspection*, *Verified Valid*, *False Positive*, *Closed with Notice*).
7. **Clean Government Software UX**: Information-dense, accessible visual layout prioritizing readability, clear tables, interactive drawers, map overlays, and executive KPI cards.

---

## 📊 Empirical Evaluation Metrics

Tested on synthetic dataset with ground-truth labeled anomaly cases:
- **Precision**: `0.7607` (76.07% true positive anomaly precision)
- **Recall**: `0.4837`
- **F1 Score**: `0.5914`

---

## 📁 Repository Structure

```text
SIH 2026/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── engine/          # Multi-Signal AI & Risk Engine Modules
│   │   │   ├── data_quality.py      # Data Quality & Evidence Confidence Engines
│   │   │   ├── rule_engine.py       # Compliance rules
│   │   │   ├── ml_anomaly.py        # Isolation Forest statistical model
│   │   │   ├── nlp_duplicate.py     # TF-IDF duplicate risk score
│   │   │   ├── gis_proximity.py     # Haversine spatial proximity
│   │   │   ├── agency_risk.py       # Headline agency risk profiler
│   │   │   ├── risk_engine.py       # Configurable Policy Risk Engine
│   │   │   └── explainability.py    # Narrative explanation generator
│   │   ├── schemas/         # Pydantic data schemas
│   │   ├── services/        # LLM RAG & Copilot service
│   │   └── main.py          # FastAPI application entrypoint
│   └── tests/               # Pytest suite & evaluation metrics
├── frontend/                # Vite + React + Clean Government UI
│   ├── src/
│   │   ├── components/      # Executive Cards, Alerts Feed, Drawer, Copilot
│   │   ├── App.jsx
│   │   └── index.css        # Information-dense CSS design system
├── scripts/
│   └── generate_synthetic_data.py # 10,000 record eSAKSHI data generator
└── data/                    # Generated synthetic MPLADS dataset & ground truth labels
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup & Running
```bash
# Generate 10,000 realistic synthetic records
python scripts/generate_synthetic_data.py

# Run FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`

### 2. Frontend Setup & Running
```bash
cd frontend
npm run dev
```
- Dashboard UI: `http://localhost:5173`

### 3. Run Evaluation & Test Suite
```bash
python -m pytest tests/test_platform.py -s
```
