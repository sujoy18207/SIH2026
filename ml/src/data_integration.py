"""
PHASE 3 — DATA INTEGRATION
============================
Creates a unified project-level master table by joining cleaned datasets
on WORK_RECOMMENDATION_DTL_ID.

Join strategy:
    works_recommended (base) 
        LEFT JOIN works_sanctioned (on DTL_ID)
        LEFT JOIN works_completed (on DTL_ID)
        LEFT JOIN expenditure (aggregated per DTL_ID)
        LEFT JOIN mp_allocation (on MP_NAME + CONSTITUENCY)

Output:
    ml/data/master_projects.csv — one row per unique project
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from config import CLEANED_DIR, OUTPUT_DIR, JOIN_KEY, PROJECT_ROOT


def load_cleaned(filename: str) -> pd.DataFrame:
    """Load a cleaned CSV from the cleaned data directory."""
    fpath = CLEANED_DIR / filename
    if fpath.exists():
        df = pd.read_csv(fpath, low_memory=False)
        print(f"  Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
        return df
    else:
        print(f"  WARNING: {filename} not found, skipping.")
        return pd.DataFrame()


def aggregate_expenditure(df_exp: pd.DataFrame) -> pd.DataFrame:
    """Aggregate expenditure records to one row per project (DTL_ID)."""
    if df_exp.empty or JOIN_KEY not in df_exp.columns:
        return pd.DataFrame()

    print(f"  Aggregating expenditure: {len(df_exp)} payment records…")

    # Ensure numeric
    if "FUND_DISBURSED_AMT" in df_exp.columns:
        df_exp["FUND_DISBURSED_AMT"] = pd.to_numeric(df_exp["FUND_DISBURSED_AMT"], errors="coerce")

    # Parse dates for min/max
    if "EXPENDITURE_DATE" in df_exp.columns:
        df_exp["EXPENDITURE_DATE"] = pd.to_datetime(df_exp["EXPENDITURE_DATE"], errors="coerce")

    agg = df_exp.groupby(JOIN_KEY).agg(
        total_expenditure=("FUND_DISBURSED_AMT", "sum"),
        max_single_payment=("FUND_DISBURSED_AMT", "max"),
        payment_count=("FUND_DISBURSED_AMT", "count"),
        first_expenditure_date=("EXPENDITURE_DATE", "min"),
        last_expenditure_date=("EXPENDITURE_DATE", "max"),
        vendor_name=("VENDOR_NAME", "first"),
        vendor_id=("VENDOR_ID", "first"),
        ia_name=("IA_NAME", "first"),
        work_status_exp=("WORK_STATUS", "first"),
        unique_vendors=("VENDOR_NAME", "nunique"),
    ).reset_index()

    print(f"  Aggregated to {len(agg)} project-level expenditure records")
    return agg


def build_master_table() -> pd.DataFrame:
    """Build the unified master project table."""
    print("\n" + "=" * 70)
    print("BUILDING MASTER PROJECT TABLE")
    print("=" * 70)

    # Load cleaned datasets
    df_rec = load_cleaned("works_recommended_all.csv")
    df_san = load_cleaned("works_sanctioned_all.csv")
    df_comp = load_cleaned("works_completed_all.csv")
    df_exp = load_cleaned("expenditure_all.csv")
    df_alloc = load_cleaned("mp_allocation_all.csv")

    if df_rec.empty:
        print("ERROR: Works recommended dataset is empty. Cannot build master table.")
        return pd.DataFrame()

    # Ensure JOIN_KEY is integer type across all datasets
    for df_name, df in [("recommended", df_rec), ("sanctioned", df_san),
                         ("completed", df_comp), ("expenditure", df_exp)]:
        if not df.empty and JOIN_KEY in df.columns:
            df[JOIN_KEY] = pd.to_numeric(df[JOIN_KEY], errors="coerce")

    # --- BASE: Works Recommended ---
    master = df_rec[[c for c in df_rec.columns if c != "_is_valid"]].copy()
    master = master.rename(columns={
        "RECOMMENDED_AMOUNT": "recommended_amount",
        "SANCTION_AMOUNT": "sanction_amount_rec",
        "RECOMMENDATION_DATE": "recommendation_date",
        "SANCTION_DATE": "sanction_date_rec",
        "WORK_DESCRIPTION": "work_description",
        "STATE_NAME": "state_name",
        "CONSTITUENCY": "constituency",
        "MP_NAME": "mp_name",
        "IDA_NAME": "ida_name",
        "WORK_CATEGORY": "work_category",
        "ACTIVITY_NAME": "activity_name",
        "TENURE": "tenure",
        "HOUSE_OF_PARLIAMENT": "house_of_parliament",
        "WORK_STAGE": "work_stage",
        "LETTER_NO": "letter_no",
        "CONSTITUENCY_ID": "constituency_id",
        "FILE_STATUS": "file_status",
        "ATTACH_ID": "attach_id_rec",
    })
    master = master.rename(columns={JOIN_KEY: "project_id"})

    print(f"\n  Base (recommended): {len(master)} projects")

    # --- JOIN: Works Sanctioned ---
    if not df_san.empty and JOIN_KEY in df_san.columns:
        san_cols = [JOIN_KEY]
        if "SANCTION_AMOUNT" in df_san.columns:
            san_cols.append("SANCTION_AMOUNT")
        if "SANCTION_DATE" in df_san.columns:
            san_cols.append("SANCTION_DATE")
        if "WORK_STAGE" in df_san.columns:
            df_san = df_san.rename(columns={"WORK_STAGE": "WORK_STAGE_SAN"})
            san_cols.append("WORK_STAGE_SAN")

        df_san_dedup = df_san[san_cols].drop_duplicates(subset=[JOIN_KEY], keep="first")
        df_san_dedup = df_san_dedup.rename(columns={
            JOIN_KEY: "project_id",
            "SANCTION_AMOUNT": "sanction_amount_san",
            "SANCTION_DATE": "sanction_date_san",
        })

        master = master.merge(df_san_dedup, on="project_id", how="left")
        matched = master["sanction_amount_san"].notna().sum() if "sanction_amount_san" in master.columns else 0
        print(f"  Joined sanctioned: {matched} projects matched")

    # --- JOIN: Works Completed ---
    if not df_comp.empty and JOIN_KEY in df_comp.columns:
        comp_cols = [JOIN_KEY]
        for c in ["ACTUAL_END_DATE", "ACTUAL_AMOUNT", "AVERAGE_RATING", "WORK_ID"]:
            if c in df_comp.columns:
                comp_cols.append(c)

        df_comp_dedup = df_comp[comp_cols].drop_duplicates(subset=[JOIN_KEY], keep="first")
        df_comp_dedup = df_comp_dedup.rename(columns={
            JOIN_KEY: "project_id",
            "ACTUAL_END_DATE": "actual_completion_date",
            "ACTUAL_AMOUNT": "actual_amount",
            "AVERAGE_RATING": "average_rating",
            "WORK_ID": "work_id_completed",
        })

        master = master.merge(df_comp_dedup, on="project_id", how="left")
        matched = master["actual_completion_date"].notna().sum() if "actual_completion_date" in master.columns else 0
        print(f"  Joined completed: {matched} projects matched")

    # --- JOIN: Expenditure (aggregated) ---
    if not df_exp.empty:
        df_exp_agg = aggregate_expenditure(df_exp)
        if not df_exp_agg.empty:
            df_exp_agg = df_exp_agg.rename(columns={JOIN_KEY: "project_id"})
            master = master.merge(df_exp_agg, on="project_id", how="left")
            matched = master["total_expenditure"].notna().sum() if "total_expenditure" in master.columns else 0
            print(f"  Joined expenditure: {matched} projects matched")

    # --- JOIN: MP Allocation (on MP_NAME + CONSTITUENCY) ---
    if not df_alloc.empty and "MP_NAME" in df_alloc.columns:
        alloc_dedup = df_alloc.rename(columns={
            "ALLOCATED_AMT": "mp_allocated_amount",
        })
        # Normalize for join
        alloc_dedup["_mp_join"] = alloc_dedup["MP_NAME"].str.upper().str.strip()
        master["_mp_join"] = master["mp_name"].str.upper().str.strip()

        alloc_subset = alloc_dedup[["_mp_join", "mp_allocated_amount"]].drop_duplicates(
            subset=["_mp_join"], keep="first"
        )
        master = master.merge(alloc_subset, on="_mp_join", how="left")
        master = master.drop(columns=["_mp_join"], errors="ignore")
        matched = master["mp_allocated_amount"].notna().sum() if "mp_allocated_amount" in master.columns else 0
        print(f"  Joined MP allocation: {matched} projects matched")

    # --- Derive unified columns ---
    # Use sanctioned amount from sanctioned dataset if available, else from recommended
    if "sanction_amount_san" in master.columns:
        master["sanction_amount"] = master["sanction_amount_san"].fillna(master.get("sanction_amount_rec", np.nan))
    elif "sanction_amount_rec" in master.columns:
        master["sanction_amount"] = master["sanction_amount_rec"]
    else:
        master["sanction_amount"] = np.nan

    if "sanction_date_san" in master.columns:
        master["sanction_date"] = pd.to_datetime(master["sanction_date_san"], errors="coerce").fillna(
            pd.to_datetime(master.get("sanction_date_rec"), errors="coerce")
        )
    elif "sanction_date_rec" in master.columns:
        master["sanction_date"] = pd.to_datetime(master["sanction_date_rec"], errors="coerce")

    # Determine project status
    master["is_completed"] = master.get("actual_completion_date", pd.Series(dtype="object")).notna()
    master["has_expenditure"] = master.get("total_expenditure", pd.Series(dtype="float")).notna() & (
        master.get("total_expenditure", 0) > 0
    )

    # Fill unavailable fields
    unavailable_fields = [
        "latitude", "longitude", "physical_progress_pct", "financial_progress_pct",
        "photo_count", "expected_completion_date",
    ]
    for field in unavailable_fields:
        master[field] = "NOT_AVAILABLE_IN_CURRENT_DATASET"

    # --- Final column selection ---
    desired_cols = [
        "project_id", "work_category", "activity_name", "state_name", "constituency",
        "constituency_id", "ida_name", "ia_name", "mp_name", "tenure",
        "house_of_parliament", "work_description", "letter_no",
        "recommendation_date", "sanction_date", "actual_completion_date",
        "recommended_amount", "sanction_amount", "actual_amount",
        "total_expenditure", "max_single_payment", "payment_count",
        "first_expenditure_date", "last_expenditure_date",
        "vendor_name", "vendor_id", "unique_vendors",
        "work_stage", "work_status_exp", "file_status",
        "average_rating", "mp_allocated_amount",
        "is_completed", "has_expenditure",
        "attach_id_rec",
        # Unavailable fields (documented)
        "latitude", "longitude", "physical_progress_pct", "financial_progress_pct",
        "photo_count", "expected_completion_date",
    ]

    # Only keep columns that actually exist
    final_cols = [c for c in desired_cols if c in master.columns]
    master = master[final_cols]

    print(f"\n  Master table: {len(master)} rows × {len(master.columns)} columns")
    print(f"  Columns: {list(master.columns)}")

    return master


def main():
    print("=" * 70)
    print("MPLADS DATA INTEGRATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master = build_master_table()

    if master.empty:
        print("ERROR: Master table is empty. Check cleaned data.")
        return

    # Save
    out_path = OUTPUT_DIR / "master_projects.csv"
    master.to_csv(out_path, index=False)
    print(f"\n✅ Master project table saved: {out_path}")
    print(f"   Shape: {master.shape}")

    # Save integration metadata
    meta = {
        "created_at": datetime.now().isoformat(),
        "total_projects": len(master),
        "total_columns": len(master.columns),
        "columns": list(master.columns),
        "completed_projects": int(master["is_completed"].sum()) if "is_completed" in master.columns else 0,
        "projects_with_expenditure": int(master["has_expenditure"].sum()) if "has_expenditure" in master.columns else 0,
        "unavailable_fields": [
            "latitude", "longitude", "physical_progress_pct",
            "financial_progress_pct", "photo_count", "expected_completion_date",
        ],
        "join_key": "WORK_RECOMMENDATION_DTL_ID (mapped to project_id)",
    }
    meta_path = OUTPUT_DIR / "master_projects_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"   Metadata: {meta_path}")

    # Quick stats
    print(f"\n  Quick Statistics:")
    print(f"    Unique states: {master['state_name'].nunique()}")
    print(f"    Unique constituencies: {master['constituency'].nunique()}")
    print(f"    Unique MPs: {master['mp_name'].nunique()}")
    print(f"    Unique IDAs: {master['ida_name'].nunique()}")
    if "total_expenditure" in master.columns:
        total_exp = master["total_expenditure"].sum()
        print(f"    Total expenditure: ₹{total_exp:,.2f}")
    if "sanction_amount" in master.columns:
        total_sanc = master["sanction_amount"].sum()
        print(f"    Total sanctioned: ₹{total_sanc:,.2f}")


if __name__ == "__main__":
    main()
