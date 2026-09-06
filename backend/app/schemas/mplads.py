"""
Pydantic Data Schemas for the real eSAKSHI MPLADS Anomaly & Risk Platform.
Fields mirror the official scraped eSAKSHI dataset joined on
WORK_RECOMMENDATION_DTL_ID.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HouseType(str, Enum):
    LOK_SABHA = "Lok Sabha"
    RAJYA_SABHA = "Rajya Sabha"


class WorkStatus(str, Enum):
    PENDING_SANCTION = "Pending Sanction"
    SANCTIONED = "Sanctioned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ReviewAction(str, Enum):
    VERIFIED_VALID = "Verified Valid (No Fraud Found)"
    FALSE_POSITIVE = "Mark as False Positive Anomaly"
    ESCALATED = "Escalated for Physical Site Inspection"
    CLOSED = "Closed with Show-Cause Notice to Agency"


class WorkBase(BaseModel):
    """A work record from the real eSAKSHI dataset (works table row)."""
    work_id: str
    house: HouseType
    state: Optional[str] = None
    district: Optional[str] = None
    constituency: Optional[str] = None
    constituency_id: Optional[str] = None
    mp_name: Optional[str] = None
    tenure: Optional[str] = None
    work_category: Optional[str] = None
    activity_name: Optional[str] = None
    work_description: Optional[str] = None
    ida_name: Optional[str] = None
    letter_no: Optional[str] = None
    file_status: Optional[str] = None
    attach_id: Optional[str] = None
    work_stage: Optional[str] = None
    work_status: Optional[str] = None
    recommendation_date: Optional[str] = None
    sanction_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    recommended_amount: Optional[float] = None
    sanction_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    total_disbursed: Optional[float] = None
    payment_count: Optional[int] = 0
    vendor_count: Optional[int] = 0
    completion_rating: Optional[float] = None
    days_to_sanction: Optional[float] = None
    days_to_completion: Optional[float] = None
    # Analytics output
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    data_quality_score: Optional[float] = None
    data_quality_status: Optional[str] = None
    evidence_confidence_score: Optional[float] = None
    evidence_confidence_level: Optional[str] = None
    signals_count: Optional[int] = 0


class PaymentRecord(BaseModel):
    """A single vendor payment row from the expenditure dataset."""
    work_id: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_id: Optional[str] = None
    ia_name: Optional[str] = None
    expenditure_date: Optional[str] = None
    fund_disbursed_amt: float = 0.0
    work_status: Optional[str] = None


class AnomalySignal(BaseModel):
    signal_type: str
    severity: RiskLevel
    score: float  # 0 to 100
    title: str
    details: str
    evidence: Dict[str, Any]


class RiskScoreBreakdown(BaseModel):
    overall_risk_score: float  # 0 to 100
    risk_level: RiskLevel
    financial_risk: float          # disbursal vs sanction irregularities
    cost_risk: float               # cost deviation outliers
    timeline_risk: float           # delays, stage-stuck, impossible dates
    duplicate_risk_score: float    # NLP duplicate candidates
    agency_risk: float             # IDA/IA systemic patterns
    compliance_risk: float         # missing documents/attachments


class ExplainableAlert(BaseModel):
    alert_id: str
    work_id: str
    work_title: str
    state: str
    district: str
    constituency: str
    mp_name: str
    implementing_agency_name: str
    created_at: str
    risk_score: float
    risk_level: RiskLevel
    risk_breakdown: RiskScoreBreakdown
    data_quality_score: float
    data_quality_status: str
    evidence_confidence_score: float
    evidence_confidence_level: str
    triggering_signals: List[AnomalySignal]
    narrative_explanation: str
    duplicate_candidate_id: Optional[str] = None
    duplicate_risk_score: Optional[float] = None
    recommended_action: str = "Priority Review Recommended"
    is_reviewed: bool = False
    latest_review: Optional[Dict[str, Any]] = None


class OfficerReview(BaseModel):
    review_id: Optional[int] = None
    alert_id: str
    work_id: str
    officer_name: str
    officer_role: str
    action: ReviewAction
    remarks: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgencyProfile(BaseModel):
    agency_id: str
    agency_name: str
    district: str
    total_works: int
    completed_works: int
    delayed_works: int
    avg_completion_days: float
    avg_cost_deviation_pct: float
    total_expenditure: float
    anomaly_count: int
    agency_risk_score: float
    agency_risk_level: RiskLevel


class VendorProfile(BaseModel):
    """Vendor payment-concentration profile (contractor nexus signal)."""
    vendor_name: str
    total_disbursed: float
    work_count: int
    district_count: int
    state_count: int
    first_payment_date: Optional[str] = None
    last_payment_date: Optional[str] = None


class OverviewStats(BaseModel):
    total_works: int
    total_recommended_amount: float
    total_sanctioned_amount: float
    total_expenditure_amount: float
    completed_works_count: int
    in_progress_works_count: int
    pending_sanction_works_count: int = 0
    sanctioned_works_count: int = 0
    high_risk_works_count: int
    critical_risk_works_count: int
    medium_risk_works_count: int = 0
    low_risk_works_count: int = 0
    potential_cost_overrun_val: float
    duplicate_candidates_count: int
    avg_data_quality_score: float = 95.0
    states_count: int = 0
    districts_count: int = 0
    vendors_count: int = 0
    mps_count: int = 0
