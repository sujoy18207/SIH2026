"""
GIS Spatial Proximity & Clustering Engine
Computes Haversine distances between asset GPS coordinates to detect geographic overlap.
"""

import math
from typing import List, Dict, Any, Tuple
from backend.app.schemas.mplads import AnomalySignal, RiskLevel


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great circle distance between two points on the earth in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


class GISProximityEngine:
    def __init__(self, proximity_threshold_km: float = 0.3):
        self.proximity_threshold_km = proximity_threshold_km

    def evaluate_spatial_clusters(self, works: List[Dict[str, Any]]) -> Dict[str, List[AnomalySignal]]:
        """
        Finds works located unusually close to other works of identical category.
        """
        results: Dict[str, List[AnomalySignal]] = {}

        n = len(works)
        for i in range(n):
            w_a = works[i]
            id_a = w_a["work_id"]
            lat_a, lng_a = float(w_a.get("latitude", 0)), float(w_a.get("longitude", 0))

            close_works = []
            for j in range(n):
                if i == j:
                    continue
                w_b = works[j]
                if w_a.get("work_category") == w_b.get("work_category"):
                    lat_b, lng_b = float(w_b.get("latitude", 0)), float(w_b.get("longitude", 0))
                    dist_km = calculate_haversine_distance(lat_a, lng_a, lat_b, lng_b)
                    
                    if dist_km <= self.proximity_threshold_km:
                        close_works.append((w_b["work_id"], round(dist_km * 1000.0, 0)))

            if close_works:
                close_works.sort(key=lambda x: x[1])
                closest_id, closest_m = close_works[0]
                
                signal = AnomalySignal(
                    signal_type="GIS_SPATIAL_PROXIMITY",
                    severity=RiskLevel.MEDIUM if closest_m > 100 else RiskLevel.HIGH,
                    score=min(100.0, max(40.0, 100.0 - (closest_m / 3.0))),
                    title="Geographic Spatial Proximity Cluster",
                    details=f"Work is located within {closest_m:.0f} meters of another asset ({closest_id}) of the same category '{w_a.get('work_category')}'.",
                    evidence={
                        "nearby_work_id": closest_id,
                        "distance_meters": closest_m,
                        "cluster_count": len(close_works)
                    }
                )
                results.setdefault(id_a, []).append(signal)

        return results
