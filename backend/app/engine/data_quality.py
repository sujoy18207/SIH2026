"""
Data Quality Engine & Evidence Confidence Engine for real eSAKSHI records.
Evaluates completeness of description, dates, amounts, file attachments, and
payment records; computes Data Quality Score (0-100%) and Evidence Confidence
Score (0-100%).
"""

from typing import Dict, Any, List, Tuple
from app.schemas.mplads import AnomalySignal


class DataQualityEngine:
    """
    Evaluates real eSAKSHI work records for missing fields, unparseable values,
    and evidence gaps. Produces Data Quality Score (0-100%) and quality level
    ('Reliable', 'Warning', 'Invalid').
    """

    def evaluate_work_quality(self, work: Dict[str, Any]) -> Tuple[float, str, List[str]]:
        quality_score = 100.0
        warnings: List[str] = []

        # Check 1: Core identifying fields
        if not work.get("work_description") or len(str(work.get("work_description", ""))) < 15:
            quality_score -= 20.0
            warnings.append("Missing or too-short work description.")
        if not work.get("mp_name"):
            quality_score -= 10.0
            warnings.append("Missing MP name.")
        if not work.get("district"):
            quality_score -= 10.0
            warnings.append("District could not be determined from the district authority record.")

        # Check 2: Financial values sanity
        sanction = work.get("sanction_amount")
        if sanction is None or float(sanction) <= 0:
            quality_score -= 15.0
            warnings.append("Missing or non-positive sanctioned amount.")

        # Check 3: Date completeness relative to stage
        stage = (work.get("work_stage") or "").lower()
        if "pending" not in stage and not work.get("sanction_date"):
            quality_score -= 15.0
            warnings.append("No sanction date recorded for a work past recommendation stage.")
        if "completed" in stage and not work.get("actual_end_date"):
            quality_score -= 15.0
            warnings.append("Completed work without recorded completion date.")
        if not work.get("recommendation_date"):
            quality_score -= 15.0
            warnings.append("Missing recommendation date.")

        quality_score = max(0.0, quality_score)

        if quality_score >= 85.0:
            status = "Reliable"
        elif quality_score >= 60.0:
            status = "Warning"
        else:
            status = "Invalid"

        return round(quality_score, 1), status, warnings


class EvidenceConfidenceEngine:
    """
    Calculates Evidence Confidence Score (0-100%) — 'How reliable is the
    evidence backing this alert?' Factors in Data Quality Score, recorded
    vendor payment evidence, attached sanction files, and independent signal
    consensus.
    """

    def calculate_evidence_confidence(
        self,
        work: Dict[str, Any],
        data_quality_score: float,
        signals: List[AnomalySignal]
    ) -> Tuple[float, str]:
        confidence = 0.5 * data_quality_score

        # Factor 1: Recorded vendor payment trail
        payment_count = int(work.get("payment_count") or 0)
        if payment_count >= 3:
            confidence += 20.0
        elif payment_count >= 1:
            confidence += 10.0

        # Factor 2: Signal consensus (multiple independent concurring signals raise confidence)
        unique_signal_types = set(s.signal_type for s in signals)
        if len(unique_signal_types) >= 3:
            confidence += 20.0
        elif len(unique_signal_types) >= 2:
            confidence += 15.0
        elif len(unique_signal_types) == 1:
            confidence += 10.0

        # Factor 3: Attached sanction file evidence
        if work.get("attach_id"):
            confidence += 10.0

        confidence = round(min(100.0, max(10.0, confidence)), 1)

        if confidence >= 80.0:
            level = "High Confidence"
        elif confidence >= 50.0:
            level = "Moderate Confidence"
        else:
            level = "Low Confidence"

        return confidence, level
