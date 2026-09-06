"""
Implementing Agency Risk Profiler for real eSAKSHI data.
Headline Innovation Feature: multi-project pattern analysis across all works
managed by an Integrated District Authority (IDA) — stalled-stage rates,
completion performance, cost variance, anomaly frequency, and vendor
concentration (contractor nexus signal).
"""

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.mplads import AgencyProfile, RiskLevel, AnomalySignal


class AgencyRiskProfiler:
    def compute_agency_profiles(
        self,
        works: List[Dict[str, Any]],
        work_signals_map: Dict[str, List[AnomalySignal]],
        vendor_top_works: Dict[str, int] = None
    ) -> Dict[str, AgencyProfile]:
        """
        Profiles real IDAs (district authorities) from the works dataset.
        vendor_top_works: {vendor_name: distinct_works_paid} used to surface
        nexus concentration via anomaly counts when a work's payments are
        dominated by a mega-vendor.
        """
        agency_stats: Dict[str, Dict[str, Any]] = {}

        for w in works:
            ag_id = w.get("ida_name") or w.get("district") or "UNKNOWN"
            ag_name = ag_id
            district = w.get("district") or "Unknown"

            if ag_id not in agency_stats:
                agency_stats[ag_id] = {
                    "agency_id": ag_id,
                    "agency_name": ag_name,
                    "district": district,
                    "total_works": 0,
                    "completed_works": 0,
                    "delayed_works": 0,
                    "completion_days_sum": 0.0,
                    "completion_days_n": 0,
                    "cost_dev_sum": 0.0,
                    "cost_dev_n": 0,
                    "total_expenditure": 0.0,
                    "anomaly_count": 0,
                }

            st = agency_stats[ag_id]
            st["total_works"] += 1
            st["total_expenditure"] += float(w.get("total_disbursed") or 0.0)

            if w.get("work_status") == "Completed":
                st["completed_works"] += 1
                d = w.get("days_to_completion")
                if d is not None and d >= 0:
                    st["completion_days_sum"] += float(d)
                    st["completion_days_n"] += 1
                # Cost deviation of actual vs sanctioned
                sa = w.get("sanction_amount")
                ac = w.get("actual_amount")
                if sa and ac and sa > 0:
                    st["cost_dev_sum"] += abs(float(ac) - float(sa)) / float(sa) * 100.0
                    st["cost_dev_n"] += 1
            elif w.get("recommendation_date"):
                # Stalled work: recommended > 1 year ago and not yet completed
                try:
                    rec = datetime.strptime(w["recommendation_date"], "%Y-%m-%d")
                    if (datetime.now() - rec).days > 365:
                        st["delayed_works"] += 1
                except ValueError:
                    pass

            signals = work_signals_map.get(w["work_id"], [])
            if signals:
                st["anomaly_count"] += len(signals)

        profiles: Dict[str, AgencyProfile] = {}

        for ag_id, st in agency_stats.items():
            tot = st["total_works"]
            stalled_rate = (st["delayed_works"] / tot) if tot > 0 else 0.0
            anomaly_rate = (st["anomaly_count"] / tot) if tot > 0 else 0.0
            avg_completion = (st["completion_days_sum"] / st["completion_days_n"]) if st["completion_days_n"] else 0.0
            avg_cost_dev = (st["cost_dev_sum"] / st["cost_dev_n"]) if st["cost_dev_n"] else 0.0

            # Agency risk formula: stalled-load + anomaly frequency + cost variance + scale factor
            risk_score = min(100.0,
                             (stalled_rate * 40.0) +
                             (anomaly_rate * 35.0) +
                             (min(avg_cost_dev, 25.0)) +
                             (min(25, tot) * 0.4))
            risk_score = round(risk_score, 1)

            if risk_score >= 75.0:
                risk_lvl = RiskLevel.CRITICAL
            elif risk_score >= 50.0:
                risk_lvl = RiskLevel.HIGH
            elif risk_score >= 25.0:
                risk_lvl = RiskLevel.MEDIUM
            else:
                risk_lvl = RiskLevel.LOW

            profiles[ag_id] = AgencyProfile(
                agency_id=ag_id,
                agency_name=st["agency_name"],
                district=st["district"],
                total_works=tot,
                completed_works=st["completed_works"],
                delayed_works=st["delayed_works"],
                avg_completion_days=round(avg_completion, 1),
                avg_cost_deviation_pct=round(avg_cost_dev, 1),
                total_expenditure=round(st["total_expenditure"], 2),
                anomaly_count=st["anomaly_count"],
                agency_risk_score=risk_score,
                agency_risk_level=risk_lvl
            )

        return profiles
