"""
PHASE 4 — FEATURE ENGINEERING
===============================
Calculates numerical features for anomaly detection from the master project table.
Only computes features where the required source data actually exists.

Feature Formulas (all documented):
    CostDeviation     = (total_expenditure - sanction_amount) / sanction_amount
    ExpenditureRatio  = total_expenditure / sanction_amount
    RecSanRatio       = sanction_amount / recommended_amount
    SanctionDelay     = sanction_date - recommendation_date  (days)
    CompletionDuration= actual_completion_date - sanction_date (days)
    SpendingVelocity  = total_expenditure / project_duration_days
    VelocityRatio     = project_velocity / median_peer_velocity (by category+state)
    PaymentFrequency  = payment_count (number of disbursements)
    PaymentConcentration = max_single_payment / total_expenditure
    VendorConcentration = projects per vendor in same constituency

Output:
    ml/data/features.csv — project-level feature matrix
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from config import OUTPUT_DIR, REPORT_DIR, REFERENCE_DATE, PROJECT_ROOT

DATA_DIR = OUTPUT_DIR  # features reads from ml/data/


def _safe_div(numerator: pd.Series, denominator: pd.Series, fill: float = 0.0) -> pd.Series:
    """Division with protection against zero/NaN denominators."""
    return numerator / denominator.replace(0, np.nan).fillna(np.nan)


def compute_features(master: pd.DataFrame) -> pd.DataFrame:
    """Compute all anomaly-detection features from the master project table."""
    print("\n  Computing features…")
    features = master[["project_id"]].copy()

    feature_availability = {}

    # ─── FEATURE 1: Cost Deviation ───
    # CostDeviation = (total_expenditure - sanction_amount) / sanction_amount
    if "total_expenditure" in master.columns and "sanction_amount" in master.columns:
        exp = pd.to_numeric(master["total_expenditure"], errors="coerce")
        san = pd.to_numeric(master["sanction_amount"], errors="coerce")

        features["cost_deviation"] = _safe_div(exp - san, san)
        features["cost_deviation_pct"] = features["cost_deviation"] * 100
        avail = features["cost_deviation"].notna().sum()
        feature_availability["cost_deviation"] = {"available": True, "computed_count": int(avail)}
        print(f"    CostDeviation: computed for {avail} projects")
    else:
        feature_availability["cost_deviation"] = {"available": False, "reason": "Missing total_expenditure or sanction_amount"}

    # ─── FEATURE 2: Expenditure Ratio ───
    # ExpenditureRatio = total_expenditure / sanction_amount
    if "total_expenditure" in master.columns and "sanction_amount" in master.columns:
        exp = pd.to_numeric(master["total_expenditure"], errors="coerce")
        san = pd.to_numeric(master["sanction_amount"], errors="coerce")

        features["expenditure_ratio"] = _safe_div(exp, san)
        avail = features["expenditure_ratio"].notna().sum()
        feature_availability["expenditure_ratio"] = {"available": True, "computed_count": int(avail)}
        print(f"    ExpenditureRatio: computed for {avail} projects")
    else:
        feature_availability["expenditure_ratio"] = {"available": False, "reason": "Missing required columns"}

    # ─── FEATURE 3: Recommended vs Sanction Ratio ───
    # RecSanRatio = sanction_amount / recommended_amount
    if "sanction_amount" in master.columns and "recommended_amount" in master.columns:
        san = pd.to_numeric(master["sanction_amount"], errors="coerce")
        rec = pd.to_numeric(master["recommended_amount"], errors="coerce")

        features["rec_san_ratio"] = _safe_div(san, rec)
        avail = features["rec_san_ratio"].notna().sum()
        feature_availability["rec_san_ratio"] = {"available": True, "computed_count": int(avail)}
        print(f"    RecSanRatio: computed for {avail} projects")
    else:
        feature_availability["rec_san_ratio"] = {"available": False, "reason": "Missing required columns"}

    # ─── FEATURE 4: Sanction Delay (days) ───
    # SanctionDelay = sanction_date - recommendation_date
    if "sanction_date" in master.columns and "recommendation_date" in master.columns:
        san_dt = pd.to_datetime(master["sanction_date"], errors="coerce")
        rec_dt = pd.to_datetime(master["recommendation_date"], errors="coerce")

        features["sanction_delay_days"] = (san_dt - rec_dt).dt.days
        avail = features["sanction_delay_days"].notna().sum()
        feature_availability["sanction_delay_days"] = {"available": True, "computed_count": int(avail)}
        print(f"    SanctionDelay: computed for {avail} projects")
    else:
        feature_availability["sanction_delay_days"] = {"available": False, "reason": "Missing date columns"}

    # ─── FEATURE 5: Completion Duration (days) — completed works only ───
    # CompletionDuration = actual_completion_date - sanction_date
    if "actual_completion_date" in master.columns and "sanction_date" in master.columns:
        comp_dt = pd.to_datetime(master["actual_completion_date"], errors="coerce")
        san_dt = pd.to_datetime(master["sanction_date"], errors="coerce")

        features["completion_duration_days"] = (comp_dt - san_dt).dt.days
        avail = features["completion_duration_days"].notna().sum()
        feature_availability["completion_duration_days"] = {"available": True, "computed_count": int(avail)}
        print(f"    CompletionDuration: computed for {avail} projects")
    else:
        feature_availability["completion_duration_days"] = {"available": False, "reason": "Missing date columns"}

    # ─── FEATURE 6: Project Age (days since sanction) ───
    if "sanction_date" in master.columns:
        san_dt = pd.to_datetime(master["sanction_date"], errors="coerce")
        reference_date = pd.Timestamp(REFERENCE_DATE)
        features["project_age_days"] = (reference_date - san_dt).dt.days
        features["project_age_days"] = features["project_age_days"].clip(lower=0)
        avail = features["project_age_days"].notna().sum()
        feature_availability["project_age_days"] = {"available": True, "computed_count": int(avail)}
        print(f"    ProjectAge: computed for {avail} projects")

    # ─── FEATURE 7: Spending Velocity ───
    # SpendingVelocity = total_expenditure / project_age_days
    if "total_expenditure" in master.columns and "project_age_days" in features.columns:
        exp = pd.to_numeric(master["total_expenditure"], errors="coerce")
        age = features["project_age_days"]

        features["spending_velocity"] = _safe_div(exp, age)
        avail = features["spending_velocity"].notna().sum()
        feature_availability["spending_velocity"] = {"available": True, "computed_count": int(avail)}
        print(f"    SpendingVelocity: computed for {avail} projects")
    else:
        feature_availability["spending_velocity"] = {"available": False, "reason": "Missing required columns"}

    # ─── FEATURE 8: Velocity Ratio (peer-relative) ───
    # VelocityRatio = project_velocity / median_peer_velocity
    if "spending_velocity" in features.columns and "work_category" in master.columns and "state_name" in master.columns:
        merged = features[["project_id", "spending_velocity"]].copy()
        merged["work_category"] = master["work_category"]
        merged["state_name"] = master["state_name"]

        # Peer group: same category + state
        peer_median = merged.groupby(["work_category", "state_name"])["spending_velocity"].transform("median")
        features["velocity_ratio"] = _safe_div(features["spending_velocity"], peer_median)
        avail = features["velocity_ratio"].notna().sum()
        feature_availability["velocity_ratio"] = {"available": True, "computed_count": int(avail)}
        print(f"    VelocityRatio: computed for {avail} projects")

    # ─── FEATURE 9: Payment Frequency ───
    if "payment_count" in master.columns:
        features["payment_frequency"] = pd.to_numeric(master["payment_count"], errors="coerce").fillna(0)
        avail = (features["payment_frequency"] > 0).sum()
        feature_availability["payment_frequency"] = {"available": True, "computed_count": int(avail)}
        print(f"    PaymentFrequency: computed for {avail} projects")

    # ─── FEATURE 10: Payment Concentration ───
    # PaymentConcentration = max_single_payment / total_expenditure
    if "max_single_payment" in master.columns and "total_expenditure" in master.columns:
        max_pay = pd.to_numeric(master["max_single_payment"], errors="coerce")
        total_exp = pd.to_numeric(master["total_expenditure"], errors="coerce")

        features["payment_concentration"] = _safe_div(max_pay, total_exp)
        avail = features["payment_concentration"].notna().sum()
        feature_availability["payment_concentration"] = {"available": True, "computed_count": int(avail)}
        print(f"    PaymentConcentration: computed for {avail} projects")

    # ─── FEATURE 11: Vendor Concentration (per constituency) ───
    if "vendor_name" in master.columns and "constituency" in master.columns:
        vendor_counts = master.groupby(["constituency", "vendor_name"]).size().reset_index(name="vendor_project_count")
        merged = master[["project_id", "constituency", "vendor_name"]].merge(
            vendor_counts, on=["constituency", "vendor_name"], how="left"
        )
        features["vendor_constituency_count"] = merged["vendor_project_count"].fillna(0).astype(int)
        avail = (features["vendor_constituency_count"] > 0).sum()
        feature_availability["vendor_constituency_count"] = {"available": True, "computed_count": int(avail)}
        print(f"    VendorConcentration: computed for {avail} projects")

    # ─── FEATURE 12: Category Cost Deviation ───
    # How much does the sanction amount deviate from the category median?
    if "sanction_amount" in master.columns and "work_category" in master.columns:
        san = pd.to_numeric(master["sanction_amount"], errors="coerce")
        cat_median = master.assign(_san=san).groupby("work_category")["_san"].transform("median")
        features["category_cost_ratio"] = _safe_div(san, cat_median)
        avail = features["category_cost_ratio"].notna().sum()
        feature_availability["category_cost_ratio"] = {"available": True, "computed_count": int(avail)}
        print(f"    CategoryCostRatio: computed for {avail} projects")

    # ─── FEATURE 13: Expenditure Spread (time between first and last payment) ───
    if "first_expenditure_date" in master.columns and "last_expenditure_date" in master.columns:
        first_dt = pd.to_datetime(master["first_expenditure_date"], errors="coerce")
        last_dt = pd.to_datetime(master["last_expenditure_date"], errors="coerce")
        features["expenditure_spread_days"] = (last_dt - first_dt).dt.days
        avail = features["expenditure_spread_days"].notna().sum()
        feature_availability["expenditure_spread_days"] = {"available": True, "computed_count": int(avail)}
        print(f"    ExpenditureSpread: computed for {avail} projects")

    # ─── UNAVAILABLE FEATURES (documented) ───
    unavailable = [
        ("progress_gap", "financial_progress_pct and physical_progress_pct not in dataset"),
        ("progress_risk", "progress percentages not in dataset"),
        ("geo_distance", "latitude/longitude not in dataset"),
        ("photo_evidence_score", "photo_count not in dataset"),
    ]
    for feat_name, reason in unavailable:
        feature_availability[feat_name] = {"available": False, "reason": reason}
        print(f"    {feat_name}: NOT AVAILABLE — {reason}")

    # Save feature availability report
    report = {
        "computed_at": datetime.now().isoformat(),
        "total_projects": len(features),
        "feature_columns": [c for c in features.columns if c != "project_id"],
        "feature_availability": feature_availability,
    }
    report_path = REPORT_DIR / "feature_engineering_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Feature report: {report_path}")

    return features


def main():
    print("=" * 70)
    print("MPLADS FEATURE ENGINEERING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        print("Run data_integration.py first.")
        return

    master = pd.read_csv(master_path, low_memory=False)
    print(f"  Loaded master table: {master.shape}")

    features = compute_features(master)

    out_path = DATA_DIR / "features.csv"
    features.to_csv(out_path, index=False)
    print(f"\n✅ Feature matrix saved: {out_path}")
    print(f"   Shape: {features.shape}")
    print(f"   Features: {[c for c in features.columns if c != 'project_id']}")


if __name__ == "__main__":
    main()
