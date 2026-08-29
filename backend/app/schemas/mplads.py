"""
Pydantic Data Schemas for MPLADS eSAKSHI Anomaly & Risk Platform
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HouseType(str, Enum):
    LOK_SABHA = "Lok Sabha"
    RAJYA_SABHA = "Rajya Sabha"


class WorkStatus(str, Enum):
    RECOMMENDED = "Recommended"
    SANCTIONED = "Sanctioned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    SUSPENDED = "Suspended"


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
    work_id: str
    state: str
    district: str
    constituency: str
    mp_name: str
    house: HouseType
    work_category: str
    work_description: str
    recommendation_date: str
    sanction_date: Optional[str] = None
    start_date: Optional[str] = None
    expected_completion_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    estimated_cost: float
    sanctioned_amount: float
    expenditure: float
    implementing_agency_id: str
    implementing_agency_name: str
    work_status: WorkStatus
    physical_progress_pct: float = Field(ge=0.0, le=100.0)
    financial_progress_pct: float = Field(ge=0.0, le=100.0)
    latitude: float
    longitude: float
    photo_count: int = 0
    documents_count: int = 0
    data_quality_score: float = 100.0
    data_quality_status: str = "Reliable"


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
    financial_risk: float
    cost_risk: float
    timeline_risk: float
    duplicate_risk_score: float
    agency_risk: float
    compliance_risk: float


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
    review_id: Optional[str] = None
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


class OverviewStats(BaseModel):
    total_works: int
    total_recommended_amount: float
    total_sanctioned_amount: float
    total_expenditure_amount: float
    completed_works_count: int
    in_progress_works_count: int
    high_risk_works_count: int
    critical_risk_works_count: int
    potential_cost_overrun_val: float
    duplicate_candidates_count: int
    avg_data_quality_score: float = 95.0
