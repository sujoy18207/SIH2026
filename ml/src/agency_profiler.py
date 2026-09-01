"""
PHASE 8 — AGENCY / VENDOR PROFILER
====================================
Computes historical risk profiles for implementing agencies (IDA) and
vendors (contractors) based on aggregated project-level metrics.

Agency Risk Formula:
    AgencyRisk = 0.40 × DelayRisk + 0.30 × CostRisk + 0.30 × HistoricalAnomalyRisk
    (all components normalized to 0-100)

Minimum 10 projects required for reliable statistics.
Below threshold: agency_risk_confidence = LOW

Output:
    ml/data/agency_risk.csv     — per-agency risk profile
    ml/data/vendor_risk.csv     — per-vendor risk profile
    ml/data/project_agency_risk.csv — agency risk mapped back to projects
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from config import (OUTPUT_DIR, REPORT_DIR, MIN_PROJECTS_RELIABLE,
                    COST_ANOMALY_THRESHOLD, AGENCY_RISK_WEIGHTS, REFERENCE_DATE)

DATA_DIR = OUTPUT_DIR


def profile_agencies(master: pd.DataFrame, rule_df: pd.DataFrame = None) -> pd.DataFrame:
    """Compute risk profiles for implementing district authorities (IDA)."""
    print("\n  Profiling implementing agencies (IDA)…")

    if "ida_name" not in master.columns:
        print("    WARNING: ida_name column not found.")
        return pd.DataFrame()

    # Merge rule risk if available
    if rule_df is not None and "project_id" in rule_df.columns:
        df = master.merge(rule_df[["project_id", "rule_risk"]], on="project_id", how="left")
    else:
        df = master.copy()
        df["rule_risk"] = 0.0

    # Ensure numeric columns
    df["total_expenditure"] = pd.to_numeric(df.get("total_expenditure"), errors="coerce").fillna(0)
    df["sanction_amount"] = pd.to_numeric(df.get("sanction_amount"), errors="coerce").fillna(0)

    # Calculate per-project flags
    df["_is_cost_anomaly"] = (df["total_expenditure"] > df["sanction_amount"] * COST_ANOMALY_THRESHOLD) & (df["sanction_amount"] > 0)
    df["_is_completed"] = df.get("is_completed", False).astype(bool)

    # Check for stalled projects (project age > 365, low expenditure)
    san_dt = pd.to_datetime(df.get("sanction_date"), errors="coerce")
    ref_date = pd.Timestamp(REFERENCE_DATE)
    df["_age_days"] = (ref_date - san_dt).dt.days.fillna(0)
    exp_ratio = df["total_expenditure"] / df["sanction_amount"].replace(0, np.nan)
    df["_is_stalled"] = (df["_age_days"] >= 365) & (exp_ratio < 0.3) & (~df["_is_completed"])

    # Aggregate by agency
    agency_stats = df.groupby("ida_name").agg(
        total_projects=("project_id", "count"),
        completed_projects=("_is_completed", "sum"),
        stalled_projects=("_is_stalled", "sum"),
        cost_anomaly_projects=("_is_cost_anomaly", "sum"),
        total_expenditure=("total_expenditure", "sum"),
        total_sanction=("sanction_amount", "sum"),
        avg_rule_risk=("rule_risk", "mean"),
        max_rule_risk=("rule_risk", "max"),
        unique_states=("state_name", "nunique"),
        unique_constituencies=("constituency", "nunique"),
    ).reset_index()

    # Compute rates
    agency_stats["completion_rate"] = agency_stats["completed_projects"] / agency_stats["total_projects"]
    agency_stats["stall_rate"] = agency_stats["stalled_projects"] / agency_stats["total_projects"]
    agency_stats["cost_anomaly_rate"] = agency_stats["cost_anomaly_projects"] / agency_stats["total_projects"]

    # Normalize to 0-100
    agency_stats["delay_risk_normalized"] = (agency_stats["stall_rate"] * 100).clip(0, 100)
    agency_stats["cost_risk_normalized"] = (agency_stats["cost_anomaly_rate"] * 100).clip(0, 100)
    agency_stats["historical_anomaly_risk"] = agency_stats["avg_rule_risk"].clip(0, 100)

    # Composite agency risk
    agency_stats["agency_risk"] = (
        0.40 * agency_stats["delay_risk_normalized"] +
        0.30 * agency_stats["cost_risk_normalized"] +
        0.30 * agency_stats["historical_anomaly_risk"]
    ).round(1)

    # Confidence based on project count
    agency_stats["agency_risk_confidence"] = np.where(
        agency_stats["total_projects"] >= MIN_PROJECTS_RELIABLE,
        "HIGH",
        np.where(agency_stats["total_projects"] >= 5, "MEDIUM", "LOW")
    )

    # Risk category
    agency_stats["agency_risk_category"] = pd.cut(
        agency_stats["agency_risk"],
        bins=[-1, 29, 59, 79, 101],
        labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )

    print(f"    Total agencies: {len(agency_stats)}")
    print(f"    Reliable profiles (≥{MIN_PROJECTS_RELIABLE} projects): {(agency_stats['total_projects'] >= MIN_PROJECTS_RELIABLE).sum()}")

    return agency_stats


def profile_vendors(master: pd.DataFrame) -> pd.DataFrame:
    """Compute risk profiles for vendors (contractors)."""
    print("\n  Profiling vendors…")

    if "vendor_name" not in master.columns:
        print("    WARNING: vendor_name column not found.")
        return pd.DataFrame()

    df = master[master["vendor_name"].notna()].copy()
    if df.empty:
        return pd.DataFrame()

    df["total_expenditure"] = pd.to_numeric(df.get("total_expenditure"), errors="coerce").fillna(0)
    df["sanction_amount"] = pd.to_numeric(df.get("sanction_amount"), errors="coerce").fillna(0)

    vendor_stats = df.groupby("vendor_name").agg(
        total_projects=("project_id", "count"),
        unique_constituencies=("constituency", "nunique"),
        unique_states=("state_name", "nunique"),
        total_expenditure=("total_expenditure", "sum"),
        avg_expenditure=("total_expenditure", "mean"),
    ).reset_index()

    # Vendor concentration risk: vendors with many projects in same constituency
    vendor_constituency = df.groupby(["vendor_name", "constituency"]).size().reset_index(name="projects_in_constituency")
    max_concentration = vendor_constituency.groupby("vendor_name")["projects_in_constituency"].max().reset_index()
    max_concentration.columns = ["vendor_name", "max_constituency_concentration"]
    vendor_stats = vendor_stats.merge(max_concentration, on="vendor_name", how="left")

    vendor_stats["vendor_risk_confidence"] = np.where(
        vendor_stats["total_projects"] >= MIN_PROJECTS_RELIABLE, "HIGH",
        np.where(vendor_stats["total_projects"] >= 5, "MEDIUM", "LOW")
    )

    print(f"    Total vendors: {len(vendor_stats)}")
    print(f"    Reliable profiles (≥{MIN_PROJECTS_RELIABLE} projects): {(vendor_stats['total_projects'] >= MIN_PROJECTS_RELIABLE).sum()}")

    return vendor_stats


def map_agency_risk_to_projects(master: pd.DataFrame, agency_stats: pd.DataFrame) -> pd.DataFrame:
    """Map agency risk scores back to individual projects."""
    if agency_stats.empty:
        result = master[["project_id"]].copy()
        result["agency_risk"] = 0.0
        result["agency_risk_confidence"] = "UNAVAILABLE"
        return result

    mapping = agency_stats[["ida_name", "agency_risk", "agency_risk_confidence"]].copy()
    result = master[["project_id", "ida_name"]].merge(mapping, on="ida_name", how="left")
    result["agency_risk"] = result["agency_risk"].fillna(0.0)
    result["agency_risk_confidence"] = result["agency_risk_confidence"].fillna("UNAVAILABLE")
    result = result.drop(columns=["ida_name"])

    return result


def main():
    print("=" * 70)
    print("MPLADS AGENCY / VENDOR PROFILER")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        return

    master = pd.read_csv(master_path, low_memory=False)
    print(f"  Loaded: {master.shape}")

    # Load rule results if available
    rule_path = DATA_DIR / "rule_results.csv"
    rule_df = pd.read_csv(rule_path) if rule_path.exists() else None

    agency_stats = profile_agencies(master, rule_df)
    vendor_stats = profile_vendors(master)
    project_agency_risk = map_agency_risk_to_projects(master, agency_stats)

    # Save
    if not agency_stats.empty:
        agency_stats.to_csv(DATA_DIR / "agency_risk.csv", index=False)
        print(f"\n✅ Agency risk profiles: {DATA_DIR / 'agency_risk.csv'}")

    if not vendor_stats.empty:
        vendor_stats.to_csv(DATA_DIR / "vendor_risk.csv", index=False)
        print(f"   Vendor risk profiles: {DATA_DIR / 'vendor_risk.csv'}")

    project_agency_risk.to_csv(DATA_DIR / "project_agency_risk.csv", index=False)
    print(f"   Project agency risk mapping: {DATA_DIR / 'project_agency_risk.csv'}")


if __name__ == "__main__":
    main()
