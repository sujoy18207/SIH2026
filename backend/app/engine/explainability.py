"""
Explainable Alert Evidence & Narrative Generator
Converts structured risk signals, Data Quality Scores, and Evidence Confidence Scores into natural, human-readable explanations.
"""

from typing import List, Dict, Any, Optional
from backend.app.schemas.mplads import RiskScoreBreakdown, AnomalySignal


def generate_narrative_explanation(
    work: Dict[str, Any],
    breakdown: RiskScoreBreakdown,
    signals: List[AnomalySignal],
    dup_info: Optional[tuple] = None,
    dq_score: float = 100.0,
    conf_score: float = 80.0
) -> str:
    wid = work.get("work_id", "")
    category = work.get("work_category", "")
    district = work.get("district", "")
    state = work.get("state", "")
    agency = work.get("implementing_agency_name", "")
    est_cost = float(work.get("estimated_cost", 0.0))
    fin_pct = float(work.get("financial_progress_pct", 0.0))
    phys_pct = float(work.get("physical_progress_pct", 0.0))

    parts = []
    parts.append(
        f"WORK {wid} ('{category}' in {district}, {state}) managed by {agency}\n"
        f"OVERALL RISK SCORE: {breakdown.overall_risk_score} / 100 ({breakdown.risk_level.value} Risk Level)\n"
        f"EVIDENCE CONFIDENCE SCORE: {conf_score:.0f}% | DATA QUALITY SCORE: {dq_score:.0f}%"
    )

    parts.append("\nKey Flagged Reasons & Signals:")
    
    # Financial progress vs physical progress gap
    if (fin_pct - phys_pct) > 25.0:
        parts.append(f"  + Financial progress ({fin_pct:.0f}%) is significantly ahead of verified physical completion ({phys_pct:.0f}%).")
    
    # Cost deviation
    if breakdown.cost_risk > 60.0:
        parts.append(f"  + Estimated cost (₹{est_cost:,.2f}) deviates substantially above comparable work median in district.")

    # Duplicate work
    if dup_info:
        cand_id, dup_risk, dist_km, _ = dup_info
        dist_m = dist_km * 1000.0
        parts.append(f"  + Potentially similar/duplicate work '{cand_id}' found located {dist_m:.0f}m away (Similarity Score: {dup_risk:.0f}%).")

    # Agency risk
    if breakdown.agency_risk > 50.0:
        parts.append(f"  + Executing agency ({agency}) exhibits an above-average historical project delay and anomaly frequency.")

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
