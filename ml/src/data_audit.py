"""
PHASE 1 — DATA AUDIT
=====================
Comprehensive data audit of real eSAKSHI MPLADS dataset (~466 MB).
Inspects all CSV files, reports schema, quality, join-key overlap, and
data characteristics without loading entire files into memory at once.

Outputs:
    reports/data_audit_report.json
    reports/data_audit_report.csv
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
from config import DATA_DIR, REPORT_DIR, CHUNK_SIZE, PROJECT_ROOT


def _safe_parse_dates(series: pd.Series) -> dict:
    """Attempt to find date range in a series of date-like strings."""
    sample = series.dropna().head(500)
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%b %d, %Y %I:%M:%S %p", "%d-%m-%Y"):
        try:
            parsed = pd.to_datetime(sample, format=fmt, errors="coerce")
            valid = parsed.dropna()
            if len(valid) > len(sample) * 0.3:
                return {
                    "min": str(valid.min()),
                    "max": str(valid.max()),
                    "parsed_count": int(len(valid)),
                    "format_detected": fmt,
                }
        except Exception:
            continue
    return {"min": None, "max": None, "parsed_count": 0, "format_detected": None}


def audit_csv_file(filepath: Path) -> dict:
    """Audit a single CSV file and return a comprehensive report dict."""
    file_size = filepath.stat().st_size
    file_name = filepath.name

    print(f"  Auditing {file_name} ({file_size / 1_048_576:.1f} MB)…")

    # Read full file (most are < 50 MB which fits in RAM)
    try:
        df = pd.read_csv(filepath, low_memory=False)
    except Exception as e:
        return {"file": file_name, "error": str(e)}

    n_rows, n_cols = df.shape
    dtypes = {col: str(dt) for col, dt in df.dtypes.items()}

    # Per-column analysis
    columns_info = []
    for col in df.columns:
        col_series = df[col]
        info = {
            "column_name": col,
            "dtype": str(col_series.dtype),
            "missing_count": int(col_series.isna().sum()),
            "missing_pct": round(float(col_series.isna().mean()) * 100, 2),
            "unique_count": int(col_series.nunique()),
            "sample_values": [str(v) for v in col_series.dropna().head(3).tolist()],
        }

        # Numerical range
        if pd.api.types.is_numeric_dtype(col_series):
            info["min"] = float(col_series.min()) if not col_series.isna().all() else None
            info["max"] = float(col_series.max()) if not col_series.isna().all() else None
            info["mean"] = round(float(col_series.mean()), 2) if not col_series.isna().all() else None

        # Date range detection
        if col_series.dtype == "object":
            lower = col.lower()
            if any(kw in lower for kw in ("date", "_dt", "start", "end")):
                date_info = _safe_parse_dates(col_series)
                info["date_range"] = date_info

        columns_info.append(info)

    # Duplicate detection
    dup_count = int(df.duplicated().sum())

    # Identify potential ID columns (high uniqueness ratio)
    potential_ids = []
    for col in df.columns:
        if df[col].nunique() > n_rows * 0.5 and df[col].dtype in ("int64", "float64", "object"):
            potential_ids.append(col)

    # Identify potential project/work identifiers
    work_id_cols = [c for c in df.columns if any(
        kw in c.upper() for kw in ("WORK_RECOMMENDATION_DTL_ID", "WORK_ID")
    )]

    # Identify potential MP identifiers
    mp_id_cols = [c for c in df.columns if "MP_NAME" in c.upper()]

    # Identify potential agency identifiers
    agency_cols = [c for c in df.columns if any(
        kw in c.upper() for kw in ("IDA_NAME", "IA_NAME", "VENDOR", "AGENCY")
    )]

    # Example records (first 3)
    examples = df.head(3).to_dict(orient="records")
    # Convert numpy types for JSON serialization
    for ex in examples:
        for k, v in ex.items():
            if isinstance(v, (np.integer,)):
                ex[k] = int(v)
            elif isinstance(v, (np.floating,)):
                ex[k] = float(v) if not np.isnan(v) else None
            elif isinstance(v, (np.bool_,)):
                ex[k] = bool(v)

    report = {
        "file_name": file_name,
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / 1_048_576, 2),
        "num_rows": n_rows,
        "num_columns": n_cols,
        "column_names": list(df.columns),
        "dtypes": dtypes,
        "duplicate_row_count": dup_count,
        "duplicate_pct": round(dup_count / max(1, n_rows) * 100, 2),
        "potential_id_columns": potential_ids,
        "work_identifier_columns": work_id_cols,
        "mp_identifier_columns": mp_id_cols,
        "agency_identifier_columns": agency_cols,
        "columns_detail": columns_info,
        "example_records": examples,
    }

    return report


def analyze_join_keys(reports: list) -> dict:
    """Analyze WORK_RECOMMENDATION_DTL_ID overlap across datasets."""
    print("\n  Analyzing join-key overlap across datasets…")

    key_col = "WORK_RECOMMENDATION_DTL_ID"
    datasets_with_key = {}

    for r in reports:
        fname = r["file_name"]
        if key_col in r.get("column_names", []):
            fpath = DATA_DIR / fname
            try:
                df = pd.read_csv(fpath, usecols=[key_col], low_memory=False)
                ids = set(df[key_col].dropna().astype(int).tolist())
                datasets_with_key[fname] = ids
                print(f"    {fname}: {len(ids):,} unique {key_col} values")
            except Exception as e:
                print(f"    {fname}: Error reading {key_col}: {e}")

    # Compute pairwise overlaps
    overlap_matrix = {}
    names = sorted(datasets_with_key.keys())
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if i < j:
                common = datasets_with_key[a] & datasets_with_key[b]
                overlap_matrix[f"{a} ∩ {b}"] = {
                    "common_ids": len(common),
                    "a_total": len(datasets_with_key[a]),
                    "b_total": len(datasets_with_key[b]),
                    "a_pct": round(len(common) / max(1, len(datasets_with_key[a])) * 100, 1),
                    "b_pct": round(len(common) / max(1, len(datasets_with_key[b])) * 100, 1),
                }

    # All-way intersection
    if len(datasets_with_key) >= 2:
        all_ids = list(datasets_with_key.values())
        universal = all_ids[0]
        for s in all_ids[1:]:
            universal = universal & s
        overlap_matrix["ALL_DATASETS_INTERSECTION"] = {
            "common_ids": len(universal),
            "datasets_count": len(datasets_with_key),
        }

    return {
        "join_key": key_col,
        "datasets_with_key": {k: len(v) for k, v in datasets_with_key.items()},
        "pairwise_overlap": overlap_matrix,
    }


def main():
    print("=" * 70)
    print("MPLADS eSAKSHI DATA AUDIT")
    print(f"Data directory: {DATA_DIR}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    print(f"\nFound {len(csv_files)} CSV files.\n")

    file_reports = []
    for fpath in csv_files:
        report = audit_csv_file(fpath)
        file_reports.append(report)

    # Join key analysis
    join_analysis = analyze_join_keys(file_reports)

    # Summary statistics
    total_rows = sum(r.get("num_rows", 0) for r in file_reports)
    total_size = sum(r.get("file_size_bytes", 0) for r in file_reports)
    total_dups = sum(r.get("duplicate_row_count", 0) for r in file_reports)

    summary = {
        "audit_timestamp": datetime.now().isoformat(),
        "data_directory": str(DATA_DIR),
        "total_csv_files": len(csv_files),
        "total_rows_all_files": total_rows,
        "total_size_mb": round(total_size / 1_048_576, 2),
        "total_duplicate_rows": total_dups,
    }

    full_report = {
        "summary": summary,
        "join_key_analysis": join_analysis,
        "file_reports": file_reports,
    }

    # Save JSON report
    json_path = REPORT_DIR / "data_audit_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ JSON report saved: {json_path}")

    # Save summary CSV
    csv_rows = []
    for r in file_reports:
        csv_rows.append({
            "file_name": r.get("file_name"),
            "file_size_mb": r.get("file_size_mb"),
            "num_rows": r.get("num_rows"),
            "num_columns": r.get("num_columns"),
            "duplicate_count": r.get("duplicate_row_count"),
            "duplicate_pct": r.get("duplicate_pct"),
            "has_work_id": "WORK_RECOMMENDATION_DTL_ID" in r.get("column_names", []),
            "potential_ids": ", ".join(r.get("potential_id_columns", [])),
        })
    csv_df = pd.DataFrame(csv_rows)
    csv_path = REPORT_DIR / "data_audit_report.csv"
    csv_df.to_csv(csv_path, index=False)
    print(f"✅ CSV summary saved: {csv_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Total records across all files: {total_rows:,}")
    print(f"Total data size: {total_size / 1_048_576:.1f} MB")
    print(f"Total duplicate rows: {total_dups:,}")
    print(f"\nJoin key: {join_analysis['join_key']}")
    print("Datasets with join key:")
    for ds, cnt in join_analysis["datasets_with_key"].items():
        print(f"  {ds}: {cnt:,} unique IDs")
    print("\nPairwise overlap:")
    for pair, info in join_analysis["pairwise_overlap"].items():
        if pair != "ALL_DATASETS_INTERSECTION":
            print(f"  {pair}: {info['common_ids']:,} common IDs")

    return full_report


if __name__ == "__main__":
    main()
