"""
PHASE 11 — COMPOSITE RISK ENGINE
==================================
Combines all risk signals into a single explainable 0-100 risk score.

Formula:
    FinalRisk = 0.30 × RuleRisk
              + 0.30 × MLAnomalyRisk
              + 0.20 × DuplicateRisk
              + 0.20 × AgencyRisk

Dynamic re-normalization:
    If a component is unavailable (missing data), its weight is excluded
    and remaining weights are re-normalized so the sum equals 1.0.

Risk Categories:
    0–29:   LOW
    30–59:  MEDIUM
    60–79:  HIGH
    80–100: CRITICAL

Data Quality Score:
    0–100 score indicating data completeness for reliable risk assessment.

Output:
    ml/data/risk_scores.csv — final risk scores with explanations
    ml/reports/risk_engine_report.json — summary statistics
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import numpy as np

from config import (OUTPUT_DIR, REPORT_DIR, RISK_COMPONENT_WEIGHTS as DEFAULT_WEIGHTS,
                    RISK_THRESHOLDS, DATA_QUALITY_PENALTIES, UNAVAILABLE_FIELD_PENALTY,
                    UNAVAILABLE_FIELDS)

DATA_DIR = OUTPUT_DIR

# Risk category thresholds
RISK_THRESHOLDS = {
    "LOW": (0, 29),
    "MEDIUM": (30, 59),
    "HIGH": (60, 79),
    "CRITICAL": (80, 100),
}


def compute_data_quality_score(master: pd.DataFrame) -> pd.Series:
    """
    Compute a 0-100 data quality score per project.
    Checks completeness of key fields.
    """
    quality = pd.Series(100.0, index=master.index)

    critical_fields = {
        "sanction_amount": 20,
        "recommendation_date": 15,
        "sanction_date": 15,
        "work_description": 15,
        "ida_name": 10,
        "total_expenditure": 15,
        "work_category": 10,
    }

    for field, penalty in critical_fields.items():
        if field in master.columns:
            missing = master[field].isna() | (master[field].astype(str).str.strip() == "")
            quality -= missing * penalty
        else:
            quality -= penalty  # Entire field missing

    # Unavailable fields: reduce quality score to indicate limited analysis
    unavailable_penalty_per_field = 2.5
    unavailable_fields = ["latitude", "longitude", "physical_progress_pct",
                          "financial_progress_pct", "photo_count", "expected_completion_date"]
    for field in unavailable_fields:
        if field in master.columns:
            is_unavailable = master[field].astype(str) == "NOT_AVAILABLE_IN_CURRENT_DATASET"
            quality -= is_unavailable * unavailable_penalty_per_field

    return quality.clip(0, 100).round(1)


def generate_explanations(row: pd.Series) -> List[str]:
    """Generate human-readable top reasons for a project's risk score."""
    reasons = []

    rule_risk = row.get("rule_risk", 0)
    ml_risk = row.get("ml_anomaly_risk", 0)
    dup_risk = row.get("duplicate_risk", 0)
    agency_risk = row.get("agency_risk", 0)

    exp = pd.to_numeric(row.get("total_expenditure"), errors="coerce")
    san = pd.to_numeric(row.get("sanction_amount"), errors="coerce")

    # Expenditure over sanction
    if pd.notna(exp) and pd.notna(san) and san > 0 and exp > san:
        overrun = round(((exp - san) / san) * 100, 1)
        reasons.append(f"Expenditure exceeds sanctioned amount by {overrun}%")

    # High ML anomaly
    if ml_risk >= 70:
        reasons.append("Project is statistically anomalous compared with similar projects (Isolation Forest)")
    elif ml_risk >= 50:
        reasons.append("Project shows moderate statistical deviation from peer projects")

    # Duplicate risk
    if dup_risk >= 70:
        reasons.append("Highly similar work description detected in same constituency")
    elif dup_risk >= 50:
        reasons.append("Moderately similar work description found nearby")

    # Agency risk
    if agency_risk >= 60:
        reasons.append("Implementing agency has elevated historical risk profile")

    # Rule violations
    if rule_risk >= 60:
        reasons.append("Multiple compliance rules triggered")
    elif rule_risk >= 30:
        reasons.append("Compliance rule violation detected")

    # Chronology issues
    rec_dt = pd.to_datetime(row.get("recommendation_date"), errors="coerce")
    san_dt = pd.to_datetime(row.get("sanction_date"), errors="coerce")
    if pd.notna(rec_dt) and pd.notna(san_dt) and san_dt < rec_dt:
        reasons.append("Invalid chronology: sanction date before recommendation date")

    if not reasons:
        reasons.append("No significant risk indicators detected")

    return reasons[:5]  # Top 5 reasons


