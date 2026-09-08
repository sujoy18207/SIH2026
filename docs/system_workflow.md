# MPLADS AI Platform — System Workflow (Mermaid)

> Grounded in the live codebase. Diagrams render on GitHub / any Mermaid-capable viewer.
> Module/endpoint file references: `backend/app/main.py`, `backend/app/etl.py`,
> `ml/run_pipeline.py`, `backend/app/engine/*`, `frontend/src/*`, `frontend/src/apiConfig.js`.

## 1. System Context

```mermaid
flowchart TB
    SRC[(eSAKSHI / mplads.mospi.gov.in<br/>raw CSVs + JSON)]
    ML[(ML artifacts<br/>ml/data/*.csv + ml/models/v1)]
    DB[(SQLite<br/>works · alerts · mp_allocations · vendors · reviews)]
    API[[FastAPI :8000<br/>backend/app/main.py]]
    FE[[React + Vite SPA<br/>frontend :5173]]
    LLM{{Gemini 1.5 Flash<br/>generativelanguage API}}

    SRC -->|python -m backend.app.etl| DB
    SRC -->|python ml/run_pipeline.py| ML
    ML -->|precomputed scores| DB
    DB --> API
    API -->|JSON /api/v1/*| FE
    API -->|retrieval + prompt| LLM
    LLM -->|explanation| FE
```

---

## 2. Offline Ingestion & ML Pipeline

Two offline jobs both feed SQLite. The ML pipeline runs 11 stages; two are skippable
(`--skip-audit`, `--skip-nlp`). Startup then reads only the precomputed DB.

```mermaid
flowchart LR
    subgraph ETL["ETL — backend/app/etl.py (python -m backend.app.etl)"]
        W[load_works] --> CLEAN[clean_text · parse_date ·<br/>derive_work_status · parse_district]
        P[load_payments] --> CLEAN2[clean amount fields]
        M[load_mp_allocations] --> CLEAN3[clean MDMS/limits]
        CLEAN --> DB[(SQLite schema)]
        CLEAN2 --> V[builder vendor_profiles<br/>build_vendor_profiles]
        CLEAN3 --> DB
        V --> DB
    end

    subgraph MLP["ML Pipeline — ml/run_pipeline.py (11 stages)"]
        direction TB
        A1[1 Data Audit] --> A2[2 Data Cleaning]
        A2 --> A3[3 Data Integration]
        A3 --> A4[4 Feature Engineering<br/>ml/models/v1/feature_config.json]
        A4 --> A5[5 Rule Engine<br/>rule_results.csv]
        A4 --> A6[6 NLP Similarity<br/>nlp_duplicate_risk.csv<br/>--skip-nlp opt]
        A4 --> A7[7 GIS Analysis<br/>gis_results.csv]
        A4 --> A8[8 Agency Profiling<br/>agency_risk.csv]
        A5 --> A9[9 Isolation Forest Training<br/>ml_anomaly_scores.csv + model]
        A9 --> A10[10 Model Evaluation<br/>experiments/model_comparison.csv]
        A8 --> A11[11 Composite Risk Engine<br/>risk_scores.csv]
        A6 --> A11
        A7 --> A11
        A10 --> A11
    end

    A5 -.scores.-> DB
    A11 -.composite risk.-> DB
    MLP --> DB
```

---

## 3. Service-Layer Runtime (API) & Risk Aggregation

The FastAPI app (backend/app/main.py) pre-instantiates `RiskEngine` and
`LLMCopilotService`. Analytics results are persisted in SQLite from ETL; `/analytics/run`
re-runs on demand.

```mermaid
flowchart TB
    REQ[Incoming HTTP request<br/>/api/v1/*]
    REQ --> ROUTE{Route dispatcher}

    ROUTE -->|/health| H[health check: counts]
    ROUTE -->|/overview| OV[OverviewStats SQL aggregates<br/>risk/bucket counts, overrun, DQ avg]
    ROUTE -->|/works · /works/{id}| WK[Work queries]
    ROUTE -->|/works/{id}/investigation| INV[Investigation dossier<br/>multi-signal evidence]
    ROUTE -->|/alerts| AL[Scored alert feed]
    ROUTE -->|/alerts/{id}/review| RV[Persist OfficerReview<br/>+ audit-log entry]
    ROUTE -->|/audit-logs · /geo/risk-zones ·<br/>/agencies · /vendors/top · /mps/allocated-limits| AGG[Aggregate views]
    ROUTE -->|/analytics/run| AN[Recompute analytics job]
    ROUTE -->|/copilot/query| CP[LLM copilot]

    H --> DB[(SQLite)]
    OV --> DB
    WK --> DB
    AL --> DB
    RV --> DB
    AGG --> DB
    AN --> DB
    CP --> LLM{{Gemini 1.5 Flash}}
    INV --> ENG[engine: rule_engine · ml_anomaly ·<br/>nlp_duplicate · agency_risk · explainability]
    ENG --> DB
```

---

## 4. Officer Interaction Loop (verification-first)

The core value loop: scan → drill → read evidence → decide → refresh. Framed as
"Potential Anomaly / Verification Required", never accusation.

```mermaid
flowchart TB
    OFF[MoSPI officer / State Nodal / DC / MP office] -->|open dashboard| SCAN
    SCAN[1. Scan national risk<br/>OverviewCards · risk donut · top-states<br/>GET /overview] --> FEED
    FEED[2. Triage alerts feed<br/>GET /alerts?limit=100] --> DRILL
    DRILL[3. Drill into a flagged work<br/>InvestigationDrawer<br/>GET /works/{id}/investigation] --> EVID
    EVID[4. Read multi-signal evidence<br/>explainability: rule + ML + NLP + GIS + DQ]
    EVID --> DM{Verify?}
    DM -->|actions| RV[5. Record OfficerReview<br/>POST /alerts/{id}/review]
    ---> REFRESH[6. Re-run analytics<br/>POST /analytics/run · GET /analytics/status]
    REFRESH --> SCAN

    DM -->|“ask the copilot”| COP[7. AI copilot explains<br/>POST /copilot/query → Gemini]
    COP --> EVID
```

