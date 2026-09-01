"""
PHASE 12 — PREDICTION PIPELINE
================================
Loads saved ML model + preprocessing pipeline and generates risk scores
for new/updated project data without retraining.

Usage:
    # Score a single project
    python predict_risk.py --project-id 133166

    # Score all projects in master table
    python predict_risk.py --all

    # Score new data file
    python predict_risk.py --input new_projects.csv

API-ready output format for FastAPI integration.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np
import joblib

from config import OUTPUT_DIR, get_current_model_dir

DATA_DIR = OUTPUT_DIR
MODEL_DIR = get_current_model_dir("v1")


class RiskPredictor:
    """Loads trained models and generates risk predictions."""

    def __init__(self, model_dir: Path = MODEL_DIR):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.imputer = None
        self.feature_config = None
        self.model_metadata = None
        self._load_models()

    def _load_models(self):
        """Load all model artifacts."""
        model_path = self.model_dir / "isolation_forest.joblib"
        scaler_path = self.model_dir / "preprocessing_scaler.joblib"
        imputer_path = self.model_dir / "preprocessing_imputer.joblib"
        config_path = self.model_dir / "feature_config.json"
        meta_path = self.model_dir / "model_metadata.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}. Run train_isolation_forest.py first.")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.imputer = joblib.load(imputer_path)

        with open(config_path) as f:
            self.feature_config = json.load(f)

        with open(meta_path) as f:
            self.model_metadata = json.load(f)

        print(f"  Model loaded: {self.model_metadata.get('algorithm')} v{self.model_metadata.get('model_version')}")
        print(f"  Features: {self.feature_config['features']}")

    def predict_anomaly_score(self, features_row: np.ndarray) -> float:
        """Predict ML anomaly risk for a single feature vector."""
        # Impute and scale
        imputed = self.imputer.transform(features_row.reshape(1, -1))
        scaled = self.scaler.transform(imputed)

        # Decision function
        decision_score = self.model.decision_function(scaled)[0]

        # Normalize to 0-100 (using training data statistics)
        # Since we don't have the exact training min/max stored, use the model's offset
        # A more robust approach: store training min/max during training
        # For now, use a reasonable sigmoid-like mapping
        anomaly_risk = 100.0 / (1.0 + np.exp(decision_score * 5))
        anomaly_risk = float(np.clip(anomaly_risk, 0, 100))

        return round(anomaly_risk, 1)

    def predict_batch(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Predict ML anomaly risk for a batch of projects."""
        feature_cols = self.feature_config["features"]
        available = [c for c in feature_cols if c in features_df.columns]

        if not available:
            print("  WARNING: No matching features found!")
            result = features_df[["project_id"]].copy()
            result["ml_anomaly_risk"] = 0.0
            return result

        X = features_df[available].copy()
        X = X.replace([np.inf, -np.inf], np.nan)

        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)

        decision_scores = self.model.decision_function(X_scaled)

        # Normalize to 0-100
        raw_min = decision_scores.min()
        raw_max = decision_scores.max()
        if raw_max > raw_min:
            anomaly_scores = 100.0 * (1.0 - (decision_scores - raw_min) / (raw_max - raw_min))
        else:
            anomaly_scores = np.full_like(decision_scores, 50.0)

        anomaly_scores = np.clip(anomaly_scores, 0, 100)

        result = features_df[["project_id"]].copy()
        result["ml_anomaly_risk"] = anomaly_scores.round(1)
        result["ml_prediction"] = np.where(
            self.model.predict(X_scaled) == -1, "ANOMALY", "NORMAL"
        )

        return result

    def get_project_risk(self, project_id: int, master_df: pd.DataFrame, risk_df: pd.DataFrame) -> Dict[str, Any]:
        """Get complete risk profile for a single project (API-ready format)."""
        project = master_df[master_df["project_id"] == project_id]
        if project.empty:
            return {"error": f"Project {project_id} not found"}

        risk = risk_df[risk_df["project_id"] == project_id]

        project_row = project.iloc[0]
        risk_row = risk.iloc[0] if not risk.empty else pd.Series(dtype=float)

        response = {
            "project_id": int(project_id),
            "risk_score": float(risk_row.get("risk_score", 0)),
            "risk_category": str(risk_row.get("risk_category", "UNKNOWN")),
            "data_quality_score": float(risk_row.get("data_quality_score", 0)),
            "confidence": str(risk_row.get("confidence", "UNKNOWN")),
            "rule_risk": float(risk_row.get("rule_risk", 0)),
            "ml_anomaly_risk": float(risk_row.get("ml_anomaly_risk", 0)),
            "duplicate_risk": float(risk_row.get("duplicate_risk", 0)),
            "agency_risk": float(risk_row.get("agency_risk", 0)),
            "evidence_count": int(risk_row.get("evidence_count", 0)),
            "reasons": str(risk_row.get("top_reasons", "")).split("; "),
            "project_details": {
                "work_description": str(project_row.get("work_description", "")),
                "state": str(project_row.get("state_name", "")),
                "constituency": str(project_row.get("constituency", "")),
                "mp_name": str(project_row.get("mp_name", "")),
                "ida_name": str(project_row.get("ida_name", "")),
                "work_category": str(project_row.get("work_category", "")),
                "sanction_amount": float(project_row.get("sanction_amount", 0)) if pd.notna(project_row.get("sanction_amount")) else None,
                "total_expenditure": float(project_row.get("total_expenditure", 0)) if pd.notna(project_row.get("total_expenditure")) else None,
                "recommendation_date": str(project_row.get("recommendation_date", "")),
                "sanction_date": str(project_row.get("sanction_date", "")),
                "is_completed": bool(project_row.get("is_completed", False)),
            },
            "model_version": self.model_metadata.get("model_version", "unknown"),
            "disclaimer": "Risk Score ≠ Fraud Probability. Final decision remains with authorized human reviewers.",
        }

        return response


def main():
    parser = argparse.ArgumentParser(description="MPLADS Risk Prediction Pipeline")
    parser.add_argument("--project-id", type=int, help="Score a specific project")
    parser.add_argument("--all", action="store_true", help="Score all projects")
    parser.add_argument("--input", type=str, help="Input CSV file")
    args = parser.parse_args()

    print("=" * 70)
    print("MPLADS RISK PREDICTION PIPELINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    predictor = RiskPredictor()

    if args.project_id:
        master_df = pd.read_csv(DATA_DIR / "master_projects.csv", low_memory=False)
        risk_df = pd.read_csv(DATA_DIR / "risk_scores.csv") if (DATA_DIR / "risk_scores.csv").exists() else pd.DataFrame()

        result = predictor.get_project_risk(args.project_id, master_df, risk_df)
        print(json.dumps(result, indent=2, default=str))

    elif args.all or args.input:
        features_path = Path(args.input) if args.input else DATA_DIR / "features.csv"
        if not features_path.exists():
            print(f"ERROR: Features not found: {features_path}")
            return

        features_df = pd.read_csv(features_path)
        results = predictor.predict_batch(features_df)

        out_path = DATA_DIR / "ml_anomaly_scores.csv"
        results.to_csv(out_path, index=False)
        print(f"\n✅ Predictions saved: {out_path}")
        print(f"   Anomalies: {(results['ml_prediction'] == 'ANOMALY').sum()}")

    else:
        print("Usage: python predict_risk.py --project-id 133166")
        print("       python predict_risk.py --all")


if __name__ == "__main__":
    main()
