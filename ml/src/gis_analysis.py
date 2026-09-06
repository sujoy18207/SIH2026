"""
PHASE 7 — GIS ANALYSIS (STUB)
===============================
Geographic / spatial analysis for MPLADS projects.

STATUS: DISABLED
REASON: GPS coordinates (latitude/longitude) are NOT present in the current
        eSAKSHI dataset. This module provides a stub implementation that
        returns empty results.

If geocoding is added in the future (e.g., by mapping constituency names
to approximate coordinates), this module can be activated.

Haversine Distance Formula (for reference):
    d = 2R × arcsin(√(sin²(Δφ/2) + cos(φ1)×cos(φ2)×sin²(Δλ/2)))
    where R = 6371 km (Earth's radius)
"""

import math
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from config import OUTPUT_DIR, REPORT_DIR, GIS_MAX_DISTANCE_KM, GIS_TEXT_WEIGHT, GIS_GEO_WEIGHT

DATA_DIR = OUTPUT_DIR


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine formula: great-circle distance between two points in km.
    Preserved for future use when GPS data becomes available.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_duplicate_risk_with_gis(
    cosine_similarity: float,
    distance_km: float,
    max_distance_km: float = 1.0,
) -> float:
    """
    Combined duplicate risk formula (for future use):
        DuplicateRisk = 0.65 × CosineSimilarity + 0.35 × (1 - Distance/dmax)
    Clamped to [0, 1], then scaled to 0-100.
    """
    geo_component = max(0, 1.0 - (distance_km / max_distance_km))
    risk = 0.65 * cosine_similarity + 0.35 * geo_component
    return round(min(100.0, max(0.0, risk * 100)), 1)


def run_gis_analysis(master: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: Returns empty GIS risk scores.
    GIS analysis is unavailable because GPS coordinates are not in the current dataset.
    """
    print("\n  ⚠️  GIS ANALYSIS DISABLED")
    print("     Reason: latitude/longitude not present in current eSAKSHI dataset.")
    print("     This module returns 0 spatial risk for all projects.")
    print("     Activate by providing GPS coordinates or geocoding constituency data.")

    gis_df = master[["project_id"]].copy()
    gis_df["gis_risk"] = 0.0
    gis_df["gis_available"] = False

    return gis_df


def main():
    print("=" * 70)
    print("MPLADS GIS ANALYSIS (DISABLED)")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        return

    master = pd.read_csv(master_path, low_memory=False)
    gis_df = run_gis_analysis(master)

    out_path = DATA_DIR / "gis_results.csv"
    gis_df.to_csv(out_path, index=False)
    print(f"\n✅ GIS results saved: {out_path} (all zeros — module disabled)")

    # Document unavailability
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "DISABLED",
        "reason": "GPS coordinates (latitude/longitude) are NOT present in the current eSAKSHI dataset.",
        "haversine_formula": "d = 2R × arcsin(√(sin²(Δφ/2) + cos(φ1)×cos(φ2)×sin²(Δλ/2)))",
        "activation_requirement": "Provide latitude/longitude columns or geocode constituency/district names.",
    }
    report_path = REPORT_DIR / "gis_analysis_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"   Report: {report_path}")


if __name__ == "__main__":
    main()
