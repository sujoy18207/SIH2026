"""
Statistical ML Anomaly Detection Engine
Isolation Forest over real eSAKSHI numerical features: sanction cost deviation vs
(activity x state) median, sanction delay, completion duration, disbursal ratio,
and vendor payment concentration.
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

    def extract_features(self, works: List[Dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(works)

        # Category-state median sanction cost for benchmarking
        grp_key = df["activity_name"].fillna("") + "|" + df["state"].fillna("")
        cat_medians = df.groupby(grp_key)["sanction_amount"].transform("median")
        df["cost_deviation_ratio"] = df["sanction_amount"] / np.maximum(cat_medians, 1.0)

        # Disbursal vs sanction ratio
        df["disbursal_ratio"] = df["total_disbursed"] / np.maximum(df["sanction_amount"], 1.0)

        # Actual-vs-sanction deviation on completed works
        df["actual_vs_sanction"] = np.where(
            df["actual_amount"].notna() & (df["sanction_amount"] > 0),
            df["actual_amount"] / df["sanction_amount"], 1.0
        )

        # Timeline features (clip absurd values to keep the matrix well-behaved)
        df["sanction_days"] = df["days_to_sanction"].fillna(-1.0).clip(-1.0, 2000.0)
        df["completion_days"] = df["days_to_completion"].fillna(-1.0).clip(-1.0, 4000.0)

        # Vendor payment concentration
        df["payment_count_feat"] = df["payment_count"].fillna(0).clip(0, 50.0)

        features = df[[
            "sanction_amount",
            "cost_deviation_ratio",
            "disbursal_ratio",
            "actual_vs_sanction",
            "sanction_days",
            "completion_days",
            "payment_count_feat",
        ]].fillna(0.0)

        return features

    def fit_predict(self, works: List[Dict[str, Any]]) -> Dict[str, Tuple[float, List[AnomalySignal]]]:
        if not works:
            return {}

        df_feat = self.extract_features(works)
        X_scaled = self.scaler.fit_transform(df_feat)

        self.iso_forest.fit(X_scaled)
        dec_scores = self.iso_forest.decision_function(X_scaled)

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
                disb_ratio = float(df_feat.iloc[idx]["disbursal_ratio"])

                signals.append(AnomalySignal(
                    signal_type="ML_STATISTICAL_OUTLIER",
                    severity=RiskLevel.CRITICAL if normalized_score >= 85.0 else RiskLevel.HIGH,
                    score=round(normalized_score, 1),
                    title="Statistical Anomaly Detected (Isolation Forest)",
                    details=(f"Multivariate feature vector (sanction cost {cost_dev:.2f}x the "
                             f"activity-state median, disbursal ratio {disb_ratio:.2f}) strays "
                             f"significantly from peer projects."),
                    evidence={
                        "ml_anomaly_score": round(normalized_score, 1),
                        "cost_deviation_ratio": round(cost_dev, 2),
                        "disbursal_ratio": round(disb_ratio, 2)
                    }
                ))

            results[work_id] = (normalized_score, signals)

        return results
