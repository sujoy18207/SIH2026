"""
ETL: Real eSAKSHI MPLADS CSVs -> SQLite database.

Parses the official scraped datasets in data/mplads_data/csv/ and builds
backend/data/mplads.db (path overridable via MPLADS_DB env var).

Run:  python -m backend.app.etl
"""

import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db import get_db_path, get_connection, init_schema

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_candidate_csv_dirs = [
    REPO_ROOT / "DATASET" / "mplads_data" / "csv",
    REPO_ROOT / "data" / "mplads_data" / "csv",
    REPO_ROOT / "mplads_data" / "csv",
]
if os.environ.get("MPLADS_DATA_DIR"):
    CSV_DIR = Path(os.environ["MPLADS_DATA_DIR"])
else:
    CSV_DIR = next((d for d in _candidate_csv_dirs if d.exists()), _candidate_csv_dirs[0])


HOUSE_MAP = {"1": "Rajya Sabha", "2": "Lok Sabha"}

TAB_RE = re.compile(r"[\t\r\n]+")


def clean_text(value: str) -> str:
    """Strip embedded tabs/newlines and excess whitespace from scraped fields."""
    if value is None:
        return ""
    return TAB_RE.sub(" ", str(value)).strip()


def parse_date(value: str):
    """Parse eSAKSHI date format '08-Jul-2024' -> ISO string, else None."""
    v = clean_text(value)
    if not v:
        return None
    try:
        return datetime.strptime(v, "%d-%b-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def parse_float(value):
    v = clean_text(value)
    if not v:
        return None
    try:
        f = float(v.replace(",", ""))
        return f
    except ValueError:
        return None


def parse_district(ida_name: str) -> str:
    """Extract district from IDA_NAME like 'JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA)'."""
    v = clean_text(ida_name)
    if "(" in v:
        v = v.split("(")[0]
    return v.strip()


def derive_work_status(stage: str, sanction_amount, actual_end_date) -> str:
    """Map eSAKSHI work stage onto the platform's work status vocabulary."""
    s = (stage or "").strip().lower()
    if "completed" in s:
        return "Completed"
    if "partially" in s:
        return "In Progress"
    if "sanction" == s or "vendor" in s or "inspection" in s or "time estimation" in s:
        # Past formal sanction: vendor selection / inspection / estimation phases
        return "Sanctioned" if (sanction_amount or 0) and sanction_amount > 0 else "In Progress"
    if "pending" in s:
        return "Pending Sanction"
    return "In Progress"


def days_between(d1, d2):
    if not d1 or not d2:
        return None
    try:
        return (datetime.strptime(d2, "%Y-%m-%d") - datetime.strptime(d1, "%Y-%m-%d")).days
    except ValueError:
        return None


def iter_csv(filename):
    path = CSV_DIR / filename
    if not path.exists():
        print(f"[WARN] Missing CSV: {path}")
        return
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            yield row


def load_works():
    """
    Build the unified works table from recommended + sanctioned + completed files.
    Sanctioned and completed rows enrich the recommended base via
    WORK_RECOMMENDATION_DTL_ID; any sanctioned/completed rows missing from the
    recommended file are still included.
    """
    works = {}

    for house, filename in (("Lok Sabha", "works_recommended_LokSabha_alltenures.csv"),
                            ("Rajya Sabha", "works_recommended_RajyaSabha_alltenures.csv")):
        for row in iter_csv(filename):
            wid = clean_text(row.get("WORK_RECOMMENDATION_DTL_ID"))
            if not wid or not wid.isdigit():
                continue
            sanction_amount = parse_float(row.get("SANCTION_AMOUNT"))
            rec = {
                "work_id": wid,
                "house": house,
                "state": clean_text(row.get("STATE_NAME")),
                "district": parse_district(row.get("IDA_NAME")),
                "constituency": clean_text(row.get("CONSTITUENCY")),
                "constituency_id": clean_text(row.get("CONSTITUENCY_ID")),
                "mp_name": clean_text(row.get("MP_NAME")),
                "tenure": clean_text(row.get("TENURE")),
                "work_category": clean_text(row.get("WORK_CATEGORY")),
                "activity_name": clean_text(row.get("ACTIVITY_NAME")),
                "work_description": clean_text(row.get("WORK_DESCRIPTION")),
                "ida_name": clean_text(row.get("IDA_NAME")),
                "letter_no": clean_text(row.get("LETTER_NO")),
                "file_status": clean_text(row.get("FILE_STATUS")) or None,
                "attach_id": clean_text(row.get("ATTACH_ID")) or None,
                "work_stage": clean_text(row.get("WORK_STAGE")),
                "recommendation_date": parse_date(row.get("RECOMMENDATION_DATE")),
                "sanction_date": parse_date(row.get("SANCTION_DATE")),
                "actual_end_date": None,
                "recommended_amount": parse_float(row.get("RECOMMENDED_AMOUNT")),
                "sanction_amount": sanction_amount,
                "actual_amount": None,
                "total_disbursed": 0.0,
                "payment_count": 0,
                "vendor_count": 0,
                "completion_rating": None,
                "days_to_sanction": None,
                "days_to_completion": None,
            }
            works[wid] = rec
        print(f"[ETL] recommended {house}: total works so far {len(works)}")

    # Enrich with sanctioned file (may contain rows absent from recommended)
    for house, filename in (("Lok Sabha", "works_sanctioned_LokSabha_alltenures.csv"),
                            ("Rajya Sabha", "works_sanctioned_RajyaSabha_alltenures.csv")):
        added = 0
        for row in iter_csv(filename):
            wid = clean_text(row.get("WORK_RECOMMENDATION_DTL_ID"))
            if not wid or not wid.isdigit():
                continue
            sanction_amount = parse_float(row.get("SANCTION_AMOUNT"))
            sanction_date = parse_date(row.get("SANCTION_DATE"))
            rec_date = parse_date(row.get("RECOMMENDATION_DATE"))
            if wid in works:
                w = works[wid]
                if sanction_amount:
                    w["sanction_amount"] = sanction_amount
                if sanction_date:
                    w["sanction_date"] = sanction_date
                stage = clean_text(row.get("WORK_STAGE"))
                if stage:
                    w["work_stage"] = stage
                if not w.get("mp_name"):
                    w["mp_name"] = clean_text(row.get("MP_NAME"))
            else:
                works[wid] = {
                    "work_id": wid,
                    "house": house,
                    "state": clean_text(row.get("STATE_NAME")),
                    "district": parse_district(row.get("IDA_NAME")),
                    "constituency": clean_text(row.get("CONSTITUENCY")),
                    "constituency_id": clean_text(row.get("CONSTITUENCY_ID")),
                    "mp_name": clean_text(row.get("MP_NAME")),
                    "tenure": clean_text(row.get("TENURE")),
                    "work_category": clean_text(row.get("WORK_CATEGORY")),
                    "activity_name": clean_text(row.get("ACTIVITY_NAME")),
                    "work_description": clean_text(row.get("WORK_DESCRIPTION")),
                    "ida_name": clean_text(row.get("IDA_NAME")),
                    "letter_no": clean_text(row.get("LETTER_NO")),
                    "file_status": clean_text(row.get("FILE_STATUS")) or None,
                    "attach_id": clean_text(row.get("ATTACH_ID")) or None,
                    "work_stage": clean_text(row.get("WORK_STAGE")),
                    "recommendation_date": rec_date,
                    "sanction_date": sanction_date,
                    "actual_end_date": None,
                    "recommended_amount": parse_float(row.get("SANCTION_AMOUNT")),
                    "sanction_amount": sanction_amount,
                    "actual_amount": None,
                    "total_disbursed": 0.0,
                    "payment_count": 0,
                    "vendor_count": 0,
                    "completion_rating": None,
                    "days_to_sanction": None,
                    "days_to_completion": None,
                }
                added += 1
        print(f"[ETL] sanctioned {house}: +{added} works not in recommended")

    # Enrich with completed file
    for filename in ("works_completed_LokSabha_alltenures.csv",
                     "works_completed_RajyaSabha_alltenures.csv"):
        matched = 0
        for row in iter_csv(filename):
            wid = clean_text(row.get("WORK_RECOMMENDATION_DTL_ID"))
            if not wid or not wid.isdigit():
                continue
            actual_amount = parse_float(row.get("ACTUAL_AMOUNT"))
            end_date = parse_date(row.get("ACTUAL_END_DATE"))
            rating = parse_float(row.get("AVERAGE_RATING"))
            if wid in works:
                w = works[wid]
                if actual_amount is not None:
                    w["actual_amount"] = actual_amount
                if end_date:
                    w["actual_end_date"] = end_date
                if rating is not None:
                    w["completion_rating"] = rating
                matched += 1
        print(f"[ETL] completed {filename.split('_')[2]}: matched {matched}")

    # Derive statuses and durations
    for w in works.values():
        w["work_status"] = derive_work_status(w["work_stage"], w["sanction_amount"], w["actual_end_date"])
        w["days_to_sanction"] = days_between(w["recommendation_date"], w["sanction_date"])
        w["days_to_completion"] = days_between(w["sanction_date"], w["actual_end_date"])
        if w["days_to_completion"] is None:
            w["days_to_completion"] = days_between(w["recommendation_date"], w["actual_end_date"])

    return works


def load_payments():
    """Load vendor payment rows; aggregate per work for enrichment."""
    payments = []
    for house, filename in (("Lok Sabha", "expenditure_LokSabha_alltenures.csv"),
                            ("Rajya Sabha", "expenditure_RajyaSabha_alltenures.csv")):
        for row in iter_csv(filename):
            wid = clean_text(row.get("WORK_RECOMMENDATION_DTL_ID"))
            amt = parse_float(row.get("FUND_DISBURSED_AMT")) or 0.0
            vendor = clean_text(row.get("VENDOR_NAME"))
            payments.append({
                "work_id": wid,
                "house": house,
                "state": clean_text(row.get("STATE_NAME")),
                "district": parse_district(row.get("IDA_NAME")),
                "constituency": clean_text(row.get("CONSTITUENCY")),
                "mp_name": clean_text(row.get("MP_NAME")),
                "tenure": clean_text(row.get("TENURE")),
                "activity_name": clean_text(row.get("ACTIVITY_NAME")),
                "ida_name": clean_text(row.get("IDA_NAME")),
                "ia_name": clean_text(row.get("IA_NAME")),
                "vendor_id": clean_text(row.get("VENDOR_ID")) or None,
                "vendor_name": vendor or None,
                "expenditure_date": parse_date(row.get("EXPENDITURE_DATE")),
                "fund_disbursed_amt": amt,
                "work_status": clean_text(row.get("WORK_STATUS")),
                "letter_no": clean_text(row.get("LETTER_NO")),
            })
        print(f"[ETL] payments {house}: {len(payments)} rows so far")

    # Per-work aggregates
    agg = {}
    for p in payments:
        wid = p["work_id"]
        if not wid:
            continue
        a = agg.setdefault(wid, {"total": 0.0, "count": 0, "vendors": set()})
        a["total"] += p["fund_disbursed_amt"] or 0.0
        a["count"] += 1
        if p["vendor_name"]:
            a["vendors"].add(p["vendor_name"])
    return payments, agg


def load_mp_allocations():
    records = []
    sr = 0
    for house, filename in (("Lok Sabha", "mp_allocation_LokSabha_alltenures.csv"),
                            ("Rajya Sabha", "mp_allocation_RajyaSabha_alltenures.csv")):
        for row in iter_csv(filename):
            mp = clean_text(row.get("MP_NAME"))
            state = clean_text(row.get("STATE_NAME"))
            if not mp or not state:
                continue
            sr += 1
            records.append({
                "sr_no": sr,
                "state": state,
                "house": house,
                "tenure": clean_text(row.get("TENURE")),
                "mp_name": mp,
                "constituency": clean_text(row.get("CONSTITUENCY")) or "General",
                "allocated_amount": parse_float(row.get("ALLOCATED_AMT")),
            })
    print(f"[ETL] mp_allocations: {len(records)} MPs (both houses)")
    return records


def build_vendor_profiles(payments):
    profiles = {}
    for p in payments:
        v = p["vendor_name"]
        if not v:
            continue
        prof = profiles.setdefault(v, {
            "vendor_name": v,
            "total_disbursed": 0.0,
            "works": set(),
            "districts": set(),
            "states": set(),
            "first": None,
            "last": None,
        })
        prof["total_disbursed"] += p["fund_disbursed_amt"] or 0.0
        if p["work_id"]:
            prof["works"].add(p["work_id"])
        if p["district"]:
            prof["districts"].add(p["district"])
        if p["state"]:
            prof["states"].add(p["state"])
        d = p["expenditure_date"]
        if d:
            if prof["first"] is None or d < prof["first"]:
                prof["first"] = d
            if prof["last"] is None or d > prof["last"]:
                prof["last"] = d
    out = []
    for v, prof in profiles.items():
        out.append({
            "vendor_name": v,
            "total_disbursed": round(prof["total_disbursed"], 2),
            "work_count": len(prof["works"]),
            "district_count": len(prof["districts"]),
            "state_count": len(prof["states"]),
            "first_payment_date": prof["first"],
            "last_payment_date": prof["last"],
        })
    print(f"[ETL] vendors: {len(out)} unique vendors profiled")
    return out


def run_etl():
    db_path = get_db_path()
    if db_path.exists():
        db_path.unlink()
        # Remove WAL sidecars too
        for suffix in ("-wal", "-shm"):
            side = Path(str(db_path) + suffix)
            if side.exists():
                side.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[ETL] Building database at {db_path}")
    conn = get_connection(db_path)
    init_schema(conn)

    # ---- works ----
    works = load_works()
    WORK_COLS = [
        "work_id", "house", "state", "district", "constituency", "constituency_id",
        "mp_name", "tenure", "work_category", "activity_name", "work_description",
        "ida_name", "letter_no", "file_status", "attach_id", "work_stage", "work_status",
        "recommendation_date", "sanction_date", "actual_end_date",
        "recommended_amount", "sanction_amount", "actual_amount",
        "total_disbursed", "payment_count", "vendor_count", "completion_rating",
        "days_to_sanction", "days_to_completion",
        "risk_score", "risk_level", "data_quality_score", "data_quality_status",
        "evidence_confidence_score", "evidence_confidence_level", "signals_count",
    ]
    work_rows = []
    for w in works.values():
        row = {c: w.get(c) for c in WORK_COLS}
        work_rows.append(row)

    # ---- payments + per-work aggregates ----
    payments, pay_agg = load_payments()
    for row in work_rows:
        a = pay_agg.get(row["work_id"])
        if a:
            row["total_disbursed"] = round(a["total"], 2)
            row["payment_count"] = a["count"]
            row["vendor_count"] = len(a["vendors"])

    placeholders = ",".join(["?"] * len(WORK_COLS))
    conn.executemany(
        f"INSERT OR REPLACE INTO works ({','.join(WORK_COLS)}) VALUES ({placeholders})",
        [tuple(r[c] for c in WORK_COLS) for r in work_rows],
    )
    print(f"[ETL] inserted {len(work_rows)} works")

    PAY_COLS = [
        "work_id", "house", "state", "district", "constituency", "mp_name", "tenure",
        "activity_name", "ida_name", "ia_name", "vendor_id", "vendor_name",
        "expenditure_date", "fund_disbursed_amt", "work_status", "letter_no",
    ]
    conn.executemany(
        f"INSERT INTO payments ({','.join(PAY_COLS)}) VALUES ({','.join(['?'] * len(PAY_COLS))})",
        [tuple(p.get(c) for c in PAY_COLS) for p in payments],
    )
    print(f"[ETL] inserted {len(payments)} payments")

    # ---- mp allocations ----
    allocs = load_mp_allocations()
    conn.executemany(
        "INSERT OR REPLACE INTO mp_allocations (sr_no, state, house, tenure, mp_name, constituency, allocated_amount) "
        "VALUES (?,?,?,?,?,?,?)",
        [(a["sr_no"], a["state"], a["house"], a["tenure"], a["mp_name"], a["constituency"], a["allocated_amount"])
         for a in allocs],
    )

    # ---- vendor profiles ----
    vendors = build_vendor_profiles(payments)
    conn.executemany(
        "INSERT OR REPLACE INTO vendors (vendor_name, total_disbursed, work_count, district_count, state_count, first_payment_date, last_payment_date) "
        "VALUES (?,?,?,?,?,?,?)",
        [(v["vendor_name"], v["total_disbursed"], v["work_count"], v["district_count"], v["state_count"],
          v["first_payment_date"], v["last_payment_date"]) for v in vendors],
    )

    # ---- indexes ----
    conn.executescript("""
    CREATE INDEX IF NOT EXISTS idx_works_state_district ON works(state, district);
    CREATE INDEX IF NOT EXISTS idx_works_level ON works(risk_level);
    CREATE INDEX IF NOT EXISTS idx_works_score ON works(risk_score);
    CREATE INDEX IF NOT EXISTS idx_works_mp ON works(mp_name);
    CREATE INDEX IF NOT EXISTS idx_works_stage ON works(work_stage);
    """)

    # ---- meta ----
    conn.executemany(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)",
        [
            ("etl_completed_at", datetime.now().isoformat()),
            ("works_count", str(len(work_rows))),
            ("payments_count", str(len(payments))),
            ("mps_count", str(len(allocs))),
            ("vendors_count", str(len(vendors))),
            ("data_source", "eSAKSHI official scraped CSVs (mplads.mospi.gov.in)"),
        ],
    )

    conn.commit()
    conn.close()
    print(f"[ETL] Data load complete: works={len(work_rows)} payments={len(payments)} mps={len(allocs)} vendors={len(vendors)}")

    # ---- run the multi-signal analytics pipeline over the real dataset ----
    print("[ETL] Running multi-signal analytics pipeline (rules + ML + NLP + agency)...")
    from app.engine.risk_engine import RiskEngine
    engine = RiskEngine()
    n_alerts, n_works = engine.run_full_analysis(db_path=db_path)
    print(f"[ETL] Analytics complete: {n_alerts} alerts over {n_works} works")
    print(f"[ETL] DONE. Database ready: {db_path}")


if __name__ == "__main__":
    run_etl()
