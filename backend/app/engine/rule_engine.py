"""
Rule-Based Compliance Engine for real eSAKSHI MPLADS data.
Evaluates deterministic financial, timeline, stage-progression and
document-evidence compliance rules on real scraped records.
"""

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.mplads import AnomalySignal, RiskLevel


class RuleEngine:
    def __init__(self):
        # Configurable rules and thresholds
        self.OVERRUN_PCT_THRESHOLD = 10.0     # Disbursed exceeds sanction by >10%
        self.ZOMBIE_DAYS = 730                 # Stage-stuck for >2 years without completion
        self.MAX_VENDORS_PER_WORK = 4          # >4 distinct vendors on one sanction
        self.ADVANCED_STAGES = (               # Stages where file evidence is mandatory
            "Physical Inspection",
            "Work partially Completed",
            "Work Completed",
        )

    def evaluate_work(self, work: Dict[str, Any]) -> List[AnomalySignal]:
        signals: List[AnomalySignal] = []

        sanction = float(work.get("sanction_amount") or 0.0)
        disbursed = float(work.get("total_disbursed") or 0.0)
        actual = work.get("actual_amount")
        actual_amt = float(actual) if actual is not None else None

        rec_date = work.get("recommendation_date")
        sanc_date = work.get("sanction_date")
        end_date = work.get("actual_end_date")
        stage = (work.get("work_stage") or "").strip()
        status = (work.get("work_status") or "").strip()

        # RULE 1a: Total Vendor Disbursements Exceed Sanctioned Amount
        # (eSAKSHI normally caps disbursements at the sanctioned amount — any
        # breach is a hard financial control failure)
        if sanction > 0 and disbursed > sanction * (1.0 + self.OVERRUN_PCT_THRESHOLD / 100.0):
            overrun_pct = round(((disbursed - sanction) / sanction) * 100.0, 1)
            signals.append(AnomalySignal(
                signal_type="RULE_DISBURSED_EXCEEDS_SANCTION",
                severity=RiskLevel.HIGH if overrun_pct < 25 else RiskLevel.CRITICAL,
                score=min(100.0, 50.0 + overrun_pct),
                title="Vendor Disbursements Exceed Sanctioned Amount",
                details=(f"Cumulative vendor payments (₹{disbursed:,.2f}) exceed the sanctioned "
                         f"amount (₹{sanction:,.2f}) by {overrun_pct}%."),
                evidence={
                    "sanction_amount": sanction,
                    "total_disbursed": disbursed,
                    "payment_count": work.get("payment_count", 0),
                    "overrun_pct": overrun_pct
                }
            ))

        # RULE 1b: Excessive Multi-Vendor Splitting of a Single Sanction
        # (many distinct vendors paid against one work suggests cost-splitting
        # to dodge procurement thresholds)
        vendor_count = int(work.get("vendor_count") or 0)
        if vendor_count >= self.MAX_VENDORS_PER_WORK:
            signals.append(AnomalySignal(
                signal_type="RULE_VENDOR_SPLITTING",
                severity=RiskLevel.HIGH if vendor_count < 10 else RiskLevel.CRITICAL,
                score=min(100.0, 40.0 + vendor_count * 4.0),
                title="Excessive Multi-Vendor Splitting of Single Sanction",
                details=(f"{vendor_count} distinct vendors were paid against a single sanctioned work "
                         f"(₹{sanction:,.2f}) — possible splitting to circumvent procurement thresholds."),
                evidence={
                    "vendor_count": vendor_count,
                    "payment_count": work.get("payment_count", 0),
                    "sanction_amount": sanction
                }
            ))

        # RULE 2: Actual Completion Cost Exceeds Sanctioned Amount
        if actual_amt is not None and sanction > 0 and actual_amt > sanction * 1.10:
            overrun_pct = round(((actual_amt - sanction) / sanction) * 100.0, 1)
            signals.append(AnomalySignal(
                signal_type="RULE_COMPLETION_OVERRUN",
                severity=RiskLevel.HIGH if overrun_pct < 40 else RiskLevel.CRITICAL,
                score=min(100.0, 45.0 + overrun_pct),
                title="Final Completion Amount Exceeds Sanction by Over 10%",
                details=(f"Completed work cost (₹{actual_amt:,.2f}) exceeds the sanctioned amount "
                         f"(₹{sanction:,.2f}) by {overrun_pct}%."),
                evidence={
                    "sanction_amount": sanction,
                    "actual_amount": actual_amt,
                    "overrun_pct": overrun_pct
                }
            ))

        # RULE 3: Sanction Date On or Before Recommendation Date (impossible timeline)
        if rec_date and sanc_date:
            try:
                r = datetime.strptime(rec_date, "%Y-%m-%d")
                s = datetime.strptime(sanc_date, "%Y-%m-%d")
                if s <= r:
                    signals.append(AnomalySignal(
                        signal_type="RULE_TIMELINE_INCONSISTENT",
                        severity=RiskLevel.HIGH,
                        score=80.0,
                        title="Sanction Date On/Before Recommendation Date",
                        details=(f"Sanction date ({sanc_date}) is on or before the recommendation "
                                 f"date ({rec_date}) — administrative sequence violation."),
                        evidence={"recommendation_date": rec_date, "sanction_date": sanc_date}
                    ))
            except ValueError:
                pass

        # RULE 4: Completion Date Precedes Sanction Date (impossible timeline)
        if sanc_date and end_date:
            try:
                s = datetime.strptime(sanc_date, "%Y-%m-%d")
                c = datetime.strptime(end_date, "%Y-%m-%d")
                if c < s:
                    signals.append(AnomalySignal(
                        signal_type="RULE_TIMELINE_INCONSISTENT",
                        severity=RiskLevel.CRITICAL,
                        score=95.0,
                        title="Completion Date Precedes Sanction Date",
                        details=(f"Actual completion date ({end_date}) precedes the sanction date "
                                 f"({sanc_date}) — chronologically impossible record."),
                        evidence={"sanction_date": sanc_date, "actual_end_date": end_date}
                    ))
            except ValueError:
                pass

        # RULE 5: Zombie Work — Stage-Stuck for Over 2 Years Without Completion
        if status != "Completed" and rec_date:
            try:
                r = datetime.strptime(rec_date, "%Y-%m-%d")
                age_days = (datetime.now() - r).days
                if age_days >= self.ZOMBIE_DAYS:
                    signals.append(AnomalySignal(
                        signal_type="RULE_ZOMBIE_WORK",
                        severity=RiskLevel.HIGH if age_days < 1460 else RiskLevel.CRITICAL,
                        score=min(100.0, 45.0 + (age_days - self.ZOMBIE_DAYS) / 20.0),
                        title="Long-Stalled Work (Zombie Project)",
                        details=(f"Work has remained at stage '{stage or 'Unknown'}' for "
                                 f"{age_days} days ({age_days / 365.0:.1f} years) since recommendation "
                                 f"without completion."),
                        evidence={
                            "recommendation_date": rec_date,
                            "age_days": age_days,
                            "work_stage": stage,
                            "sanction_amount": sanction,
                            "total_disbursed": disbursed
                        }
                    ))
            except ValueError:
                pass

        # RULE 6: Completed Work With Zero Recorded Vendor Payments
        if status == "Completed" and (work.get("payment_count") or 0) == 0:
            amt = actual_amt if actual_amt is not None else sanction
            signals.append(AnomalySignal(
                signal_type="RULE_COMPLETED_NO_PAYMENTS",
                severity=RiskLevel.HIGH,
                score=70.0,
                title="Completed Work With No Vendor Payment Records",
                details=(f"Work is marked completed (₹{amt or 0:,.2f}) but the eSAKSHI expenditure "
                         f"ledger contains zero vendor payment rows against it."),
                evidence={
                    "actual_amount": amt,
                    "payment_count": 0,
                    "completion_date": end_date
                }
            ))

        # RULE 7: Advanced Stage Without Mandatory File Evidence
        if stage in self.ADVANCED_STAGES and not work.get("attach_id") and not work.get("file_status"):
            signals.append(AnomalySignal(
                signal_type="RULE_MISSING_EVIDENCE",
                severity=RiskLevel.MEDIUM,
                score=60.0,
                title="Advanced Stage Without Sanction File Attachment",
                details=(f"Work has reached '{stage}' but has no attached sanction file "
                         f"(ATTACH_ID and FILE_STATUS empty) in the record."),
                evidence={"work_stage": stage, "attach_id": None, "file_status": None}
            ))

        # RULE 8: Completed Work With Zero Rating and Zero Utilization Evidence
        if status == "Completed":
            rating = work.get("completion_rating")
            if (rating is None or float(rating) == 0.0) and (work.get("payment_count") or 0) > 0:
                signals.append(AnomalySignal(
                    signal_type="RULE_UNVERIFIED_COMPLETION",
                    severity=RiskLevel.MEDIUM,
                    score=55.0,
                    title="Completion Not Verified (No Rating Recorded)",
                    details=("Work is marked completed with vendor payments recorded, but carries "
                             "no field completion rating — physical verification absent."),
                    evidence={
                        "completion_rating": rating,
                        "payment_count": work.get("payment_count", 0)
                    }
                ))

        return signals