---

## 5. Frontend → Backend Contract

Each view/tab maps to the endpoint(s) it fetches (traced from `App.jsx` + `apiConfig.js`).

```mermaid
flowchart LR
    subgraph UI[React SPA — frontend/src/components]
        HERO[HeroLanding]
        CHARTS[DashboardCharts]
        FEED2[RiskAlertsFeed]
        MAP[GeoRiskMap]
        AG[AgencyRiskMatrix]
        MPS[MPAllocatedLimitsTable]
        INV2[InvestigationDrawer]
        COP2[AICopilotModal]
        HEADER[Header · refresh/persona]
    end

    HERO --> OV[GET /overview]
    CHARTS --> OV
    FEED2 --> AL[GET /alerts]
    MAP --> GEO[GET /geo/risk-zones]
    AG --> AGG[GET /agencies]
    MPS --> LIM[GET /mps/allocated-limits]
    INV2 --> I[GET /works/{id}/investigation]
    INV2 --> RV2[POST /alerts/{id}/review]
    COP2 --> C[POST /copilot/query]
    HEADER --> RUN[POST /analytics/run]

    OV & AL & GEO & AGG & LIM & I & C & RUN --> API{{FastAPI :8000}}
```

---

## 6. Sequence Diagrams — Request Lifecycles

### 6a. Officer drill-down & review (core verification lifecycle)

```mermaid
sequenceDiagram
    autonumber
    participant O as Officer (MoSPI / State / DC / MP)
    participant FE as React SPA (frontend/src)
    participant API as FastAPI :8000 (main.py)
    participant ENG as engine/* (RiskEngine · explainability)
    participant DB as SQLite
    participant LLM as Gemini 1.5 Flash

    O->>FE: open dashboard (Home)
    FE->>API: GET /api/v1/overview
    API->>DB: aggregate counts, risk buckets, overrun, DQ avg
    DB-->>API: OverviewStats
    API-->>FE: stats JSON
    FE-->>O: OverviewCards · risk donut · top-states

    O->>FE: view alerts tab
    FE->>API: GET /api/v1/alerts?limit=100
    API->>DB: query scored alerts (incl. duplicate_candidate_id)
    DB-->>API: alert rows
    API-->>FE: alert feed
    FE-->>O: RiskAlertsFeed

    O->>FE: click a flagged work
    FE->>API: GET /api/v1/works/{id}/investigation
    API->>ENG: compose multi-signal dossier
    ENG->>DB: pull rule/ML/NLP/GIS/DQ signals
    DB-->>ENG: evidence rows
    ENG-->>API: explained dossier
    API-->>FE: investigation payload
    FE->>FE: open InvestigationDrawer
    FE-->>O: “Potential Anomaly / Verification Required” + evidence

    opt ask the copilot
        O->>FE: AICopilotModal / ask query
        FE->>API: POST /api/v1/copilot/query
        API->>LLM: retrieve + Gemini prompt
        LLM-->>API: natural-language explanation
        API-->>FE: answer
        FE-->>O: explanation
    end

    opt record decision
        O->>FE: choose review action
        FE->>API: POST /api/v1/alerts/{id}/review
        API->>DB: persist OfficerReview + audit-log entry
        DB-->>API: ok
        API-->>FE: confirmation
        FE-->>O: review saved
        O->>FE: trigger refresh
        FE->>API: POST /api/v1/analytics/run → GET /analytics/status
        API->>DB: recompute & persist analytics
        API-->>FE: done → refetch overview + alerts
        FE-->>O: refreshed national picture
    end
```

### 6b. LLM copilot query (retrieval + generate)

```mermaid
sequenceDiagram
    autonumber
    participant O as Officer
    participant FE as AICopilotModal
    participant API as FastAPI (llm_service · LLMCopilotService)
    participant DB as SQLite
    participant LLM as Gemini 1.5 Flash

    O->>FE: type question about a work / alert
    FE->>API: POST /api/v1/copilot/query {query}
    alt GEMINI_API_KEY set
        API->>DB: _retrieve context (work + signals)
        DB-->>API: context payload
        API->>LLM: build prompt (context + question)
        LLM-->>API: explanation
        API-->>FE: answer JSON
    else no key (offline fallback)
        API->>DB: _retrieve context
        DB-->>API: context payload
        API-->>FE: local template summary (no external call)
    end
    FE-->>O: rendered explanation
```

---

## 7. Decision Points & Edge Cases

- **Risk bucketing**: rule + ML + NLP + GIS + DQ signals → `Composite Risk Engine` → one of
  Low / Medium / High / Critical; never an accusation, always “verification required”.
- **Duplicate gating**: `nlp_duplicate_risk.csv` marks *candidates*, surfaced only in
  `/alerts` when `duplicate_candidate_id` is set.
- **DB not built**: startup raises `RuntimeError` → run `python -m backend.app.etl` first
  (`main.py` startup_event).
- **Partner LLM absent**: `GEMINI_API_KEY` unset → copilot degrades to retrieval-only local
  summaries (no external call).
- **Analytics re-run**: `POST /analytics/run` recomputes in-memory job state; results
  persist back to SQLite; frontend refetches overview+alerts after completion.
- **Data-quality gaps**: per-work `data_quality_score` feeds explainability and flags
  low-confidence signals rather than suppressing them.
