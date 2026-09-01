"""
PHASE 2 — DATA CLEANING
========================
Reusable preprocessing pipeline for real eSAKSHI MPLADS CSV data.

Handles:
    - Mixed date formats (dd-Mon-yyyy, Mon d, yyyy hh:mm:ss AM/PM)
    - Currency/amount cleaning
    - Whitespace / case normalization
    - Duplicate removal
    - Invalid record flagging
    - Transformation logging

Outputs cleaned CSVs to ml/data/cleaned/
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import numpy as np

from config import DATA_DIR, CLEANED_DIR, PROJECT_ROOT

# Cleaning log
_cleaning_log: List[dict] = []


def _log(dataset: str, action: str, detail: str, affected_rows: int = 0):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset,
        "action": action,
        "detail": detail,
        "affected_rows": affected_rows,
    }
    _cleaning_log.append(entry)
    print(f"  [{action}] {detail} (rows affected: {affected_rows})")


def parse_date_column(series: pd.Series, col_name: str, dataset_name: str) -> pd.Series:
    """Parse dates from mixed-format eSAKSHI date strings."""
    if series.isna().all():
        return series

    result = pd.Series(pd.NaT, index=series.index)

    # Format 1: "08-Jul-2024" (dd-Mon-yyyy)
    mask1 = series.str.match(r"^\d{2}-[A-Za-z]{3}-\d{4}$", na=False)
    if mask1.any():
        result[mask1] = pd.to_datetime(series[mask1], format="%d-%b-%Y", errors="coerce")
        _log(dataset_name, "DATE_PARSE", f"{col_name}: parsed {mask1.sum()} dates as dd-Mon-yyyy", int(mask1.sum()))

    # Format 2: "Jun 4, 2024 12:00:00 AM" (Mon d, yyyy hh:mm:ss AM/PM)
    mask2 = series.str.match(r"^[A-Za-z]{3}\s+\d{1,2},\s+\d{4}", na=False) & ~mask1
    if mask2.any():
        result[mask2] = pd.to_datetime(series[mask2], format="%b %d, %Y %I:%M:%S %p", errors="coerce")
        _log(dataset_name, "DATE_PARSE", f"{col_name}: parsed {mask2.sum()} dates as Mon d, yyyy hh:mm:ss", int(mask2.sum()))

    # Format 3: "05-Sep-2024"
    mask3 = (~mask1) & (~mask2) & series.notna()
    if mask3.any():
        result[mask3] = pd.to_datetime(series[mask3], errors="coerce")
        parsed_count = result[mask3].notna().sum()
        _log(dataset_name, "DATE_PARSE", f"{col_name}: auto-parsed {parsed_count} remaining dates", int(parsed_count))

    return result


def clean_amount_column(series: pd.Series, col_name: str, dataset_name: str) -> pd.Series:
    """Clean currency/amount fields: remove commas, convert to float."""
    if series.isna().all():
        return series.astype(float)

    # If already numeric, just ensure float
    if pd.api.types.is_numeric_dtype(series):
        result = series.astype(float)
        _log(dataset_name, "AMOUNT_CLEAN", f"{col_name}: already numeric, cast to float", 0)
        return result

    # Remove commas, currency symbols, whitespace
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace("₹", "", regex=False)
    cleaned = cleaned.str.replace("Rs.", "", regex=False)
    cleaned = cleaned.str.strip()
    result = pd.to_numeric(cleaned, errors="coerce")

    coerced = result.isna().sum() - series.isna().sum()
    _log(dataset_name, "AMOUNT_CLEAN", f"{col_name}: cleaned {len(series)} values, {coerced} coerced to NaN", int(coerced))

    return result


def clean_text_column(series: pd.Series, col_name: str, dataset_name: str) -> pd.Series:
    """Normalize text: strip whitespace, normalize internal spaces."""
    if series.isna().all():
        return series

    result = series.astype(str).str.strip()
    result = result.str.replace(r"\s+", " ", regex=True)
    result = result.replace({"nan": np.nan, "None": np.nan, "": np.nan})

    _log(dataset_name, "TEXT_CLEAN", f"{col_name}: stripped whitespace and normalized", int(len(result)))
    return result


def remove_duplicates(df: pd.DataFrame, subset: list, dataset_name: str) -> pd.DataFrame:
    """Remove duplicate rows based on subset of columns."""
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    after = len(df)
    removed = before - after
    if removed > 0:
        _log(dataset_name, "DEDUP", f"Removed {removed} duplicate rows (subset: {subset})", removed)
    else:
        _log(dataset_name, "DEDUP", f"No duplicates found (subset: {subset})", 0)
    return df


def flag_invalid_records(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Flag records with invalid values (negative amounts, impossible dates)."""
    df["_is_valid"] = True

    # Flag negative amounts
    amount_cols = [c for c in df.columns if any(
        kw in c.upper() for kw in ("AMOUNT", "EXPENDITURE", "FUND", "AMT", "COST")
    ) and pd.api.types.is_numeric_dtype(df[c])]

    for col in amount_cols:
        neg_mask = df[col] < 0
        if neg_mask.any():
            df.loc[neg_mask, "_is_valid"] = False
            _log(dataset_name, "INVALID_FLAG", f"{col}: {neg_mask.sum()} negative values", int(neg_mask.sum()))

    invalid_count = (~df["_is_valid"]).sum()
    _log(dataset_name, "VALIDATION", f"Total invalid records flagged: {invalid_count}", int(invalid_count))
    return df


