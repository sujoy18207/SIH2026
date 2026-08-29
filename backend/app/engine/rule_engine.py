"""
Rule-Based Compliance Engine for MPLADS
Evaluates deterministic financial, progress, timeline, and document compliance rules.
"""

from typing import List, Dict, Any
from datetime import datetime
from backend.app.schemas.mplads import AnomalySignal, RiskLevel


class RuleEngine:
    def __init__(self):
        # Configurable rules and thresholds
        self.FINANCIAL_GAP_THRESHOLD = 30.0  # Financial progress ahead of physical by > 30%
        self.EXTREME_DELAY_DAYS = 180         # Days past expected completion
        self.MIN_PHOTOS_REQUIRED = 2          # Photos required for works > 30% progress

    def evaluate_work(self, work: Dict[str, Any]) -> List[AnomalySignal]:
        signals: List[AnomalySignal] = []

        fin_pct = float(work.get("financial_progress_pct", 0.0))
        phys_pct = float(work.get("physical_progress_pct", 0.0))
        sanctioned = float(work.get("sanctioned_amount", 0.0))
        expenditure = float(work.get("expenditure", 0.0))
        photo_count = int(work.get("photo_count", 0))

        # RULE 1: Expenditure Exceeds Sanctioned Amount
        if expenditure > sanctioned and sanctioned > 0:
            overrun_pct = round(((expenditure - sanctioned) / sanctioned) * 100, 1)
            signals.append(AnomalySignal(
                signal_type="RULE_EXP_EXCEEDS_SANCTION",
                severity=RiskLevel.HIGH if overrun_pct < 20 else RiskLevel.CRITICAL,
                score=min(100.0, 50.0 + overrun_pct),
                title="Expenditure Exceeds Sanctioned Amount",
                details=f"Work expenditure (₹{expenditure:,.2f}) exceeds sanctioned amount (₹{sanctioned:,.2f}) by {overrun_pct}%.",
                evidence={
                    "sanctioned_amount": sanctioned,
                    "expenditure": expenditure,
                    "overrun_pct": overrun_pct
                }
            ))

        # RULE 2: Financial Progress Significantly Ahead of Physical Progress
        fin_phys_gap = fin_pct - phys_pct
        if fin_phys_gap >= self.FINANCIAL_GAP_THRESHOLD and work.get("work_status") == "In Progress":
            severity = RiskLevel.CRITICAL if fin_phys_gap >= 50.0 else RiskLevel.HIGH
            signals.append(AnomalySignal(
                signal_type="RULE_PROGRESS_MISMATCH",
                severity=severity,
                score=min(100.0, fin_phys_gap * 1.2),
                title="Financial Progress vs Physical Progress Mismatch",
                details=f"Financial progress ({fin_pct}%) is {fin_phys_gap:.1f}% ahead of physical progress ({phys_pct}%).",
                evidence={
                    "financial_progress_pct": fin_pct,
                    "physical_progress_pct": phys_pct,
                    "gap_pct": round(fin_phys_gap, 1)
                }
            ))

        # RULE 3: Timeline Inconsistency (Dates out of logical sequence)
        rec_date_str = work.get("recommendation_date")
        sanc_date_str = work.get("sanction_date")
        act_comp_date_str = work.get("actual_completion_date")

        try:
            if rec_date_str and sanc_date_str:
                r_date = datetime.strptime(rec_date_str, "%Y-%m-%d")
                s_date = datetime.strptime(sanc_date_str, "%Y-%m-%d")
                if s_date < r_date:
                    signals.append(AnomalySignal(
                        signal_type="RULE_TIMELINE_INCONSISTENT",
                        severity=RiskLevel.HIGH,
                        score=80.0,
                        title="Sanction Date Before Recommendation Date",
                        details=f"Sanction date ({sanc_date_str}) precedes recommendation date ({rec_date_str}).",
                        evidence={"recommendation_date": rec_date_str, "sanction_date": sanc_date_str}
                    ))
            
            if sanc_date_str and act_comp_date_str:
                s_date = datetime.strptime(sanc_date_str, "%Y-%m-%d")
                c_date = datetime.strptime(act_comp_date_str, "%Y-%m-%d")
                if c_date < s_date:
                    signals.append(AnomalySignal(
                        signal_type="RULE_TIMELINE_INCONSISTENT",
                        severity=RiskLevel.CRITICAL,
                        score=95.0,
                        title="Completion Date Before Sanction Date",
                        details=f"Actual completion date ({act_comp_date_str}) precedes sanction date ({sanc_date_str}).",
                        evidence={"sanction_date": sanc_date_str, "actual_completion_date": act_comp_date_str}
                    ))
        except Exception:
            pass

        # RULE 4: Severe Timeline Delay with Low Physical Progress
        exp_comp_str = work.get("expected_completion_date")
        if exp_comp_str and work.get("work_status") == "In Progress":
            try:
                exp_date = datetime.strptime(exp_comp_str, "%Y-%m-%d")
                # Using 2026-08-29 as reference current date
                current_date = datetime(2026, 8, 29)
                if current_date > exp_date:
                    delay_days = (current_date - exp_date).days
                    if delay_days >= self.EXTREME_DELAY_DAYS and phys_pct < 50.0:
                        signals.append(AnomalySignal(
                            signal_type="RULE_EXCESSIVE_DELAY",
                            severity=RiskLevel.HIGH if delay_days < 365 else RiskLevel.CRITICAL,
                            score=min(100.0, 50.0 + (delay_days / 10.0)),
                            title="Severe Project Timeline Delay",
                            details=f"Project is {delay_days} days overdue with only {phys_pct}% physical progress achieved.",
                            evidence={
                                "expected_completion_date": exp_comp_str,
                                "delay_days": delay_days,
                                "physical_progress_pct": phys_pct
                            }
                        ))
            except Exception:
                pass

        # RULE 5: Missing Geo-Tagged Photographs for Advanced Financial Disbursement
        if fin_pct >= 40.0 and photo_count < self.MIN_PHOTOS_REQUIRED:
            signals.append(AnomalySignal(
                signal_type="RULE_MISSING_EVIDENCE",
                severity=RiskLevel.MEDIUM,
                score=65.0,
                title="Insufficient Geo-tagged Photographs for Released Funds",
                details=f"Financial progress reached {fin_pct}%, but only {photo_count} geo-tagged photos uploaded (minimum {self.MIN_PHOTOS_REQUIRED} required).",
                evidence={"financial_progress_pct": fin_pct, "photo_count": photo_count}
            ))

        return signals
