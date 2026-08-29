"""
Central Configurable Risk Policy Engine
Aggregates normalized signal scores (Rules, Isolation Forest ML, NLP Duplicate, GIS Proximity, Agency Risk),
computes Data Quality Score & Evidence Confidence Score, and triggers Priority Review Recommendations.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime

from backend.app.schemas.mplads import (
    ExplainableAlert, RiskScoreBreakdown, RiskLevel, AnomalySignal, AgencyProfile
)
from backend.app.engine.data_quality import DataQualityEngine, EvidenceConfidenceEngine
from backend.app.engine.rule_engine import RuleEngine
from backend.app.engine.ml_anomaly import MLAnomalyEngine
from backend.app.engine.nlp_duplicate import NLPDuplicateEngine
from backend.app.engine.gis_proximity import GISProximityEngine
from backend.app.engine.agency_risk import AgencyRiskProfiler
from backend.app.engine.explainability import generate_narrative_explanation


class RiskEngine:
    def __init__(self):
        self.quality_engine = DataQualityEngine()
        self.confidence_engine = EvidenceConfidenceEngine()
        self.rule_engine = RuleEngine()
        self.ml_engine = MLAnomalyEngine(contamination=0.05)
        self.nlp_engine = NLPDuplicateEngine()
        self.gis_engine = GISProximityEngine()
        self.agency_profiler = AgencyRiskProfiler()

    def calculate_delay_risk_score(self, work: Dict[str, Any], ag_profile: Any) -> float:
        """
        Calculates transparent Delay Risk Score based on elapsed duration, expected duration,
        physical progress %, financial progress %, and agency delay rate.
        """
        if work.get("work_status") == "Completed":
            return 0.0

        phys = float(work.get("physical_progress_pct", 0.0))
        fin = float(work.get("financial_progress_pct", 0.0))
        exp_comp_str = work.get("expected_completion_date")
        
        delay_score = 0.0
        if exp_comp_str:
            try:
                exp_date = datetime.strptime(exp_comp_str, "%Y-%m-%d")
                current_date = datetime(2026, 8, 29)
                if current_date > exp_date:
                    days_overdue = (current_date - exp_date).days
                    delay_score += min(60.0, days_overdue / 5.0)
            except Exception:
                pass

        if phys < 30.0 and fin > 50.0:
            delay_score += 25.0

        if ag_profile and ag_profile.agency_risk_score > 50.0:
            delay_score += 15.0

        return round(min(100.0, delay_score), 1)

    def analyze_all_works(self, works: List[Dict[str, Any]]) -> Tuple[List[ExplainableAlert], Dict[str, AgencyProfile], List[Dict[str, Any]]]:
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

        # 4. GIS Spatial Proximity
        gis_signals_map = self.gis_engine.evaluate_spatial_clusters(works)

        # Combine signals for agency profiling
        combined_signals_map: Dict[str, List[AnomalySignal]] = {}
        for w in works:
            wid = w["work_id"]
            sigs = list(rule_signals_map.get(wid, []))
            if wid in ml_results:
                sigs.extend(ml_results[wid][1])
            if wid in duplicates_map:
                sigs.append(duplicates_map[wid][3])
            if wid in gis_signals_map:
                sigs.extend(gis_signals_map[wid])
            combined_signals_map[wid] = sigs

        # 5. Agency Risk Profiler
        agency_profiles = self.agency_profiler.compute_agency_profiles(works, combined_signals_map)

        alerts: List[ExplainableAlert] = []
        analyzed_works: List[Dict[str, Any]] = []

        for w in works:
            wid = w["work_id"]
            rule_sigs = rule_signals_map.get(wid, [])
            ml_score, ml_sigs = ml_results.get(wid, (0.0, []))
            dup_info = duplicates_map.get(wid)
            gis_sigs = gis_signals_map.get(wid, [])

            # Data Quality Score
            dq_score, dq_status, dq_warnings = self.quality_engine.evaluate_work_quality(w)

            # Sub-Risk Category Scores
            fin_risk = max([s.score for s in rule_sigs if "PROGRESS" in s.signal_type or "EXP" in s.signal_type], default=0.0)
            cost_risk = max([s.score for s in rule_sigs if "EXP" in s.signal_type] + [ml_score if ml_score > 60 else 0.0], default=0.0)
            
            ag_profile = agency_profiles.get(w.get("implementing_agency_id"))
            agency_risk = ag_profile.agency_risk_score if ag_profile else 0.0
            
            delay_risk_score = self.calculate_delay_risk_score(w, ag_profile)
            dup_risk_score = dup_info[1] if dup_info else 0.0
            gis_risk = max([s.score for s in gis_sigs], default=0.0)
            compliance_risk = max([s.score for s in rule_sigs if "MISSING" in s.signal_type], default=0.0)

            # Configurable Policy Risk Engine Weight Formula
            rule_top_score = max([s.score for s in rule_sigs], default=0.0)
            
            composite_score = (
                (0.35 * rule_top_score) +
                (0.25 * ml_score) +
                (0.20 * dup_risk_score) +
                (0.10 * delay_risk_score) +
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
                timeline_risk=round(delay_risk_score, 1),
                duplicate_risk_score=round(dup_risk_score, 1),
                agency_risk=round(agency_risk, 1),
                compliance_risk=round(compliance_risk, 1)
            )

            all_signals = rule_sigs + ml_sigs + ( [dup_info[3]] if dup_info else [] ) + gis_sigs

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

            # Generate Alert if Risk Level is High or Critical, or signals exist
            if composite_score >= 45.0 or len(all_signals) > 0:
                narrative = generate_narrative_explanation(w, breakdown, all_signals, dup_info, dq_score, conf_score)
                
                alert = ExplainableAlert(
                    alert_id=f"ALT-{wid}",
                    work_id=wid,
                    work_title=w.get("work_description", "MPLADS Work"),
                    state=w.get("state", ""),
                    district=w.get("district", ""),
                    constituency=w.get("constituency", ""),
                    mp_name=w.get("mp_name", ""),
                    implementing_agency_name=w.get("implementing_agency_name", ""),
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
                    duplicate_risk_score=dup_info[1] if dup_info else None,
                    recommended_action="Priority Review Recommended"
                )
                alerts.append(alert)

        alerts.sort(key=lambda x: x.risk_score, reverse=True)
        return alerts, agency_profiles, analyzed_works