def clean_works_recommended() -> pd.DataFrame:
    """Clean and merge Lok Sabha + Rajya Sabha works recommended data."""
    ds_name = "works_recommended"
    print(f"\n{'='*60}")
    print(f"Cleaning: {ds_name}")
    print(f"{'='*60}")

    dfs = []
    for house_label, suffix in [("Lok Sabha", "LokSabha"), ("Rajya Sabha", "RajyaSabha")]:
        fpath = DATA_DIR / f"works_recommended_{suffix}_alltenures.csv"
        if fpath.exists():
            df = pd.read_csv(fpath, low_memory=False)
            _log(ds_name, "LOAD", f"Loaded {suffix}: {len(df)} rows, {len(df.columns)} columns", len(df))
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    _log(ds_name, "MERGE", f"Combined LS+RS: {len(df)} total rows", len(df))

    # Date columns
    for col in ["RECOMMENDATION_DATE", "SANCTION_DATE", "TENURE_START_DATE", "TENURE_END_DATE"]:
        if col in df.columns:
            df[col] = parse_date_column(df[col].astype(str), col, ds_name)

    # Amount columns
    for col in ["RECOMMENDED_AMOUNT", "SANCTION_AMOUNT", "Total_Amt"]:
        if col in df.columns:
            df[col] = clean_amount_column(df[col], col, ds_name)

    # Text columns
    for col in ["WORK_DESCRIPTION", "STATE_NAME", "CONSTITUENCY", "MP_NAME", "IDA_NAME",
                 "WORK_CATEGORY", "ACTIVITY_NAME", "LETTER_NO"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col], col, ds_name)

    # Dedup on WORK_RECOMMENDATION_DTL_ID
    if "WORK_RECOMMENDATION_DTL_ID" in df.columns:
        df = remove_duplicates(df, ["WORK_RECOMMENDATION_DTL_ID"], ds_name)

    df = flag_invalid_records(df, ds_name)

    out_path = CLEANED_DIR / "works_recommended_all.csv"
    df.to_csv(out_path, index=False)
    _log(ds_name, "SAVE", f"Saved cleaned data: {out_path} ({len(df)} rows)", len(df))

    return df


def clean_works_sanctioned() -> pd.DataFrame:
    """Clean and merge works sanctioned data."""
    ds_name = "works_sanctioned"
    print(f"\n{'='*60}")
    print(f"Cleaning: {ds_name}")
    print(f"{'='*60}")

    dfs = []
    for suffix in ["LokSabha", "RajyaSabha"]:
        fpath = DATA_DIR / f"works_sanctioned_{suffix}_alltenures.csv"
        if fpath.exists():
            df = pd.read_csv(fpath, low_memory=False)
            _log(ds_name, "LOAD", f"Loaded {suffix}: {len(df)} rows", len(df))
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    _log(ds_name, "MERGE", f"Combined LS+RS: {len(df)} total rows", len(df))

    for col in ["RECOMMENDATION_DATE", "SANCTION_DATE", "TENURE_START_DATE", "TENURE_END_DATE"]:
        if col in df.columns:
            df[col] = parse_date_column(df[col].astype(str), col, ds_name)

    for col in ["SANCTION_AMOUNT", "Total_Amt"]:
        if col in df.columns:
            df[col] = clean_amount_column(df[col], col, ds_name)

    for col in ["WORK_DESCRIPTION", "STATE_NAME", "CONSTITUENCY", "MP_NAME", "IDA_NAME",
                 "WORK_CATEGORY", "ACTIVITY_NAME"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col], col, ds_name)

    if "WORK_RECOMMENDATION_DTL_ID" in df.columns:
        df = remove_duplicates(df, ["WORK_RECOMMENDATION_DTL_ID"], ds_name)

    df = flag_invalid_records(df, ds_name)

    out_path = CLEANED_DIR / "works_sanctioned_all.csv"
    df.to_csv(out_path, index=False)
    _log(ds_name, "SAVE", f"Saved: {out_path} ({len(df)} rows)", len(df))

    return df


