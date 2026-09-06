"""
Automated Evaluation and Unit Test Suite for the MPLADS AI Anomaly Platform.
Runs against the REAL eSAKSHI dataset loaded into SQLite by the ETL
(`python -m backend.app.etl`).

Requirements before running:
    MPLADS_DB=<path to built mplads.db> python -m pytest tests/test_platform.py -s
or simply build the default database first, then run pytest.
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
# Default DB built by the ETL
DEFAULT_DB = REPO_ROOT / "backend" / "data" / "mplads.db"


def db_available() -> bool:
    from app.db import get_db_path
    return get_db_path().exists()


# ---------------------------------------------------------------------------
# Engine unit tests (no database needed)
# ---------------------------------------------------------------------------

def test_rule_engine_fires_on_crafted_violations():
    from app.engine.rule_engine import RuleEngine
    engine = RuleEngine()

    # Financial control breach + impossible timeline + no payments
    bad = {
        "work_id": "T1", "sanction_amount": 100000.0, "total_disbursed": 150000.0,
        "vendor_count": 1, "payment_count": 2,
        "work_stage": "Work Completed", "work_status": "Completed",
        "recommendation_date": "2024-06-01", "sanction_date": "2024-01-01",
        "actual_end_date": "2024-02-01", "actual_amount": 120000.0,
        "attach_id": None, "file_status": None, "completion_rating": None,
    }
    signals = engine.evaluate_work(bad)
    types = {s.signal_type for s in signals}
    assert "RULE_DISBURSED_EXCEEDS_SANCTION" in types
    assert "RULE_TIMELINE_INCONSISTENT" in types
    assert "RULE_COMPLETED_NO_PAYMENTS" not in types  # has payments
    for s in signals:
        assert 0.0 <= s.score <= 100.0


def test_rule_engine_vendor_splitting_and_zombie():
    from app.engine.rule_engine import RuleEngine
    engine = RuleEngine()

    split = {
        "work_id": "T2", "sanction_amount": 500000.0, "total_disbursed": 500000.0,
        "vendor_count": 8, "payment_count": 9,
        "work_stage": "Sanction", "work_status": "Sanctioned",
        "recommendation_date": "2026-01-01", "sanction_date": "2026-02-01",
        "attach_id": "A1", "file_status": "True",
    }
    signals = engine.evaluate_work(split)
    assert any(s.signal_type == "RULE_VENDOR_SPLITTING" for s in signals)

    zombie = {
        "work_id": "T3", "sanction_amount": 100.0, "total_disbursed": 0.0,
        "vendor_count": 0, "payment_count": 0,
        "work_stage": "Sanction", "work_status": "Sanctioned",
        "recommendation_date": "2020-01-01", "sanction_date": "2020-02-01",
        "attach_id": "A2", "file_status": "True",
    }
    signals = engine.evaluate_work(zombie)
    assert any(s.signal_type == "RULE_ZOMBIE_WORK" for s in signals)


def test_nlp_duplicate_engine_exact_and_fuzzy():
    from app.engine.nlp_duplicate import NLPDuplicateEngine
    engine = NLPDuplicateEngine()

    works = [
        {"work_id": "A", "state": "S", "district": "D", "work_description": "Construction of community hall at ward 4 in village panchayat area", "sanction_amount": 100.0},
        {"work_id": "B", "state": "S", "district": "D", "work_description": "CONSTRUCTION OF COMMUNITY HALL AT WARD 4 IN VILLAGE PANCHAYAT AREA", "sanction_amount": 101.0},
        {"work_id": "C", "state": "S", "district": "D", "work_description": "Supply of solar street lights along the main road of the village", "sanction_amount": 50.0},
        {"work_id": "D", "state": "S", "district": "OTHER", "work_description": "Construction of community hall at ward 4 in village panchayat area", "sanction_amount": 100.0},
    ]
    dupes = engine.find_duplicate_pairs(works)
    # A and B are exact duplicates in the same district; D is in another district (no match)
    assert "A" in dupes or "B" in dupes
    assert dupes["A"][0] == "B"
    assert "D" not in dupes


def test_data_quality_engine_real_fields():
    from app.engine.data_quality import DataQualityEngine
    qe = DataQualityEngine()

    complete = {
        "work_description": "Construction of additional classrooms at government school",
        "mp_name": "Test MP", "district": "Nadia", "sanction_amount": 500000.0,
        "sanction_date": "2024-06-01", "recommendation_date": "2024-05-01",
        "actual_end_date": None, "work_stage": "Sanction",
    }
    score, status, warnings = qe.evaluate_work_quality(complete)
    assert score >= 85.0
    assert status == "Reliable"

    broken = {
        "work_description": "x", "mp_name": "", "district": "",
        "sanction_amount": 0.0, "sanction_date": None,
        "recommendation_date": None, "work_stage": "Work Completed",
        "actual_end_date": None,
    }
    score2, status2, _ = qe.evaluate_work_quality(broken)
    assert score2 < 60.0
    assert status2 == "Invalid"


# ---------------------------------------------------------------------------
# Database / ETL sanity tests (require built DB)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not db_available(), reason="Database not built — run `python -m backend.app.etl` first")
class TestRealDatabase:
    def get_conn(self):
        from app.db import get_connection
        return get_connection()

    def test_database_row_counts_real_scale(self):
        conn = self.get_conn()
        try:
            works = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
            payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
            mps = conn.execute("SELECT COUNT(*) FROM mp_allocations").fetchone()[0]
            vendors = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()[0]

            assert works > 120000, f"Expected 120K+ real works, got {works}"
            assert payments > 100000, f"Expected 100K+ payments, got {payments}"
            assert mps >= 770, f"Expected ~774 MPs (both houses), got {mps}"
            assert vendors > 20000
        finally:
            conn.close()

    def test_works_schema_and_joins(self):
        conn = self.get_conn()
        try:
            # District parsed from IDA_NAME
            row = conn.execute(
                "SELECT work_id, district, recommendation_date FROM works WHERE ida_name LIKE '%(%' AND district != '' LIMIT 1"
            ).fetchone()
            assert row is not None
            assert row["district"], "District should be parsed from IDA_NAME"
            # Dates ISO-parsed
            assert len(row["recommendation_date"] or "") == 10

            # Payment aggregation joined onto works
            row = conn.execute(
                "SELECT total_disbursed, payment_count FROM works WHERE payment_count > 0 LIMIT 1"
            ).fetchone()
            assert row is not None
            assert row["payment_count"] >= 1

            # Both houses present
            houses = {r[0] for r in conn.execute("SELECT DISTINCT house FROM works")}
            assert houses == {"Lok Sabha", "Rajya Sabha"}
        finally:
            conn.close()

    def test_analytics_outputs_present(self):
        conn = self.get_conn()
        try:
            alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            assert alerts > 1000, f"Expected thousands of alerts on real data, got {alerts}"

            # Risk levels bounded
            bad = conn.execute(
                "SELECT COUNT(*) FROM works WHERE risk_score < 0 OR risk_score > 100").fetchone()[0]
            assert bad == 0

            # Duplicate candidates exist (9K+ exact dupes are known in the real data)
            dupes = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE duplicate_candidate_id IS NOT NULL").fetchone()[0]
            assert dupes > 1000

            # Narrative explanations present on alerts
            empty_narrative = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE narrative_explanation IS NULL OR narrative_explanation = ''"
            ).fetchone()[0]
            assert empty_narrative == 0
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# API endpoint tests (require built DB)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not db_available(), reason="Database not built — run `python -m backend.app.etl` first")
class TestAPIEndpoints:
    @pytest.fixture(scope="class")
    def client(self, request):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        # class-scoped fixture stored on the class (avoids per-test instance attribute pitfall)
        cls = request.cls
        if not hasattr(cls, "_client"):
            cls._client = TestClient(app)
        return cls._client

    def test_health(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["monitored_works"] > 120000

    def test_overview_real_numbers(self, client):
        response = client.get("/api/v1/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["total_works"] > 120000
        assert data["total_expenditure_amount"] > 1e9   # ₹100 Cr+
        assert data["mps_count"] >= 770
        assert data["states_count"] >= 30

    def test_works_filters_and_pagination(self, client):
        response = client.get("/api/v1/works?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 120000
        assert len(data["works"]) <= 10
        first_wid = data["works"][0]["work_id"]

        response = client.get(f"/api/v1/works/{first_wid}")
        assert response.status_code == 200
        assert response.json()["work_id"] == first_wid

        response = client.get("/api/v1/works?state=Uttar%20Pradesh&limit=5")
        assert response.status_code == 200
        for w in response.json()["works"]:
            assert w["state"] == "Uttar Pradesh"

    def test_investigation_dossier_with_payments(self, client):
        # Find a work that has vendor payments
        r = client.get("/api/v1/works?limit=50")
        works = r.json()["works"]
        target = next((w for w in works if (w.get("payment_count") or 0) > 0), works[0])

        response = client.get(f"/api/v1/works/{target['work_id']}/investigation")
        assert response.status_code == 200
        data = response.json()
        assert "work" in data
        assert "payments" in data
        assert isinstance(data["payments"], list)

    def test_alerts_pagination_and_review_audit(self, client):
        response = client.get("/api/v1/alerts?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 1000
        assert len(data["alerts"]) <= 5

        alert = data["alerts"][0]
        review_payload = {
            "officer_name": "District Collector (Test)",
            "officer_role": "District Magistrate",
            "action": "Escalated for Physical Site Inspection",
            "remarks": "Ordered field physical measurement survey. (pytest)"
        }
        response = client.post(f"/api/v1/alerts/{alert['alert_id']}/review", json=review_payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        ts = response.json()["review"]["timestamp"]
        assert "T" in ts, "Timestamp should be a real ISO datetime now"

        # Audit log persisted
        response = client.get("/api/v1/audit-logs")
        assert response.status_code == 200
        logs = response.json()
        assert any(l["alert_id"] == alert["alert_id"] for l in logs)

    def test_mp_allocated_limits_both_houses(self, client):
        response = client.get("/api/v1/mps/allocated-limits")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 770
        houses = {m["house"] for m in data["mp_allocations"]}
        assert houses == {"Lok Sabha", "Rajya Sabha"}

        response = client.get("/api/v1/mps/allocated-limits?house=Rajya%20Sabha")
        for m in response.json()["mp_allocations"]:
            assert m["house"] == "Rajya Sabha"

    def test_agencies_and_vendors(self, client):
        response = client.get("/api/v1/agencies?limit=10")
        assert response.status_code == 200
        agencies = response.json()
        assert len(agencies) > 0
        assert all("agency_risk_score" in a for a in agencies)

        response = client.get("/api/v1/vendors/top?limit=10")
        assert response.status_code == 200
        vendors = response.json()
        assert len(vendors) > 0
        # Real data fact: the top vendor is paid across hundreds of works
        assert vendors[0]["work_count"] >= 100

    def test_copilot_query_real_context(self, client):
        response = client.post("/api/v1/copilot/query", json={"query": "Show high-risk works"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "128" in data["answer"] or "works" in data["answer"].lower()

        response = client.post("/api/v1/copilot/query", json={"query": "Vendor concentration analysis"})
        assert response.status_code == 200
        assert "vendor" in response.json()["answer"].lower()
