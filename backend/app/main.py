"""
FastAPI Backend Application for MPLADS Anomaly & Risk Detection Platform
"""

import json
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.schemas.mplads import (
    OverviewStats, WorkBase, ExplainableAlert, OfficerReview, AgencyProfile, ReviewAction
)
from backend.app.engine.risk_engine import RiskEngine
from backend.app.services.llm_service import LLMCopilotService

app = FastAPI(
    title="MPLADS AI Anomaly & Risk Detection Platform API",
    description="AI-powered monitoring, fraud detection, cost benchmarking, duplicate work detection & decision-support API for MPLADS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join("data", "mplads_synthetic_dataset.json")
RAW_WORKS: List[Dict[str, Any]] = []
ANALYZED_WORKS: List[Dict[str, Any]] = []
ALERTS_MAP: Dict[str, ExplainableAlert] = {}
AGENCY_PROFILES_MAP: Dict[str, AgencyProfile] = {}
REVIEWS_STORE: Dict[str, Dict[str, Any]] = {}
AUDIT_LOGS: List[Dict[str, Any]] = []

risk_engine = RiskEngine()
llm_service = LLMCopilotService()


def load_and_analyze_dataset():
    global RAW_WORKS, ANALYZED_WORKS, ALERTS_MAP, AGENCY_PROFILES_MAP
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            RAW_WORKS = json.load(f)
    else:
        from scripts.generate_synthetic_data import generate_synthetic_dataset
        RAW_WORKS, _ = generate_synthetic_dataset(10000)

    alerts, agency_profiles, analyzed_works = risk_engine.analyze_all_works(RAW_WORKS)
    
    ANALYZED_WORKS = analyzed_works
    ALERTS_MAP = {a.alert_id: a for a in alerts}
    AGENCY_PROFILES_MAP = agency_profiles
    print(f"[API Startup] Analyzed {len(ANALYZED_WORKS)} works. Generated {len(ALERTS_MAP)} explainable alerts.")


@app.on_event("startup")
def startup_event():
    load_and_analyze_dataset()


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "monitored_works": len(ANALYZED_WORKS), "active_alerts": len(ALERTS_MAP)}


@app.get("/api/v1/overview", response_model=OverviewStats)
def get_overview_stats():
    total_w = len(ANALYZED_WORKS)
    rec_amt = sum(w.get("estimated_cost", 0) for w in ANALYZED_WORKS)
    sanc_amt = sum(w.get("sanctioned_amount", 0) for w in ANALYZED_WORKS)
    exp_amt = sum(w.get("expenditure", 0) for w in ANALYZED_WORKS)

    completed_cnt = sum(1 for w in ANALYZED_WORKS if w.get("work_status") == "Completed")
    in_prog_cnt = sum(1 for w in ANALYZED_WORKS if w.get("work_status") == "In Progress")
    
    high_cnt = sum(1 for w in ANALYZED_WORKS if w.get("risk_level") == "High")
    crit_cnt = sum(1 for w in ANALYZED_WORKS if w.get("risk_level") == "Critical")

    cost_overrun_val = sum(
        max(0.0, w.get("expenditure", 0) - w.get("sanctioned_amount", 0))
        for w in ANALYZED_WORKS
    )
    
    dup_cnt = sum(1 for a in ALERTS_MAP.values() if a.duplicate_candidate_id)
    avg_dq = sum(w.get("data_quality_score", 100.0) for w in ANALYZED_WORKS) / max(1, total_w)

    return OverviewStats(
        total_works=total_w,
        total_recommended_amount=round(rec_amt, 2),
        total_sanctioned_amount=round(sanc_amt, 2),
        total_expenditure_amount=round(exp_amt, 2),
        completed_works_count=completed_cnt,
        in_progress_works_count=in_prog_cnt,
        high_risk_works_count=high_cnt,
        critical_risk_works_count=crit_cnt,
        potential_cost_overrun_val=round(cost_overrun_val, 2),
        duplicate_candidates_count=dup_cnt,
        avg_data_quality_score=round(avg_dq, 1)
    )


