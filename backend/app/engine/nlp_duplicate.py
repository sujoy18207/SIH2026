"""
NLP Similarity & Duplicate Work Detection Engine
Calculates n-gram TF-IDF cosine similarity between work descriptions.
Combined with GIS spatial proximity distance to compute duplicate_risk_score.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.schemas.mplads import AnomalySignal, RiskLevel
from backend.app.engine.gis_proximity import calculate_haversine_distance


class NLPDuplicateEngine:
    def __init__(self, sim_threshold: float = 0.70, max_dist_km: float = 1.0):
        self.sim_threshold = sim_threshold
        self.max_dist_km = max_dist_km
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words="english")

    def find_duplicate_pairs(self, works: List[Dict[str, Any]]) -> Dict[str, Tuple[str, float, float, AnomalySignal]]:
        if len(works) < 2:
            return {}

        descriptions = [w.get("work_description", "") for w in works]
        tfidf_matrix = self.vectorizer.fit_transform(descriptions)
        cos_sim_matrix = cosine_similarity(tfidf_matrix)

        duplicates = {}

        n = len(works)
        for i in range(n):
            work_a = works[i]
            id_a = work_a["work_id"]
            lat_a, lng_a = float(work_a.get("latitude", 0)), float(work_a.get("longitude", 0))

            best_match_id = None
            best_sim = 0.0
            best_dist = 0.0

            for j in range(n):
                if i == j:
                    continue
                work_b = works[j]
                id_b = work_b["work_id"]

                if work_a.get("district") != work_b.get("district"):
                    continue

                sim = float(cos_sim_matrix[i, j])
                if sim >= self.sim_threshold:
                    lat_b, lng_b = float(work_b.get("latitude", 0)), float(work_b.get("longitude", 0))
                    dist_km = calculate_haversine_distance(lat_a, lng_a, lat_b, lng_b)

                    if dist_km <= self.max_dist_km:
                        if sim > best_sim:
                            best_sim = sim
                            best_match_id = id_b
                            best_dist = dist_km

            if best_match_id and best_sim >= self.sim_threshold:
                sim_pct = round(best_sim * 100.0, 1)
                dist_m = round(best_dist * 1000.0, 0)
                duplicate_risk_score = min(100.0, sim_pct * (1.0 if dist_m < 300 else 0.85))
                
                signal = AnomalySignal(
                    signal_type="NLP_DUPLICATE_WORK",
                    severity=RiskLevel.CRITICAL if sim_pct >= 85.0 and dist_m < 200 else RiskLevel.HIGH,
                    score=round(duplicate_risk_score, 1),
                    title="Potentially Similar/Duplicate Work — Verification Required",
                    details=f"High description similarity ({sim_pct}%) with nearby work {best_match_id} located {dist_m:.0f} meters away.",
                    evidence={
                        "candidate_work_id": best_match_id,
                        "similarity_pct": sim_pct,
                        "distance_meters": dist_m,
                        "duplicate_risk_score": round(duplicate_risk_score, 1),
                        "work_a_desc": work_a.get("work_description"),
                    }
                )
                duplicates[id_a] = (best_match_id, duplicate_risk_score, best_dist, signal)

        return duplicates
