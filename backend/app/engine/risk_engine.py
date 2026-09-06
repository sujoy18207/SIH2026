"""
Central Configurable Risk Policy Engine for real eSAKSHI data.
Aggregates normalized signal scores (Rules, Isolation Forest ML, NLP Duplicate,
Agency Risk), computes Data Quality Score & Evidence Confidence Score, and
persists explainable alerts to the SQLite alerts table.
"""

import json
from typing import List, Dict, Any, Tuple
from datetime import datetime

from app.schemas.mplads import (
    ExplainableAlert, RiskScoreBreakdown, RiskLevel, AnomalySignal, AgencyProfile
)
from app.engine.data_quality import DataQualityEngine, EvidenceConfidenceEngine
from app.engine.rule_engine import RuleEngine
from app.engine.ml_anomaly import MLAnomalyEngine
from app.engine.nlp_duplicate import NLPDuplicateEngine
from app.engine.agency_risk import AgencyRiskProfiler
from app.engine.explainability import generate_narrative_explanation
from app.db import get_connection


class RiskEngine:
    def __init__(self):
        self.quality_engine = DataQualityEngine()
        self.confidence_engine = EvidenceConfidenceEngine()
        self.rule_engine = RuleEngine()
        self.ml_engine = MLAnomalyEngine(contamination=0.05)
        self.nlp_engine = NLPDuplicateEngine()
        self.agency_profiler = AgencyRiskProfiler()

    def analyze_all_works(self, works: List[Dict[str, Any]]) -> Tuple[List[ExplainableAlert], Dict[str, AgencyProfile], List[Dict[str, Any]]]:
        """Run the full multi-signal pipeline over works (list of dicts from DB)."""
        if not works:
            return [], {}, []

        # 1. Rule Engine Signals
        rule_signals_map: Dict[str, List[AnomalySignal]] = {}
        for w in works:
            rule_signals_map[w["work_id"]] = self.rule_engine.evaluate_work(w)

        # 2. ML Anomaly Detection (Isolation Forest)
        ml_results = self.ml_engine.fit_predict(works)

        # 3. NLP Duplicate Work Detection
        duplicates_map = self.nlp_engine.find_duplicate_pairs(works)

        # Combine rule + ML signals for agency profiling
        combined_signals_map: Dict[str, List[AnomalySignal]] = {}
        for w in works:
            wid = w["work_id"]
            sigs = list(rule_signals_map.get(wid, []))
            if wid in ml_results:
                sigs.extend(ml_results[wid][1])
            if wid in duplicates_map:
                sigs.append(duplicates_map[wid][3])
            combined_signals_map[wid] = sigs

        # 4. Agency Risk Profiler (per IDA)
        agency_profiles = self.agency_profiler.compute_agency_profiles(works, combined_signals_map)

        alerts: List[ExplainableAlert] = []
        analyzed_works: List[Dict[str, Any]] = []

        for w in works:
            wid = w["work_id"]
            rule_sigs = rule_signals_map.get(wid, [])
            ml_score, ml_sigs = ml_results.get(wid, (0.0, []))
            dup_info = duplicates_map.get(wid)

            # Data Quality Score
            dq_score, dq_status, dq_warnings = self.quality_engine.evaluate_work_quality(w)

            # Sub-risk category scores
            fin_risk = max(
                [s.score for s in rule_sigs if "DISBURSED" in s.signal_type or "OVERRUN" in s.signal_type or "VENDOR" in s.signal_type] +
                [ml_score if ml_score > 60 else 0.0],
                default=0.0
            )
            cost_risk = max(
                [s.score for s in rule_sigs if "OVERRUN" in s.signal_type or "COMPLETION_OVERRUN" in s.signal_type],
                default=0.0
            )
            timeline_risk = max(
                [s.score for s in rule_sigs if "TIMELINE" in s.signal_type or "ZOMBIE" in s.signal_type],
                default=0.0
            )
            compliance_risk = max(
                [s.score for s in rule_sigs if "MISSING" in s.signal_type or "UNVERIFIED" in s.signal_type or "NO_PAYMENTS" in s.signal_type],
                default=0.0
            )

            ag_profile = agency_profiles.get(w.get("ida_name"))
            agency_risk = ag_profile.agency_risk_score if ag_profile else 0.0
            dup_risk_score = dup_info[1] if dup_info else 0.0

            # Configurable Policy Risk Engine Weight Formula
            rule_top_score = max([s.score for s in rule_sigs], default=0.0)

            composite_score = (
                (0.35 * rule_top_score) +
                (0.25 * ml_score) +
                (0.20 * dup_risk_score) +
                (0.10 * timeline_risk) +
                (0.10 * agency_risk)
            )
            composite_score = round(min(100.0, composite_score), 1)

            if composite_score >= 76.0:
                risk_lvl = RiskLevel.CRITICAL
            elif composite_score >= 51.0:
                risk_lvl = RiskLevel.HIGH
            elif composite_score >= 26.0:
                risk_lvl = RiskLevel.MEDIUM
            else:
                risk_lvl = RiskLevel.LOW

            breakdown = RiskScoreBreakdown(
                overall_risk_score=composite_score,
                risk_level=risk_lvl,
                financial_risk=round(fin_risk, 1),
                cost_risk=round(cost_risk, 1),
                timeline_risk=round(timeline_risk, 1),
                duplicate_risk_score=round(dup_risk_score, 1),
                agency_risk=round(agency_risk, 1),
                compliance_risk=round(compliance_risk, 1)
            )

            all_signals = rule_sigs + ml_sigs + ([dup_info[3]] if dup_info else [])

            # Evidence Confidence Score
            conf_score, conf_level = self.confidence_engine.calculate_evidence_confidence(w, dq_score, all_signals)

            # Store updated risk score & quality metrics in work record
            w_updated = dict(w)
            w_updated["risk_score"] = composite_score
            w_updated["risk_level"] = risk_lvl.value
            w_updated["data_quality_score"] = dq_score
            w_updated["data_quality_status"] = dq_status
            w_updated["evidence_confidence_score"] = conf_score
            w_updated["evidence_confidence_level"] = conf_level
            w_updated["signals_count"] = len(all_signals)
            analyzed_works.append(w_updated)

            # Generate Alert if meaningfully risky or any signals exist
            if composite_score >= 45.0 or len(all_signals) > 0:
                narrative = generate_narrative_explanation(w, breakdown, all_signals, dup_info, dq_score, conf_score)

                alert = ExplainableAlert(
                    alert_id=f"ALT-{wid}",
                    work_id=wid,
                    work_title=w.get("work_description", "MPLADS Work"),
                    state=w.get("state", "") or "",
                    district=w.get("district", "") or "",
                    constituency=w.get("constituency", "") or "",
                    mp_name=w.get("mp_name", "") or "",
                    implementing_agency_name=w.get("ida_name", "") or "",
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    risk_score=composite_score,
                    risk_level=risk_lvl,
                    risk_breakdown=breakdown,
                    data_quality_score=dq_score,
                    data_quality_status=dq_status,
                    evidence_confidence_score=conf_score,
                    evidence_confidence_level=conf_level,
                    triggering_signals=all_signals,
                    narrative_explanation=narrative,
                    duplicate_candidate_id=dup_info[0] if dup_info else None,
                    duplicate_risk_score=round(dup_info[1], 1) if dup_info else None,
                    recommended_action="Priority Review Recommended"
                )
                alerts.append(alert)

        alerts.sort(key=lambda x: x.risk_score, reverse=True)
        return alerts, agency_profiles, analyzed_works

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def persist_results(self, alerts: List[ExplainableAlert], agency_profiles: Dict[str, AgencyProfile], analyzed_works: List[Dict[str, Any]], db_path=None):
        """Write analysis results into the SQLite database (works + alerts + agencies)."""
        conn = get_connection(db_path)
        try:
            cur = conn.cursor()
            cur.execute("BEGIN")

            # Update works with scores
            for w in analyzed_works:
                cur.execute(
                    """UPDATE works SET risk_score=?, risk_level=?, data_quality_score=?,
                       data_quality_status=?, evidence_confidence_score=?,
                       evidence_confidence_level=?, signals_count=?
                       WHERE work_id=?""",
                    (
                        w["risk_score"], w["risk_level"], w["data_quality_score"],
                        w["data_quality_status"], w["evidence_confidence_score"],
                        w["evidence_confidence_level"], w["signals_count"], w["work_id"]
                    )
                )

            # Regenerate alerts table (analytics output is derived data)
            cur.execute("DELETE FROM alerts")
            for a in alerts:
                cur.execute(
                    """INSERT INTO alerts (alert_id, work_id, work_title, state, district,
                       constituency, mp_name, agency_name, created_at, risk_score, risk_level,
                       risk_breakdown, data_quality_score, data_quality_status,
                       evidence_confidence_score, evidence_confidence_level,
                       triggering_signals, narrative_explanation,
                       duplicate_candidate_id, duplicate_risk_score, recommended_action,
                       is_reviewed, latest_review)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        a.alert_id, a.work_id, a.work_title, a.state, a.district,
                        a.constituency, a.mp_name, a.implementing_agency_name, a.created_at,
                        a.risk_score, a.risk_level.value,
                        a.risk_breakdown.model_dump_json(),
                        a.data_quality_score, a.data_quality_status,
                        a.evidence_confidence_score, a.evidence_confidence_level,
                        json.dumps([s.model_dump() for s in a.triggering_signals]),
                        a.narrative_explanation,
                        a.duplicate_candidate_id, a.duplicate_risk_score, a.recommended_action,
                        0, None
                    )
                )

            # Regenerate agencies table
            cur.execute("DELETE FROM agencies")
            for ag in agency_profiles.values():
                cur.execute(
                    """INSERT INTO agencies (agency_id, agency_name, district, total_works,
                       completed_works, delayed_works, avg_days_to_completion,
                       avg_cost_deviation_pct, total_expenditure, anomaly_count,
                       agency_risk_score, agency_risk_level)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        ag.agency_id, ag.agency_name, ag.district, ag.total_works,
                        ag.completed_works, ag.delayed_works, ag.avg_completion_days,
                        ag.avg_cost_deviation_pct, ag.total_expenditure, ag.anomaly_count,
                        ag.agency_risk_score, ag.agency_risk_level.value
                    )
                )

            # Stamp analytics run
            cur.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)",
                ("last_analytics_run", datetime.now().isoformat())
            )

            conn.commit()
        finally:
            conn.close()

    def run_full_analysis(self, db_path=None, state: str = None):
        """Load works from the database, analyze, and persist. Used by ETL & API."""
        conn = get_connection(db_path)
        try:
            if state:
                rows = conn.execute("SELECT * FROM works WHERE state=?", (state,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM works").fetchall()
            works = [dict(r) for r in rows]
        finally:
            conn.close()

        alerts, agency_profiles, analyzed_works = self.analyze_all_works(works)
        self.persist_results(alerts, agency_profiles, analyzed_works, db_path=db_path)
        return len(alerts), len(analyzed_works)