@app.get("/api/v1/works")
def list_works(
    state: Optional[str] = None,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    house: Optional[str] = None,
    work_category: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    filtered = list(ANALYZED_WORKS)

    if state:
        filtered = [w for w in filtered if w.get("state") == state]
    if district:
        filtered = [w for w in filtered if w.get("district") == district]
    if constituency:
        filtered = [w for w in filtered if w.get("constituency") == constituency]
    if house:
        filtered = [w for w in filtered if w.get("house") == house]
    if work_category:
        filtered = [w for w in filtered if w.get("work_category") == work_category]
    if risk_level:
        filtered = [w for w in filtered if w.get("risk_level") == risk_level]
    if search:
        s_low = search.lower()
        filtered = [
            w for w in filtered
            if s_low in w.get("work_id", "").lower()
            or s_low in w.get("work_description", "").lower()
            or s_low in w.get("mp_name", "").lower()
            or s_low in w.get("implementing_agency_name", "").lower()
        ]

    total = len(filtered)
    paged = filtered[offset : offset + limit]

    return {"total": total, "limit": limit, "offset": offset, "works": paged}


@app.get("/api/v1/works/{work_id}")
def get_work_by_id(work_id: str):
    for w in ANALYZED_WORKS:
        if w["work_id"] == work_id:
            return w
    raise HTTPException(status_code=404, detail=f"Work {work_id} not found")


@app.get("/api/v1/works/{work_id}/investigation")
def get_work_investigation_dossier(work_id: str):
    work = None
    for w in ANALYZED_WORKS:
        if w["work_id"] == work_id:
            work = w
            break
    if not work:
        raise HTTPException(status_code=404, detail=f"Work {work_id} not found")

    alert_obj = ALERTS_MAP.get(f"ALT-{work_id}")
    
    duplicate_work = None
    if alert_obj and alert_obj.duplicate_candidate_id:
        for w in ANALYZED_WORKS:
            if w["work_id"] == alert_obj.duplicate_candidate_id:
                duplicate_work = w
                break

    ag_id = work.get("implementing_agency_id")
    agency_profile = AGENCY_PROFILES_MAP.get(ag_id)
    review_history = REVIEWS_STORE.get(f"ALT-{work_id}")

    return {
        "work": work,
        "alert": alert_obj,
        "duplicate_candidate_work": duplicate_work,
        "agency_profile": agency_profile,
        "review_history": review_history
    }


@app.get("/api/v1/alerts")
def list_alerts(
    risk_level: Optional[str] = None,
    signal_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    alert_list = list(ALERTS_MAP.values())

    if risk_level:
        alert_list = [a for a in alert_list if a.risk_level.value == risk_level]

    if signal_type:
        alert_list = [
            a for a in alert_list
            if any(s.signal_type == signal_type for s in a.triggering_signals)
        ]

    total = len(alert_list)
    paged = alert_list[offset : offset + limit]

    for a in paged:
        if a.alert_id in REVIEWS_STORE:
            a.is_reviewed = True
            a.latest_review = REVIEWS_STORE[a.alert_id]

    return {"total": total, "alerts": paged}


class ReviewSubmissionReq(BaseModel):
    officer_name: str
    officer_role: str
    action: ReviewAction
    remarks: str


@app.post("/api/v1/alerts/{alert_id}/review")
def submit_officer_review(alert_id: str, req: ReviewSubmissionReq):
    if alert_id not in ALERTS_MAP:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert = ALERTS_MAP[alert_id]
    review_record = {
        "alert_id": alert_id,
        "work_id": alert.work_id,
        "officer_name": req.officer_name,
        "officer_role": req.officer_role,
        "action": req.action.value,
        "remarks": req.remarks,
        "timestamp": json.dumps(str(json.loads(json.dumps(dict(req))) if hasattr(req, 'dict') else {}))
    }

    REVIEWS_STORE[alert_id] = review_record
    alert.is_reviewed = True
    alert.latest_review = review_record

    # Append-only audit log entry
    AUDIT_LOGS.append({
        "timestamp": review_record["timestamp"],
        "action_type": "OFFICER_ALERT_REVIEW",
        "alert_id": alert_id,
        "work_id": alert.work_id,
        "officer": req.officer_name,
        "action": req.action.value,
        "remarks": req.remarks
    })

    return {"status": "success", "message": "Officer review recorded in append-only audit log.", "review": review_record}


@app.get("/api/v1/agencies")
def list_agencies():
    return list(AGENCY_PROFILES_MAP.values())


@app.post("/api/v1/analytics/run")
def trigger_analytics_rerun():
    load_and_analyze_dataset()
    return {"status": "success", "message": f"Analytics pipeline completed. Analyzed {len(ANALYZED_WORKS)} works and updated alerts."}


class CopilotQueryReq(BaseModel):
    query: str


@app.post("/api/v1/copilot/query")
async def copilot_query(req: CopilotQueryReq):
    res = await llm_service.answer_investigation_query(
        req.query, ANALYZED_WORKS, list(ALERTS_MAP.values()), AGENCY_PROFILES_MAP
    )
    return res


@app.get("/api/v1/audit-logs")
def get_audit_logs():
    return AUDIT_LOGS
