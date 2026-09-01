"""
SQLITE & POSTGRESQL DATA LOADER
=================================
Loads cleaned CSVs and ML pipeline outputs into a zero-setup SQLite database
file (`ml/data/mplads.db`) or an optional PostgreSQL database.

Usage:
    # Default: Load into SQLite database (ml/data/mplads.db)
    python ml/src/db_loader.py

    # Optional: Load into custom database via SQLAlchemy URL
    python ml/src/db_loader.py --db-url postgresql://user:pass@localhost:5432/mplads_db
"""

import sys
import io
import sqlite3
import argparse
from pathlib import Path

# Set stdout/stderr encoding to UTF-8 for Windows console support
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import OUTPUT_DIR, CLEANED_DIR, REPORT_DIR

SQLITE_DB_PATH = OUTPUT_DIR / "mplads.db"
SQLITE_SCHEMA_PATH = SRC_DIR.parent / "schema_sqlite.sql"


def init_sqlite_schema(conn: sqlite3.Connection):
    """Apply DDL schema to SQLite database."""
    if SQLITE_SCHEMA_PATH.exists():
        with open(SQLITE_SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        print("  Applied SQLite schema successfully.")


def load_into_sqlite(db_path: Path = SQLITE_DB_PATH):
    """Load all pipeline CSV outputs into local SQLite database."""
    print(f"\n==================================================")
    print(f"LOADING PIPELINE DATA INTO SQLITE DATABASE")
    print(f"Database File: {db_path}")
    print(f"==================================================")

    conn = sqlite3.connect(db_path)
    init_sqlite_schema(conn)

    tables_map = [
        ("master_projects.csv", "projects", "Master Projects"),
        ("features.csv", "project_features", "Project Features"),
        ("rule_results.csv", "rule_results", "Rule Results"),
        ("ml_anomaly_scores.csv", "ml_results", "ML Anomaly Scores"),
        ("agency_risk.csv", "agencies", "Agency Risk Profiles"),
        ("risk_scores.csv", "risk_scores", "Composite Risk Scores"),
    ]

    for csv_file, table_name, label in tables_map:
        csv_path = OUTPUT_DIR / csv_file
        if csv_path.exists():
            print(f"  Loading {label} ({csv_file}) -> table '{table_name}'...")
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_sql(table_name, conn, if_exists="replace", index=False, chunksize=5000)
            print(f"  ✅ Loaded {len(df):,} rows into '{table_name}'.")
        else:
            print(f"  ⚠️ File not found: {csv_file}, skipping.")

    conn.close()
    print(f"\n✅ SQLite database populated successfully at: {db_path}")


def load_into_sqlalchemy(db_url: str):
    """Load data using SQLAlchemy (supports PostgreSQL, MySQL, etc.)."""
    try:
        from sqlalchemy import create_engine
    except ImportError:
        print("ERROR: sqlalchemy is required for custom DB URLs. Install via `pip install sqlalchemy`.")
        return

    print(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    engine = create_engine(db_url)

    tables_map = [
        ("master_projects.csv", "projects"),
        ("features.csv", "project_features"),
        ("rule_results.csv", "rule_results"),
        ("ml_anomaly_scores.csv", "ml_results"),
        ("agency_risk.csv", "agencies"),
        ("risk_scores.csv", "risk_scores"),
    ]

    for csv_file, table_name in tables_map:
        csv_path = OUTPUT_DIR / csv_file
        if csv_path.exists():
            print(f"  Loading {csv_file} -> table '{table_name}'...")
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_sql(table_name, engine, if_exists="replace", index=False, method="multi", chunksize=5000)
            print(f"  ✅ Loaded {len(df):,} rows.")

    print("\n✅ Database loading complete.")


def main():
    parser = argparse.ArgumentParser(description="Load MPLADS CSV data into SQLite or PostgreSQL")
    parser.add_argument("--db-url", type=str, help="SQLAlchemy DB connection URL (e.g. postgresql://user:pass@localhost:5432/db)")
    args = parser.parse_args()

    if args.db_url:
        load_into_sqlalchemy(args.db_url)
    else:
        load_into_sqlite()


if __name__ == "__main__":
    main()
