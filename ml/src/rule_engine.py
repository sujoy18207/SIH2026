"""
PHASE 5 — RULE ENGINE
=====================
Deterministic compliance rule engine for MPLADS anomaly detection.
Evaluates each project against configurable rules based on actually available data.

Each rule returns:
    rule_id, rule_name, triggered, severity, explanation, raw_values, threshold

Final output: normalized RuleRisk score (0-100) per project.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

from config import OUTPUT_DIR, RULE_WEIGHTS, REFERENCE_DATE

DATA_DIR = OUTPUT_DIR


def evaluate_rule_r01(row: pd.Series) -> Optional[dict]:
    """R01: Expenditure exceeds sanctioned amount."""
    exp = pd.to_numeric(row.get("total_expenditure"), errors="coerce")
    san = pd.to_numeric(row.get("sanction_amount"), errors="coerce")

    if pd.isna(exp) or pd.isna(san) or san <= 0:
        return None  # Rule not applicable

    if exp > san:
        overrun_pct = round(((exp - san) / san) * 100, 1)
        severity = "CRITICAL" if overrun_pct >= 20 else "HIGH"
        return {
            "rule_id": "R01",
            "rule_name": "Expenditure Exceeds Sanctioned Amount",
            "triggered": True,
            "severity": severity,
            "explanation": f"Total expenditure (₹{exp:,.0f}) exceeds sanctioned amount (₹{san:,.0f}) by {overrun_pct}%.",
            "raw_values": {"total_expenditure": float(exp), "sanction_amount": float(san), "overrun_pct": overrun_pct},
            "threshold": "Expenditure > Sanction Amount",
        }
    return {"rule_id": "R01", "rule_name": "Expenditure Exceeds Sanctioned Amount",
            "triggered": False, "severity": "NONE", "explanation": "", "raw_values": {}, "threshold": ""}


def evaluate_rule_r02(row: pd.Series) -> Optional[dict]:
    """R02: Sanction date before recommendation date (invalid chronology)."""
    rec_dt = pd.to_datetime(row.get("recommendation_date"), errors="coerce")
    san_dt = pd.to_datetime(row.get("sanction_date"), errors="coerce")

    if pd.isna(rec_dt) or pd.isna(san_dt):
        return None

    if san_dt < rec_dt:
        return {
            "rule_id": "R02",
            "rule_name": "Invalid Chronology — Sanction Before Recommendation",
            "triggered": True,
            "severity": "HIGH",
            "explanation": f"Sanction date ({san_dt.date()}) is before recommendation date ({rec_dt.date()}).",
            "raw_values": {"recommendation_date": str(rec_dt.date()), "sanction_date": str(san_dt.date())},
            "threshold": "sanction_date >= recommendation_date",
        }
    return {"rule_id": "R02", "rule_name": "Invalid Chronology", "triggered": False,
            "severity": "NONE", "explanation": "", "raw_values": {}, "threshold": ""}


def evaluate_rule_r03(row: pd.Series) -> Optional[dict]:
    """R03: High expenditure ratio (>120%) on works that are NOT completed."""
    exp = pd.to_numeric(row.get("total_expenditure"), errors="coerce")
    san = pd.to_numeric(row.get("sanction_amount"), errors="coerce")
    is_completed = row.get("is_completed", False)

    if pd.isna(exp) or pd.isna(san) or san <= 0:
        return None

    ratio = exp / san
    if ratio > 1.2 and not is_completed:
        return {
            "rule_id": "R03",
            "rule_name": "High Expenditure Ratio on Incomplete Work",
            "triggered": True,
            "severity": "HIGH",
            "explanation": f"Expenditure ratio is {ratio:.2f}x ({ratio*100:.0f}%) of sanctioned amount, but work is not completed.",
            "raw_values": {"expenditure_ratio": round(ratio, 2), "is_completed": bool(is_completed)},
            "threshold": "ExpenditureRatio > 1.2 AND is_completed = False",
        }
    return {"rule_id": "R03", "rule_name": "High Expenditure Ratio on Incomplete Work",
            "triggered": False, "severity": "NONE", "explanation": "", "raw_values": {}, "threshold": ""}


def evaluate_rule_r04(row: pd.Series) -> Optional[dict]:
    """R04: Stalled project — old project with very low expenditure ratio."""
    san_dt = pd.to_datetime(row.get("sanction_date"), errors="coerce")
    exp = pd.to_numeric(row.get("total_expenditure"), errors="coerce")
    san = pd.to_numeric(row.get("sanction_amount"), errors="coerce")
    is_completed = row.get("is_completed", False)

    if pd.isna(san_dt) or pd.isna(san) or san <= 0 or is_completed:
        return None

    ref_date = pd.Timestamp(REFERENCE_DATE)
    age_days = (ref_date - san_dt).days

    exp_ratio = (exp / san) if not pd.isna(exp) else 0.0

    if age_days >= 365 and exp_ratio < 0.3:
        return {
            "rule_id": "R04",
            "rule_name": "Stalled Project — Low Expenditure Over Extended Period",
            "triggered": True,
            "severity": "MEDIUM" if age_days < 730 else "HIGH",
            "explanation": f"Project sanctioned {age_days} days ago but expenditure ratio is only {exp_ratio:.2f} ({exp_ratio*100:.0f}%).",
            "raw_values": {"age_days": age_days, "expenditure_ratio": round(exp_ratio, 2)},
            "threshold": "age >= 365 days AND expenditure_ratio < 0.3",
        }
    return {"rule_id": "R04", "rule_name": "Stalled Project", "triggered": False,
            "severity": "NONE", "explanation": "", "raw_values": {}, "threshold": ""}


def evaluate_rule_r05(row: pd.Series) -> Optional[dict]:
    """R05: Completion date before sanction date (impossible chronology)."""
    san_dt = pd.to_datetime(row.get("sanction_date"), errors="coerce")
    comp_dt = pd.to_datetime(row.get("actual_completion_date"), errors="coerce")

    if pd.isna(san_dt) or pd.isna(comp_dt):
        return None

    if comp_dt < san_dt:
        return {
            "rule_id": "R05",
            "rule_name": "Impossible Chronology — Completion Before Sanction",
            "triggered": True,
            "severity": "CRITICAL",
            "explanation": f"Actual completion date ({comp_dt.date()}) is before sanction date ({san_dt.date()}).",
            "raw_values": {"sanction_date": str(san_dt.date()), "actual_completion_date": str(comp_dt.date())},
            "threshold": "actual_completion_date >= sanction_date",
        }
    return {"rule_id": "R05", "rule_name": "Impossible Chronology", "triggered": False,
            "severity": "NONE", "explanation": "", "raw_values": {}, "threshold": ""}


RULE_FUNCTIONS = [evaluate_rule_r01, evaluate_rule_r02, evaluate_rule_r03, evaluate_rule_r04, evaluate_rule_r05]


def evaluate_project(row: pd.Series) -> dict:
    """Evaluate all rules for a single project and compute RuleRisk."""
    results = []
    applicable_weight_sum = 0
    triggered_weight_sum = 0

    for rule_fn in RULE_FUNCTIONS:
        result = rule_fn(row)
        if result is None:
            # Rule not applicable (missing data)
            continue
        results.append(result)
        rule_id = result["rule_id"]
        weight = RULE_WEIGHTS.get(rule_id, 10)
        applicable_weight_sum += weight
        if result["triggered"]:
            triggered_weight_sum += weight

    # Normalize to 0-100
    if applicable_weight_sum > 0:
        rule_risk = round((triggered_weight_sum / applicable_weight_sum) * 100, 1)
    else:
        rule_risk = 0.0

    return {
        "rule_results": results,
        "rule_risk": rule_risk,
        "applicable_rules": len(results),
        "triggered_rules": sum(1 for r in results if r["triggered"]),
        "applicable_weight_sum": applicable_weight_sum,
        "triggered_weight_sum": triggered_weight_sum,
    }


def run_rule_engine(master: pd.DataFrame) -> pd.DataFrame:
    """Run all rules on the master project table using VECTORIZED operations.
    
    Returns (rule_df, detailed_results) where rule_df has per-project scores.
    """
    print(f"\n  Evaluating {len(master)} projects against {len(RULE_FUNCTIONS)} rules…")
    print("  Using vectorized evaluation for performance…")

    # Pre-compute shared numeric columns
    exp = pd.to_numeric(master.get("total_expenditure"), errors="coerce")
    san = pd.to_numeric(master.get("sanction_amount"), errors="coerce")
    rec_dt = pd.to_datetime(master.get("recommendation_date"), errors="coerce")
    san_dt = pd.to_datetime(master.get("sanction_date"), errors="coerce")
    comp_dt = pd.to_datetime(master.get("actual_completion_date"), errors="coerce")
    is_completed = master.get("is_completed", pd.Series(False, index=master.index)).astype(bool)
    ref_date = pd.Timestamp(REFERENCE_DATE)
    age_days = (ref_date - san_dt).dt.days
    exp_ratio = exp / san.replace(0, np.nan)

    # --- R01: Expenditure > Sanctioned Amount ---
    r01_applicable = exp.notna() & san.notna() & (san > 0)
    r01_triggered = r01_applicable & (exp > san)

    # --- R02: Sanction before Recommendation ---
    r02_applicable = rec_dt.notna() & san_dt.notna()
    r02_triggered = r02_applicable & (san_dt < rec_dt)

    # --- R03: High expenditure ratio on incomplete work ---
    r03_applicable = exp.notna() & san.notna() & (san > 0)
    r03_triggered = r03_applicable & (exp_ratio > 1.2) & (~is_completed)

    # --- R04: Stalled project ---
    r04_applicable = san_dt.notna() & san.notna() & (san > 0) & (~is_completed)
    r04_triggered = r04_applicable & (age_days >= 365) & (exp_ratio.fillna(0) < 0.3)

    # --- R05: Completion before sanction ---
    r05_applicable = san_dt.notna() & comp_dt.notna()
    r05_triggered = r05_applicable & (comp_dt < san_dt)

    # Compute RuleRisk vectorized
    rules = {
        "R01": (r01_applicable, r01_triggered),
        "R02": (r02_applicable, r02_triggered),
        "R03": (r03_applicable, r03_triggered),
        "R04": (r04_applicable, r04_triggered),
        "R05": (r05_applicable, r05_triggered),
    }

    applicable_weight = pd.Series(0.0, index=master.index)
    triggered_weight = pd.Series(0.0, index=master.index)
    triggered_count = pd.Series(0, index=master.index)
    applicable_count = pd.Series(0, index=master.index)

    for rule_id, (app_mask, trig_mask) in rules.items():
        w = RULE_WEIGHTS.get(rule_id, 10)
        applicable_weight += app_mask.astype(float) * w
        triggered_weight += trig_mask.astype(float) * w
        applicable_count += app_mask.astype(int)
        triggered_count += trig_mask.astype(int)

    rule_risk = (triggered_weight / applicable_weight.replace(0, np.nan) * 100).fillna(0).round(1)

    rule_df = pd.DataFrame({
        "project_id": master.get("project_id", master.index),
        "rule_risk": rule_risk,
        "applicable_rules": applicable_count,
        "triggered_rules": triggered_count,
    })

    # Summary
    triggered_any = (triggered_count > 0).sum()
    avg_risk = rule_risk.mean()
    high_risk = (rule_risk >= 60).sum()

    print(f"  Projects with ≥1 triggered rule: {triggered_any}")
    print(f"  Average rule risk: {avg_risk:.1f}")
    print(f"  High rule risk (≥60): {high_risk}")

    # Generate detailed results for explainability (top anomalies only to save memory)
    all_results = []
    high_risk_mask = rule_risk >= 30
    for idx in master.index[high_risk_mask]:
        row = master.loc[idx]
        evaluation = evaluate_project(row)
        all_results.append({
            "project_id": row.get("project_id"),
            **evaluation,
        })

    return rule_df, all_results


def main():
    print("=" * 70)
    print("MPLADS RULE ENGINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        return

    master = pd.read_csv(master_path, low_memory=False)
    print(f"  Loaded: {master.shape}")

    rule_df, detailed_results = run_rule_engine(master)

    # Save rule risk scores
    out_path = DATA_DIR / "rule_results.csv"
    rule_df.to_csv(out_path, index=False)
    print(f"\n✅ Rule results saved: {out_path}")

    # Save detailed results as JSON
    json_path = DATA_DIR / "rule_results_detailed.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=2, default=str)
    print(f"   Detailed: {json_path}")


if __name__ == "__main__":
    main()
