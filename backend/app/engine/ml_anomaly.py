"""
Statistical ML Anomaly Detection Engine
Uses Isolation Forest on extracted numerical feature matrices (cost deviation ratio, spending velocity, unit cost).
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.schemas.mplads import AnomalySignal, RiskLevel


class MLAnomalyEngine:
    def __init__(self, contamination: float = 0.05):
        # 5% contamination rate matching realistic anomaly distribution
        self.contamination = contamination
        self.iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def extract_features(self, works: List[Dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(works)
        
        # Calculate category median cost for benchmarking
        cat_medians = df.groupby("work_category")["estimated_cost"].transform("median")
        
        df["cost_deviation_ratio"] = df["estimated_cost"] / np.maximum(cat_medians, 1.0)
        df["fin_phys_gap"] = df["financial_progress_pct"] - df["physical_progress_pct"]
        df["cost_per_photo"] = df["expenditure"] / np.maximum(1.0, df["photo_count"])
        df["cost_per_phys_unit"] = df["expenditure"] / np.maximum(1.0, df["physical_progress_pct"])
        
        features = df[[
            "estimated_cost",
            "cost_deviation_ratio",
            "fin_phys_gap",
            "cost_per_photo",
            "cost_per_phys_unit"
        ]].fillna(0.0)

        return features

    def fit_predict(self, works: List[Dict[str, Any]]) -> Dict[str, Tuple[float, List[AnomalySignal]]]:
        if not works:
            return {}

        df_feat = self.extract_features(works)
        X_scaled = self.scaler.fit_transform(df_feat)
        
        self.iso_forest.fit(X_scaled)
        dec_scores = self.iso_forest.decision_function(X_scaled)
        self.is_fitted = True

        raw_min = np.min(dec_scores)
        raw_max = np.max(dec_scores)
        
        results = {}
        for idx, work in enumerate(works):
            work_id = work["work_id"]
            raw_score = dec_scores[idx]
            
            # Map decision score to 0-100 anomaly score
            if raw_max > raw_min:
                normalized_score = 100.0 * (1.0 - (raw_score - raw_min) / (raw_max - raw_min))
            else:
                normalized_score = 50.0

            normalized_score = float(np.clip(normalized_score, 0.0, 100.0))
            
            signals = []
            if normalized_score >= 70.0:
                cost_dev = float(df_feat.iloc[idx]["cost_deviation_ratio"])
                fin_gap = float(df_feat.iloc[idx]["fin_phys_gap"])
                
                signals.append(AnomalySignal(
                    signal_type="ML_STATISTICAL_OUTLIER",
                    severity=RiskLevel.CRITICAL if normalized_score >= 85.0 else RiskLevel.HIGH,
                    score=round(normalized_score, 1),
                    title="Statistical Anomaly Detected (Isolation Forest)",
                    details=f"Multivariate numerical feature vector (cost ratio: {cost_dev:.2f}x median, gap: {fin_gap:.1f}%) strays significantly from peer projects.",
                    evidence={
                        "ml_anomaly_score": round(normalized_score, 1),
                        "cost_deviation_ratio": round(cost_dev, 2),
                        "financial_physical_gap": round(fin_gap, 1)
                    }
                ))

            results[work_id] = (normalized_score, signals)

        return results
