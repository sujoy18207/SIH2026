"""
FASTAPI RISK INTELLIGENCE API SERVER
======================================
REST API service providing access to MPLADS project risk scores,
anomalies, analytics, and prediction capabilities.

Endpoints:
    GET  /health
    GET  /projects/{project_id}/risk
    GET  /risks/high
    GET  /risks/critical
    GET  /analytics/summary
    POST /model/retrain (protected)
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Ensure src in path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import OUTPUT_DIR, REPORT_DIR, RISK_THRESHOLDS
from predict_risk import RiskPredictor

app = FastAPI(
    title="MPLADS Anomaly & Risk Intelligence API",
    description="API for eSAKSHI MPLADS project anomaly detection and explainable risk scores",
    version="1.0.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data cache
_master_cache: Optional[pd.DataFrame] = None
_risk_cache: Optional[pd.DataFrame] = None
_predictor: Optional[RiskPredictor] = None


def get_data():
    global _master_cache, _risk_cache, _predictor
    master_path = OUTPUT_DIR / "master_projects.csv"
    risk_path = OUTPUT_DIR / "risk_scores.csv"

    if _master_cache is None and master_path.exists():
        _master_cache = pd.read_csv(master_path, low_memory=False)

    if _risk_cache is None and risk_path.exists():
        _risk_cache = pd.read_csv(risk_path)

    if _predictor is None:
        try:
            _predictor = RiskPredictor()
        except Exception as e:
            print(f"Predictor warning: {e}")

    return _master_cache, _risk_cache, _predictor


@app.get("/health")
def health_check():
    master_df, risk_df, _ = get_data()
    return {
        "status": "healthy",
        "master_records": len(master_df) if master_df is not None else 0,
        "risk_records": len(risk_df) if risk_df is not None else 0,
        "api_version": "1.0.0",
    }


@app.get("/projects/{project_id}/risk")
def get_project_risk(project_id: int):
    master_df, risk_df, predictor = get_data()

    if master_df is None or risk_df is None:
        raise HTTPException(status_code=503, detail="Risk dataset not yet generated. Run ML pipeline first.")

    if predictor:
        res = predictor.get_project_risk(project_id, master_df, risk_df)
        if "error" in res:
            raise HTTPException(status_code=404, detail=res["error"])
        return res

    # Fallback lookup if predictor not loaded
    proj_risk = risk_df[risk_df["project_id"] == project_id]
    if proj_risk.empty:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    row = proj_risk.iloc[0].to_dict()
    return row


@app.get("/risks/high")
def get_high_risk_projects(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    state: Optional[str] = None,
):
    master_df, risk_df, _ = get_data()
    if risk_df is None or master_df is None:
        raise HTTPException(status_code=503, detail="Risk dataset not ready.")

    filtered = risk_df[risk_df["risk_category"].isin(["HIGH", "CRITICAL"])].copy()

    if state and "state_name" in master_df.columns:
        master_states = master_df[["project_id", "state_name", "constituency", "work_description"]]
        filtered = filtered.merge(master_states, on="project_id", how="left")
        filtered = filtered[filtered["state_name"].str.upper() == state.upper()]
    elif "state_name" in master_df.columns:
        master_states = master_df[["project_id", "state_name", "constituency", "work_description"]]
        filtered = filtered.merge(master_states, on="project_id", how="left")

    filtered = filtered.sort_values(by="risk_score", ascending=False)
    total = len(filtered)

    page = filtered.iloc[offset : offset + limit]

    records = page.to_dict(orient="records")

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "projects": records,
    }


@app.get("/risks/critical")
def get_critical_risk_projects(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    master_df, risk_df, _ = get_data()
    if risk_df is None:
        raise HTTPException(status_code=503, detail="Risk dataset not ready.")

    filtered = risk_df[risk_df["risk_category"] == "CRITICAL"].copy()

    if master_df is not None:
        master_details = master_df[["project_id", "state_name", "constituency", "mp_name", "sanction_amount", "total_expenditure", "work_description"]]
        filtered = filtered.merge(master_details, on="project_id", how="left")

    filtered = filtered.sort_values(by="risk_score", ascending=False)
    total = len(filtered)
    page = filtered.iloc[offset : offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "projects": page.to_dict(orient="records"),
    }


@app.get("/analytics/summary")
def get_analytics_summary():
    master_df, risk_df, _ = get_data()
    if risk_df is None:
        raise HTTPException(status_code=503, detail="Risk dataset not ready.")

    cats = risk_df["risk_category"].value_counts().to_dict()

    summary = {
        "total_projects": len(risk_df),
        "risk_distribution": {
            "LOW": int(cats.get("LOW", 0)),
            "MEDIUM": int(cats.get("MEDIUM", 0)),
            "HIGH": int(cats.get("HIGH", 0)),
            "CRITICAL": int(cats.get("CRITICAL", 0)),
        },
        "average_risk_score": round(float(risk_df["risk_score"].mean()), 1),
        "average_data_quality": round(float(risk_df["data_quality_score"].mean()), 1),
        "projects_with_rules_triggered": int((risk_df["rule_risk"] > 0).sum()) if "rule_risk" in risk_df.columns else 0,
        "high_ml_anomaly_count": int((risk_df["ml_anomaly_risk"] >= 70).sum()) if "ml_anomaly_risk" in risk_df.columns else 0,
    }

    if master_df is not None:
        summary["total_states"] = int(master_df["state_name"].nunique()) if "state_name" in master_df.columns else 0
        summary["total_constituencies"] = int(master_df["constituency"].nunique()) if "constituency" in master_df.columns else 0
        summary["total_mps"] = int(master_df["mp_name"].nunique()) if "mp_name" in master_df.columns else 0
        if "sanction_amount" in master_df.columns:
            summary["total_sanctioned_amt"] = float(master_df["sanction_amount"].sum())
        if "total_expenditure" in master_df.columns:
            summary["total_expenditure_amt"] = float(master_df["total_expenditure"].sum())

    return summary


@app.post("/model/retrain")
def trigger_model_retrain(x_api_key: Optional[str] = Header(None)):
    # Protect endpoint
    if x_api_key != "sih2026_admin_secret_key":
        raise HTTPException(status_code=401, detail="Unauthorized retrain request")

    # Launch pipeline retraining
    import run_pipeline
    try:
        run_pipeline.run_full_pipeline(skip_audit=True)
        # Clear cache
        global _master_cache, _risk_cache, _predictor
        _master_cache = None
        _risk_cache = None
        _predictor = None
        return {"status": "success", "message": "Model retrained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
