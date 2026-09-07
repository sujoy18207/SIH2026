"""
FastAPI Backend Application for MPLADS Anomaly & Risk Detection Platform
Serving the REAL eSAKSHI dataset (scraped from mplads.mospi.gov.in) from a
persistent SQLite database. Designed for a persistent server deployment —
no serverless assumptions.
"""

import json
import os
import sqlite3
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.schemas.mplads import (
    OverviewStats, WorkBase, ExplainableAlert, OfficerReview, AgencyProfile, ReviewAction,
    AnomalySignal, RiskScoreBreakdown, RiskLevel
)
from app.db import get_db_path, get_connection, init_schema
from app.engine.risk_engine import RiskEngine
from app.services.llm_service import LLMCopilotService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open/validate the SQLite database. Analytics are precomputed by the ETL — startup is instant."""
    db_path = get_db_path()
    if not db_path.exists():
        raise RuntimeError(
            f"Database not found at {db_path}. Run `python -m backend.app.etl` first "
            f"to build it from the real eSAKSHI CSVs."
        )
    conn = get_connection()
    try:
        init_schema(conn)  # no-op if schema exists
        n = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        print(f"[API Startup] Real eSAKSHI database ready: {n:,} works at {db_path}")
    finally:
        conn.close()
    yield


app = FastAPI(
    title="MPLADS AI Anomaly & Risk Detection Platform API",
    description="AI-powered monitoring, anomaly detection, cost benchmarking, duplicate work detection & decision-support API for MPLADS (real eSAKSHI data)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

risk_engine = RiskEngine()
llm_service = LLMCopilotService()

# Background analytics job state (in-memory job bookkeeping only; results are persisted in SQLite)
ANALYTICS_STATE = {
    "running": False,
    "last_run": None,
    "last_alerts": None,
    "works_processed": None,
    "error": None,
}



# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/v1/health")
def health_check():
    conn = get_connection()
    try:
        works = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        mps = conn.execute("SELECT COUNT(*) FROM mp_allocations").fetchone()[0]
        return {
            "status": "healthy",
            "data_source": "real eSAKSHI scraped dataset",
            "monitored_works": works,
            "active_alerts": alerts,
            "mps": mps,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@app.get("/api/v1/overview", response_model=OverviewStats)
def get_overview_stats():
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total_works,
                   COALESCE(SUM(recommended_amount),0) AS rec_amt,
                   COALESCE(SUM(sanction_amount),0) AS sanc_amt,
                   COALESCE(SUM(total_disbursed),0) AS exp_amt,
                   SUM(CASE WHEN work_status='Completed' THEN 1 ELSE 0 END) AS completed_cnt,
                   SUM(CASE WHEN work_status='In Progress' THEN 1 ELSE 0 END) AS in_prog_cnt,
                   SUM(CASE WHEN risk_level='High' THEN 1 ELSE 0 END) AS high_cnt,
                   SUM(CASE WHEN risk_level='Critical' THEN 1 ELSE 0 END) AS crit_cnt,
                   SUM(CASE WHEN risk_level='Medium' THEN 1 ELSE 0 END) AS med_cnt,
                   SUM(CASE WHEN risk_level='Low' THEN 1 ELSE 0 END) AS low_cnt,
                   SUM(CASE WHEN work_status='Pending Sanction' THEN 1 ELSE 0 END) AS pending_cnt,
                   SUM(CASE WHEN work_status='Sanctioned' THEN 1 ELSE 0 END) AS sancd_cnt,
                   SUM(CASE WHEN total_disbursed > sanction_amount THEN total_disbursed - sanction_amount ELSE 0 END) AS overrun_val,
                   COUNT(DISTINCT state) AS states_cnt,
                   COUNT(DISTINCT district) AS districts_cnt
            FROM works
            """
        ).fetchone()
        dup_cnt = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE duplicate_candidate_id IS NOT NULL").fetchone()[0]
        avg_dq = conn.execute("SELECT AVG(data_quality_score) FROM works").fetchone()[0] or 100.0
        vendors = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()[0]
        mps = conn.execute("SELECT COUNT(*) FROM mp_allocations").fetchone()[0]

        return OverviewStats(
            total_works=row["total_works"],
            total_recommended_amount=round(row["rec_amt"], 2),
            total_sanctioned_amount=round(row["sanc_amt"], 2),
            total_expenditure_amount=round(row["exp_amt"], 2),
            completed_works_count=row["completed_cnt"] or 0,
            in_progress_works_count=row["in_prog_cnt"] or 0,
            pending_sanction_works_count=row["pending_cnt"] or 0,
            sanctioned_works_count=row["sancd_cnt"] or 0,
            high_risk_works_count=row["high_cnt"] or 0,
            critical_risk_works_count=row["crit_cnt"] or 0,
            medium_risk_works_count=row["med_cnt"] or 0,
            low_risk_works_count=row["low_cnt"] or 0,
            potential_cost_overrun_val=round(row["overrun_val"], 2),
            duplicate_candidates_count=dup_cnt,
            avg_data_quality_score=round(avg_dq, 1),
            states_count=row["states_cnt"] or 0,
            districts_count=row["districts_cnt"] or 0,
            vendors_count=vendors,
            mps_count=mps
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Works
# ---------------------------------------------------------------------------

WORK_LIST_COLUMNS = """
    work_id, house, state, district, constituency, mp_name, tenure,
    work_category, activity_name, work_description, ida_name, work_stage, work_status,
    recommendation_date, sanction_date, actual_end_date,
    recommended_amount, sanction_amount, actual_amount,
    total_disbursed, payment_count, vendor_count,
    risk_score, risk_level, data_quality_score, data_quality_status,
    evidence_confidence_score, evidence_confidence_level, signals_count
"""


@app.get("/api/v1/works")
def list_works(
    state: Optional[str] = None,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    house: Optional[str] = None,
    work_category: Optional[str] = None,
    work_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0
):
    where_clauses: List[str] = []
    params: List[Any] = []

    if state:
        where_clauses.append("state = ?"); params.append(state)
    if district:
        where_clauses.append("district = ?"); params.append(district)
    if constituency:
        where_clauses.append("constituency = ?"); params.append(constituency)
    if house:
        where_clauses.append("house = ?"); params.append(house)
    if work_category:
        where_clauses.append("work_category = ?"); params.append(work_category)
    if work_status:
        where_clauses.append("work_status = ?"); params.append(work_status)
    if risk_level:
        where_clauses.append("risk_level = ?"); params.append(risk_level)
    if search:
        like = f"%{search.lower()}%"
        where_clauses.append(
            "(LOWER(work_id) LIKE ? OR LOWER(work_description) LIKE ? OR LOWER(mp_name) LIKE ? OR LOWER(ida_name) LIKE ?)"
        )
        params.extend([like, like, like, like])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    order_sql = "ORDER BY COALESCE(risk_score, 0) DESC, work_id ASC"

    conn = get_connection()
    try:
        total = conn.execute(f"SELECT COUNT(*) FROM works {where_sql}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT {WORK_LIST_COLUMNS} FROM works {where_sql} {order_sql} LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "works": [dict(r) for r in rows]
        }
    finally:
        conn.close()


@app.get("/api/v1/works/{work_id}")
def get_work_by_id(work_id: str):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM works WHERE work_id=?", (work_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Work {work_id} not found")
        return dict(row)
    finally:
        conn.close()


