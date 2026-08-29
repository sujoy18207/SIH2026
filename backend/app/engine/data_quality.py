"""
Data Quality Engine & Evidence Confidence Engine for MPLADS
Evaluates raw work records for missing fields, coordinate validity, logical data flaws,
and computes Data Quality Score (0-100%) and Evidence Confidence Score (0-100%).
"""

from typing import Dict, Any, List, Tuple
from backend.app.schemas.mplads import AnomalySignal


class DataQualityEngine:
    """
    Evaluates input data completeness, coordinate validity, and field formatting.
    Produces Data Quality Score (0-100%) and Quality Level ('Reliable', 'Warning', 'Invalid').
    """

    def evaluate_work_quality(self, work: Dict[str, Any]) -> Tuple[float, str, List[str]]:
        quality_score = 100.0
        warnings: List[str] = []

        # Check 1: Valid GPS Coordinates
        lat = float(work.get("latitude", 0.0))
        lng = float(work.get("longitude", 0.0))
        if lat == 0.0 or lng == 0.0 or not (8.0 <= lat <= 37.0) or not (68.0 <= lng <= 97.0):
            quality_score -= 25.0
            warnings.append("Missing or invalid GPS spatial coordinates.")

        # Check 2: Mandatory Core Fields
        if not work.get("sanction_date"):
            quality_score -= 15.0
            warnings.append("Missing formal sanction date.")
        if not work.get("work_description") or len(work.get("work_description", "")) < 10:
            quality_score -= 15.0
            warnings.append("Incomplete work description.")
        if not work.get("implementing_agency_name"):
            quality_score -= 15.0
            warnings.append("Missing designated Implementing Agency.")

        # Check 3: Negative or Impossible Financial Values
        est = float(work.get("estimated_cost", 0.0))
        sanc = float(work.get("sanctioned_amount", 0.0))
        exp = float(work.get("expenditure", 0.0))
        if est <= 0 or sanc <= 0 or exp < 0:
            quality_score -= 20.0
            warnings.append("Negative or zero estimated/sanctioned cost.")

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
    Calculates Evidence Confidence Score (0-100%) - 'How reliable is the evidence backing this alert?'
    Factors in Data Quality Score, uploaded photo evidence, coordinate validity, and independent signal consensus.
    """

    def calculate_evidence_confidence(
        self,
        work: Dict[str, Any],
        data_quality_score: float,
        signals: List[AnomalySignal]
    ) -> Tuple[float, str]:
        confidence = 0.5 * data_quality_score

        # Factor 1: Photo Evidence Count
        photo_count = int(work.get("photo_count", 0))
        if photo_count >= 3:
            confidence += 20.0
        elif photo_count >= 1:
            confidence += 10.0

        # Factor 2: Signal Consensus (Multiple independent concurring signals increase evidence confidence)
        unique_signal_types = set(s.signal_type for s in signals)
        if len(unique_signal_types) >= 3:
            confidence += 20.0
        elif len(unique_signal_types) >= 2:
            confidence += 15.0
        elif len(unique_signal_types) == 1:
            confidence += 10.0

        # Factor 3: Financial Records Completeness
        if float(work.get("sanctioned_amount", 0.0)) > 0 and float(work.get("expenditure", 0.0)) >= 0:
            confidence += 10.0

        confidence = round(min(100.0, max(10.0, confidence)), 1)

        if confidence >= 80.0:
            level = "High Confidence"
        elif confidence >= 50.0:
            level = "Moderate Confidence"
        else:
            level = "Low Confidence"

        return confidence, level