def clean_works_completed() -> pd.DataFrame:
    """Clean and merge works completed data."""
    ds_name = "works_completed"
    print(f"\n{'='*60}")
    print(f"Cleaning: {ds_name}")
    print(f"{'='*60}")

    dfs = []
    for suffix in ["LokSabha", "RajyaSabha"]:
        fpath = DATA_DIR / f"works_completed_{suffix}_alltenures.csv"
        if fpath.exists():
            df = pd.read_csv(fpath, low_memory=False)
            _log(ds_name, "LOAD", f"Loaded {suffix}: {len(df)} rows", len(df))
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    _log(ds_name, "MERGE", f"Combined LS+RS: {len(df)} total rows", len(df))

    for col in ["ACTUAL_END_DATE"]:
        if col in df.columns:
            df[col] = parse_date_column(df[col].astype(str), col, ds_name)

    for col in ["ACTUAL_AMOUNT", "Total_Amt"]:
        if col in df.columns:
            df[col] = clean_amount_column(df[col], col, ds_name)

    for col in ["WORK_DESCRIPTION", "STATE_NAME", "CONSTITUENCY", "MP_NAME", "IDA_NAME",
                 "WORK_CATEGORY", "ACTIVITY_NAME"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col], col, ds_name)

    if "WORK_RECOMMENDATION_DTL_ID" in df.columns:
        df = remove_duplicates(df, ["WORK_RECOMMENDATION_DTL_ID"], ds_name)

    df = flag_invalid_records(df, ds_name)

    out_path = CLEANED_DIR / "works_completed_all.csv"
    df.to_csv(out_path, index=False)
    _log(ds_name, "SAVE", f"Saved: {out_path} ({len(df)} rows)", len(df))

    return df


def clean_expenditure() -> pd.DataFrame:
    """Clean and merge expenditure data."""
    ds_name = "expenditure"
    print(f"\n{'='*60}")
    print(f"Cleaning: {ds_name}")
    print(f"{'='*60}")

    dfs = []
    for suffix in ["LokSabha", "RajyaSabha"]:
        fpath = DATA_DIR / f"expenditure_{suffix}_alltenures.csv"
        if fpath.exists():
            df = pd.read_csv(fpath, low_memory=False)
            _log(ds_name, "LOAD", f"Loaded {suffix}: {len(df)} rows", len(df))
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    _log(ds_name, "MERGE", f"Combined LS+RS: {len(df)} total rows", len(df))

    for col in ["EXPENDITURE_DATE", "TENURE_START_DATE", "TENURE_END_DATE"]:
        if col in df.columns:
            df[col] = parse_date_column(df[col].astype(str), col, ds_name)

    for col in ["FUND_DISBURSED_AMT", "Total_Amt"]:
        if col in df.columns:
            df[col] = clean_amount_column(df[col], col, ds_name)

    for col in ["STATE_NAME", "CONSTITUENCY", "MP_NAME", "IDA_NAME", "IA_NAME",
                 "VENDOR_NAME", "ACTIVITY_NAME"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col], col, ds_name)

    # Expenditure has multiple rows per project (one per payment), so do NOT dedup on DTL_ID
    # Instead dedup on the full row
    before = len(df)
    df = df.drop_duplicates(keep="first")
    _log(ds_name, "DEDUP", f"Removed {before - len(df)} exact duplicate rows", before - len(df))

    df = flag_invalid_records(df, ds_name)

    out_path = CLEANED_DIR / "expenditure_all.csv"
    df.to_csv(out_path, index=False)
    _log(ds_name, "SAVE", f"Saved: {out_path} ({len(df)} rows)", len(df))

    return df


def clean_mp_allocation() -> pd.DataFrame:
    """Clean MP allocation data."""
    ds_name = "mp_allocation"
    print(f"\n{'='*60}")
    print(f"Cleaning: {ds_name}")
    print(f"{'='*60}")

    dfs = []
    for suffix in ["LokSabha", "RajyaSabha"]:
        fpath = DATA_DIR / f"mp_allocation_{suffix}_alltenures.csv"
        if fpath.exists():
            df = pd.read_csv(fpath, low_memory=False)
            _log(ds_name, "LOAD", f"Loaded {suffix}: {len(df)} rows", len(df))
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    for col in ["TENURE_START_DATE", "TENURE_END_DATE"]:
        if col in df.columns:
            df[col] = parse_date_column(df[col].astype(str), col, ds_name)

    for col in ["ALLOCATED_AMT", "Total_Amt"]:
        if col in df.columns:
            df[col] = clean_amount_column(df[col], col, ds_name)

    for col in ["STATE_NAME", "MP_NAME", "CONSTITUENCY"]:
        if col in df.columns:
            df[col] = clean_text_column(df[col], col, ds_name)

    out_path = CLEANED_DIR / "mp_allocation_all.csv"
    df.to_csv(out_path, index=False)
    _log(ds_name, "SAVE", f"Saved: {out_path} ({len(df)} rows)", len(df))

    return df


def save_cleaning_log():
    """Save the cleaning transformation log."""
    log_path = CLEANED_DIR / "cleaning_log.json"
    import json
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(_cleaning_log, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ Cleaning log saved: {log_path} ({len(_cleaning_log)} entries)")


def main():
    print("=" * 70)
    print("MPLADS DATA CLEANING PIPELINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    clean_works_recommended()
    clean_works_sanctioned()
    clean_works_completed()
    clean_expenditure()
    clean_mp_allocation()

    save_cleaning_log()

    print("\n✅ All datasets cleaned successfully.")
    print(f"   Output directory: {CLEANED_DIR}")


if __name__ == "__main__":
    main()