@app.get("/api/v1/works/{work_id}/investigation")
def get_work_investigation_dossier(work_id: str):
    conn = get_connection()
    try:
        work = conn.execute("SELECT * FROM works WHERE work_id=?", (work_id,)).fetchone()
        if work is None:
            raise HTTPException(status_code=404, detail=f"Work {work_id} not found")
        work = dict(work)

        alert_row = conn.execute("SELECT * FROM alerts WHERE work_id=?", (work_id,)).fetchone()

        alert_obj = None
        duplicate_work = None
        if alert_row is not None:
            a = dict(alert_row)
            # Rehydrate the Pydantic alert from persisted JSON
            try:
                signals = [AnomalySignal(**s) for s in json.loads(a["triggering_signals"] or "[]")]
                breakdown = RiskScoreBreakdown(**json.loads(a["risk_breakdown"] or "{}"))
                alert_obj = ExplainableAlert(
                    alert_id=a["alert_id"],
                    work_id=a["work_id"],
                    work_title=a["work_title"] or "",
                    state=a["state"] or "",
                    district=a["district"] or "",
                    constituency=a["constituency"] or "",
                    mp_name=a["mp_name"] or "",
                    implementing_agency_name=a["agency_name"] or "",
                    created_at=a["created_at"] or "",
                    risk_score=a["risk_score"] or 0.0,
                    risk_level=RiskLevel(a["risk_level"]) if a["risk_level"] else RiskLevel.LOW,
                    risk_breakdown=breakdown,
                    data_quality_score=a["data_quality_score"] or 0.0,
                    data_quality_status=a["data_quality_status"] or "",
                    evidence_confidence_score=a["evidence_confidence_score"] or 0.0,
                    evidence_confidence_level=a["evidence_confidence_level"] or "",
                    triggering_signals=signals,
                    narrative_explanation=a["narrative_explanation"] or "",
                    duplicate_candidate_id=a["duplicate_candidate_id"],
                    duplicate_risk_score=a["duplicate_risk_score"],
                    recommended_action=a["recommended_action"] or "Priority Review Recommended",
                    is_reviewed=bool(a["is_reviewed"]),
                    latest_review=json.loads(a["latest_review"]) if a["latest_review"] else None
                )
            except Exception:
                alert_obj = None

            if a["duplicate_candidate_id"]:
                dup = conn.execute(
                    "SELECT * FROM works WHERE work_id=?", (a["duplicate_candidate_id"],)).fetchone()
                if dup is not None:
                    duplicate_work = dict(dup)

        agency_profile = None
        if work.get("ida_name"):
            ag = conn.execute("SELECT * FROM agencies WHERE agency_id=?", (work["ida_name"],)).fetchone()
            if ag is not None:
                agency_profile = dict(ag)

        reviews = conn.execute(
            "SELECT * FROM reviews WHERE work_id=? ORDER BY created_at DESC", (work_id,)).fetchall()

        payments = conn.execute(
            """SELECT payment_id, vendor_name, vendor_id, ia_name, expenditure_date,
                      fund_disbursed_amt, work_status
               FROM payments WHERE work_id=? ORDER BY expenditure_date ASC""",
            (work_id,)).fetchall()

        return {
            "work": work,
            "alert": alert_obj,
            "duplicate_candidate_work": duplicate_work,
            "agency_profile": agency_profile,
            "review_history": [dict(r) for r in reviews],
            "payments": [dict(p) for p in payments]
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

@app.get("/api/v1/alerts")
def list_alerts(
    risk_level: Optional[str] = None,
    signal_type: Optional[str] = None,
    limit: int = Query(50, le=500),
    offset: int = 0
):
    conn = get_connection()
    try:
        where_clauses: List[str] = []
        params: List[Any] = []

        if risk_level:
            where_clauses.append("risk_level = ?"); params.append(risk_level)
        if signal_type:
            # Match against the JSON signals array text
            where_clauses.append("LOWER(triggering_signals) LIKE ?")
            params.append(f'%"{signal_type.lower()}"%')

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        total = conn.execute(f"SELECT COUNT(*) FROM alerts {where_sql}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM alerts {where_sql} ORDER BY risk_score DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()

        alerts = []
        for r in rows:
            a = dict(r)
            try:
                a["risk_breakdown"] = json.loads(a["risk_breakdown"] or "{}")
                a["triggering_signals"] = json.loads(a["triggering_signals"] or "[]")
            except json.JSONDecodeError:
                a["risk_breakdown"] = {}
                a["triggering_signals"] = []
            if a.get("latest_review"):
                try:
                    a["latest_review"] = json.loads(a["latest_review"])
                except json.JSONDecodeError:
                    a["latest_review"] = None
            a["is_reviewed"] = bool(a.get("is_reviewed"))
            alerts.append(a)

        return {"total": total, "alerts": alerts}
    finally:
        conn.close()


class ReviewSubmissionReq(BaseModel):
    officer_name: str
    officer_role: str
    action: ReviewAction
    remarks: str


@app.post("/api/v1/alerts/{alert_id}/review")
def submit_officer_review(alert_id: str, req: ReviewSubmissionReq):
    conn = get_connection()
    try:
        alert = conn.execute("SELECT alert_id, work_id FROM alerts WHERE alert_id=?", (alert_id,)).fetchone()
        if alert is None:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

        now = datetime.now().isoformat()
        review_record = {
            "alert_id": alert_id,
            "work_id": alert["work_id"],
            "officer_name": req.officer_name,
            "officer_role": req.officer_role,
            "action": req.action.value,
            "remarks": req.remarks,
            "timestamp": now
        }

        cur = conn.cursor()
        cur.execute("BEGIN")
        cur.execute(
            """INSERT INTO reviews (alert_id, work_id, officer_name, officer_role, action, remarks, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (alert_id, alert["work_id"], req.officer_name, req.officer_role,
             req.action.value, req.remarks, now)
        )
        cur.execute("UPDATE alerts SET is_reviewed=1, latest_review=? WHERE alert_id=?",
                    (json.dumps(review_record), alert_id))
        # Append-only audit log entry
        cur.execute(
            """INSERT INTO audit_logs (created_at, action_type, alert_id, work_id, officer, action, remarks)
               VALUES (?,?,?,?,?,?,?)""",
            (now, "OFFICER_ALERT_REVIEW", alert_id, alert["work_id"],
             req.officer_name, req.action.value, req.remarks)
        )
        conn.commit()

        return {
            "status": "success",
            "message": "Officer review recorded in append-only audit log.",
            "review": review_record
        }
    finally:
        conn.close()


@app.get("/api/v1/audit-logs")
def get_audit_logs(limit: int = Query(200, le=1000)):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Geographic Risk Zones (state-level aggregates for the National Risk Map)
# ---------------------------------------------------------------------------

@app.get("/api/v1/geo/risk-zones")
def get_geo_risk_zones():
    """State-level multi-signal aggregates powering the Geographic Risk Map.

    Coordinates are NOT taken from the works data (the real eSAKSHI extracts
    carry none); the frontend joins these aggregates onto a static table of
    state centroids. Risk level mirrors the platform classification but is
    ranked relative to state scale: HIGH when >=3% of the state's works are
    high/critical risk, MEDIUM at >=1%, else LOW.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT state,
                   COUNT(*) AS total_works,
                   SUM(CASE WHEN risk_level IN ('High','Critical') THEN 1 ELSE 0 END) AS high_risk_works,
                   ROUND(AVG(risk_score), 1) AS avg_risk_score,
                   ROUND(SUM(total_disbursed) / 10000000.0, 1) AS disbursed_cr,
                   COUNT(DISTINCT district) AS districts_count
            FROM works
            WHERE state IS NOT NULL AND state != ''
            GROUP BY state
            ORDER BY total_works DESC
            """
        ).fetchall()
        zones = []
        for r in rows:
            total = r["total_works"] or 0
            high = r["high_risk_works"] or 0
            pct = (high / total) if total else 0.0
            if pct >= 0.03:
                status = "HIGH"
            elif pct >= 0.01:
                status = "MEDIUM"
            else:
                status = "LOW"
            zones.append({
                "state": r["state"],
                "total_works": total,
                "high_risk_works": high,
                "avg_risk_score": r["avg_risk_score"] or 0.0,
                "disbursed_cr": r["disbursed_cr"] or 0.0,
                "districts_count": r["districts_count"] or 0,
                "status": status,
            })
        return {"total_states": len(zones), "zones": zones}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Agencies & Vendors
# ---------------------------------------------------------------------------

@app.get("/api/v1/agencies")
def list_agencies(limit: int = Query(500, le=5000)):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM agencies ORDER BY agency_risk_score DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/api/v1/vendors/top")
def list_top_vendors(limit: int = Query(50, le=500)):
    """Vendor payment concentration — contractor-nexus verification signal."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM vendors ORDER BY work_count DESC, total_disbursed DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# MP Allocation Database (real eSAKSHI data, both houses)
# ---------------------------------------------------------------------------

@app.get("/api/v1/mps/allocated-limits")
def get_official_mp_allocated_limits(
    house: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(800, le=1000),
):
    conn = get_connection()
    try:
        where_clauses: List[str] = []
        params: List[Any] = []
        if house:
            where_clauses.append("house = ?"); params.append(house)
        if state:
            where_clauses.append("state = ?"); params.append(state)
        if search:
            like = f"%{search.lower()}%"
            where_clauses.append("(LOWER(mp_name) LIKE ? OR LOWER(constituency) LIKE ? OR LOWER(state) LIKE ?)")
            params.extend([like, like, like])
        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        total = conn.execute(f"SELECT COUNT(*) FROM mp_allocations {where_sql}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM mp_allocations {where_sql} ORDER BY sr_no ASC LIMIT ?",
            params + [limit]).fetchall()
        records = [dict(r) for r in rows]
        return {
            "total": total,
            "source": "eSAKSHI Official Allocated Limit dataset (Lok Sabha + Rajya Sabha)",
            "mp_allocations": records
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Analytics pipeline
# ---------------------------------------------------------------------------

def _run_analytics_job():
    """Background worker: full multi-signal analysis over all real works, persisted to SQLite."""
    try:
        n_alerts, n_works = risk_engine.run_full_analysis()
        ANALYTICS_STATE.update({
            "running": False,
            "last_run": datetime.now().isoformat(),
            "last_alerts": n_alerts,
            "works_processed": n_works,
            "error": None
        })
        print(f"[Analytics] Completed: {n_alerts} alerts over {n_works} works")
    except Exception as e:
        ANALYTICS_STATE.update({"running": False, "error": str(e)})
        print(f"[Analytics] FAILED: {e}")


@app.post("/api/v1/analytics/run")
def trigger_analytics_rerun():
    if ANALYTICS_STATE["running"]:
        return {"status": "already_running", "message": "Analytics pipeline is currently running."}
    ANALYTICS_STATE.update({"running": True, "error": None})
    thread = threading.Thread(target=_run_analytics_job, daemon=True)
    thread.start()
    return {"status": "started", "message": "Analytics pipeline started in background over the real dataset."}


@app.get("/api/v1/analytics/status")
def analytics_status():
    conn = get_connection()
    try:
        last_run = conn.execute("SELECT value FROM meta WHERE key='last_analytics_run'").fetchone()
        alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    finally:
        conn.close()
    return {
        "running": ANALYTICS_STATE["running"],
        "last_run": ANALYTICS_STATE["last_run"] or (last_run[0] if last_run else None),
        "last_alerts": ANALYTICS_STATE["last_alerts"] if ANALYTICS_STATE["last_alerts"] is not None else alerts,
        "works_processed": ANALYTICS_STATE["works_processed"],
        "error": ANALYTICS_STATE["error"]
    }


# ---------------------------------------------------------------------------
# AI Copilot
# ---------------------------------------------------------------------------

class CopilotQueryReq(BaseModel):
    query: str


@app.post("/api/v1/copilot/query")
async def copilot_query(req: CopilotQueryReq):
    res = await llm_service.answer_investigation_query(req.query)
    return res