def compute_composite_risk(master: pd.DataFrame) -> pd.DataFrame:
    """Compute composite risk scores for all projects."""
    print("\n  Computing composite risk scores…")

    # Load component scores
    components = {"rule_risk": None, "ml_anomaly_risk": None, "duplicate_risk": None, "agency_risk": None}

    rule_path = DATA_DIR / "rule_results.csv"
    if rule_path.exists():
        rule_df = pd.read_csv(rule_path)
        components["rule_risk"] = rule_df[["project_id", "rule_risk"]]
        print(f"    Rule risk loaded: {len(rule_df)} projects")

    ml_path = DATA_DIR / "ml_anomaly_scores.csv"
    if ml_path.exists():
        ml_df = pd.read_csv(ml_path)
        components["ml_anomaly_risk"] = ml_df[["project_id", "ml_anomaly_risk"]]
        print(f"    ML anomaly risk loaded: {len(ml_df)} projects")

    dup_path = DATA_DIR / "nlp_duplicate_risk.csv"
    if dup_path.exists():
        dup_df = pd.read_csv(dup_path)
        components["duplicate_risk"] = dup_df[["project_id", "duplicate_risk"]]
        print(f"    Duplicate risk loaded: {len(dup_df)} projects")

    agency_path = DATA_DIR / "project_agency_risk.csv"
    if agency_path.exists():
        agency_df = pd.read_csv(agency_path)
        components["agency_risk"] = agency_df[["project_id", "agency_risk"]]
        print(f"    Agency risk loaded: {len(agency_df)} projects")

    # Merge all components
    result = master[["project_id"]].copy()
    for comp_name, comp_df in components.items():
        if comp_df is not None:
            result = result.merge(comp_df, on="project_id", how="left")
        else:
            result[comp_name] = np.nan
            print(f"    ⚠️  {comp_name}: NOT AVAILABLE")

    # Fill NaN with 0 for available components, leave as NaN for unavailable
    for comp_name in components:
        if components[comp_name] is not None:
            result[comp_name] = result[comp_name].fillna(0.0)

    # ─── Dynamic Weight Re-normalization ───
    # If a component is entirely unavailable (all NaN), exclude its weight
    available_weights = {}
    for comp_name, weight in DEFAULT_WEIGHTS.items():
        if components[comp_name] is not None:
            available_weights[comp_name] = weight

    if not available_weights:
        print("  ERROR: No risk components available!")
        result["risk_score"] = 0.0
    else:
        weight_sum = sum(available_weights.values())
        normalized_weights = {k: v / weight_sum for k, v in available_weights.items()}

        print(f"    Available components: {list(normalized_weights.keys())}")
        print(f"    Normalized weights: {', '.join(f'{k}={v:.2f}' for k, v in normalized_weights.items())}")

        # Compute weighted composite
        result["risk_score"] = sum(
            normalized_weights[comp] * result[comp].fillna(0)
            for comp in normalized_weights
        ).round(1).clip(0, 100)

    # Risk category
    result["risk_category"] = pd.cut(
        result["risk_score"],
        bins=[-1, 29, 59, 79, 101],
        labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )

    # Data quality score
    result["data_quality_score"] = compute_data_quality_score(master)

    # Evidence count (how many non-zero risk components)
    risk_cols = [c for c in components if components[c] is not None]
    result["evidence_count"] = (result[risk_cols] > 0).sum(axis=1)

    # Confidence
    result["confidence"] = np.where(
        result["data_quality_score"] >= 80, "HIGH",
        np.where(result["data_quality_score"] >= 50, "MODERATE", "LOW")
    )

    # Generate explanations
    merged_for_explain = result.merge(
        master[["project_id", "total_expenditure", "sanction_amount",
                "recommendation_date", "sanction_date"]],
        on="project_id", how="left"
    )

    explanations = []
    for _, row in merged_for_explain.iterrows():
        reasons = generate_explanations(row)
        explanations.append("; ".join(reasons))
    result["top_reasons"] = explanations

    return result


def main():
    print("=" * 70)
    print("MPLADS COMPOSITE RISK ENGINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        return

    master = pd.read_csv(master_path, low_memory=False)
    print(f"  Loaded: {master.shape}")

    risk_df = compute_composite_risk(master)

    # Save
    out_path = DATA_DIR / "risk_scores.csv"
    risk_df.to_csv(out_path, index=False)
    print(f"\n✅ Risk scores saved: {out_path}")

    # Summary
    cats = risk_df["risk_category"].value_counts()
    print(f"\n  Risk Distribution:")
    for cat in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        count = cats.get(cat, 0)
        pct = count / len(risk_df) * 100
        emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(cat, "")
        print(f"    {emoji} {cat}: {count} ({pct:.1f}%)")

    print(f"\n  Average risk score: {risk_df['risk_score'].mean():.1f}")
    print(f"  Average data quality: {risk_df['data_quality_score'].mean():.1f}")

    # Important disclaimer
    print("\n  ⚠️  IMPORTANT: Risk Score ≠ Fraud Probability")
    print("     Final decision remains with authorized human reviewers.")

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_projects": len(risk_df),
        "risk_distribution": {cat: int(cats.get(cat, 0)) for cat in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
        "avg_risk_score": round(risk_df["risk_score"].mean(), 1),
        "avg_data_quality": round(risk_df["data_quality_score"].mean(), 1),
        "weights_used": DEFAULT_WEIGHTS,
        "disclaimer": "Risk Score ≠ Fraud Probability. Final decision remains with authorized human reviewers.",
    }
    report_path = REPORT_DIR / "risk_engine_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Report: {report_path}")


if __name__ == "__main__":
    main()
