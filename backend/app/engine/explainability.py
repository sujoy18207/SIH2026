"""
Explainable Alert Evidence & Narrative Generator
Converts structured risk signals, Data Quality Scores, and Evidence Confidence
Scores from real eSAKSHI records into natural, human-readable explanations.
"""

from typing import List, Dict, Any, Optional
from app.schemas.mplads import RiskScoreBreakdown, AnomalySignal


def _fmt_inr(value) -> str:
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def generate_narrative_explanation(
    work: Dict[str, Any],
    breakdown: RiskScoreBreakdown,
    signals: List[AnomalySignal],
    dup_info: Optional[tuple] = None,
    dq_score: float = 100.0,
    conf_score: float = 80.0
) -> str:
    wid = work.get("work_id", "")
    category = work.get("activity_name") or work.get("work_category") or ""
    district = work.get("district", "")
    state = work.get("state", "")
    agency = work.get("ida_name", "")
    sanction = work.get("sanction_amount")
    disbursed = work.get("total_disbursed")
    actual = work.get("actual_amount")
    stage = work.get("work_stage", "")

    parts = []
    parts.append(
        f"WORK {wid} ('{category}' in {district}, {state}) executed via {agency}\n"
        f"CURRENT STAGE: {stage}\n"
        f"OVERALL RISK SCORE: {breakdown.overall_risk_score} / 100 ({breakdown.risk_level.value} Risk Level)\n"
        f"EVIDENCE CONFIDENCE SCORE: {conf_score:.0f}% | DATA QUALITY SCORE: {dq_score:.0f}%"
    )

    # Financial summary
    fin_line = f"  + Sanctioned: {_fmt_inr(sanction)}"
    if disbursed is not None:
        fin_line += f" | Vendor payments recorded: {_fmt_inr(disbursed)} across {work.get('payment_count') or 0} disbursement(s)"
    if actual is not None:
        fin_line += f" | Final completion amount: {_fmt_inr(actual)}"
    parts.append(fin_line)

    parts.append("\nKey Flagged Reasons & Signals:")

    # Disbursal overrun
    if breakdown.financial_risk > 60.0:
        parts.append(f"  + Recorded vendor disbursements deviate materially from the sanctioned amount (Financial Risk {breakdown.financial_risk:.0f}/100).")

    # Cost deviation
    if breakdown.cost_risk > 60.0:
        parts.append(f"  + Cost pattern (Sanctioned {_fmt_inr(sanction)}) deviates substantially above comparable works in the same activity and state.")

    # Duplicate work
    if dup_info:
        cand_id, dup_risk, amount_ratio, _ = dup_info
        ratio_txt = f", sanctioned at {amount_ratio:.0%} of its cost" if amount_ratio else ""
        parts.append(f"  + Potentially similar/duplicate work '{cand_id}' detected in the same district{ratio_txt} (Duplicate Risk Score: {dup_risk:.0f}%).")

    # Timeline anomalies
    if breakdown.timeline_risk > 50.0:
        parts.append(f"  + Timeline anomalies detected (Timeline Risk {breakdown.timeline_risk:.0f}/100): stalled stage, impossible date sequence, or extreme delay.")

    # Agency risk
    if breakdown.agency_risk > 50.0:
        parts.append(f"  + Executing district authority ({agency}) exhibits an above-average historical stalled-work and anomaly frequency.")

    # Detailed signals list
    if signals:
        parts.append("\nTriggering Evidence Signals:")
        for idx, sig in enumerate(signals, 1):
            parts.append(f"  {idx}. [{sig.title}] ({sig.severity.value} Severity): {sig.details}")

    parts.append(
        "\nRecommendation: Priority review recommended. This alert represents an automated decision-support indicator "
        "requiring official site verification and voucher audit before issuing administrative sanctions."
    )

    return "\n".join(parts)
