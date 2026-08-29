"""
Synthetic MPLADS Dataset Generator (Upgraded Scale: 10,000 records)
Generates 10,000 realistic eSAKSHI MPLADS records (95% normal, 5% injected ground-truth anomalies)
using the OFFICIAL 544 Members of Parliament Excel Database ('Allocated Limit for Honble MPs.xlsx').
"""

import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

def load_official_mp_database():
    excel_path = "Allocated Limit for Honble MPs.xlsx"
    if os.path.exists(excel_path):
        try:
            import pandas as pd
            df = pd.read_excel(excel_path, engine='calamine', skiprows=1, names=['sr_no', 'state', 'mp_name', 'constituency', 'allocated_amount'])
            mp_records = []
            for _, row in df.iterrows():
                if pd.notna(row['mp_name']) and pd.notna(row['state']):
                    mp_records.append({
                        "mp_name": str(row['mp_name']).strip(),
                        "state": str(row['state']).strip(),
                        "constituency": str(row['constituency']).strip() if pd.notna(row['constituency']) else "General",
                        "allocated_amount": float(row['allocated_amount']) if pd.notna(row['allocated_amount']) and str(row['allocated_amount']).replace('.','').isdigit() else 147000000.0
                    })
            if mp_records:
                print(f"[OK] Loaded {len(mp_records)} OFFICIAL MP records from '{excel_path}'")
                return mp_records
        except Exception as e:
            print(f"[WARN] Failed to read Excel database ({e}), using default fallback.")
    return None


CATEGORIES_BASE_COST = {
    "Drinking Water & Sanitation": (150000, 800000),
    "Roads, Bridges & Culverts": (500000, 3500000),
    "Community Halls & Shelters": (1000000, 4500000),
    "Education & School Building": (400000, 2500000),
    "Public Health & Medical Equipment": (300000, 2000000),
    "Solar Street Lighting": (100000, 600000),
    "Irrigation & Flood Control": (600000, 3000000)
}

WORK_DESCRIPTIONS = {
    "Drinking Water & Sanitation": [
        "Installation of Deep Tube Well with Solar Pump at Village Gram Panchayat Ward {}",
        "Construction of Public Sanitation Facility near Bus Stand Ward {}",
        "Supply and Commissioning of RO Drinking Water Plant at Community Center Ward {}",
    ],
    "Roads, Bridges & Culverts": [
        "Construction of Concrete Road from Main Highway to Village Market Ward {}",
        "Repair and Bituminous Overlay of Link Road connecting GP Office Ward {}",
        "Construction of RCC Box Culvert across Drainage Channel Ward {}",
    ],
    "Community Halls & Shelters": [
        "Construction of Multi-purpose Community Cultural Hall at Ward {}",
        "Construction of Senior Citizen Activity Center and Meeting Shelter Ward {}",
        "Building of Public Auditorium and Event Pavilion Ward {}",
    ],
    "Education & School Building": [
        "Construction of Additional Classrooms at Government Higher Secondary School Ward {}",
        "Establishment of Digital Smart Computer Lab at Zilla Parishad School Ward {}",
        "Renovation and Roof Repair of Primary School Building Ward {}",
    ],
    "Public Health & Medical Equipment": [
        "Supply of Advanced Diagnostic X-Ray Equipment for Primary Health Centre Ward {}",
        "Construction of Patient Waiting Hall at Sub-Divisional Hospital Ward {}",
        "Provision of Mobile Ambulance Unit with ICU Equipment Ward {}",
    ],
    "Solar Street Lighting": [
        "Installation of Standalone LED Solar Street Lights along Main Road Ward {}",
        "Erection of High-Mast Solar Light Poles at Public Intersection Ward {}",
    ],
    "Irrigation & Flood Control": [
        "De-siltation and Retaining Wall Construction for Village Irrigation Tank Ward {}",
        "Construction of Check Dam across Canal for Water Conservation Ward {}",
    ]
}

AGENCIES = [
    "Public Works Department (PWD)",
    "Zilla Parishad Engineering Division",
    "Rural Development & Panchayat Raj Agency",
    "District Urban Development Agency (DUDA)",
    "Irrigation & Waterways Department",
    "State Health Infrastructure Corporation",
    "Municipal Corporation Engineering Cell"
]


def generate_synthetic_dataset(total_records=10000):
    official_mps = load_official_mp_database()
    dataset = []
    anomaly_ground_truth = {}
    
    start_base = datetime(2023, 4, 1)

    for i in range(1, total_records + 1):
        work_id = f"MPL-2024-{i:05d}"
        
        if official_mps:
            mp_rec = random.choice(official_mps)
            state_name = mp_rec["state"]
            constituency_name = mp_rec["constituency"]
            mp_name = f"Hon'ble {mp_rec['mp_name']}"
            district_name = constituency_name.split("_")[0]
        else:
            state_name = "West Bengal"
            district_name = "Nadia"
            constituency_name = "Krishnanagar"
            mp_name = "Hon'ble Mahua Moitra"

        house = "Lok Sabha"
        category = random.choice(list(CATEGORIES_BASE_COST.keys()))
        ward_num = random.randint(1, 99)
        desc_tmpl = random.choice(WORK_DESCRIPTIONS[category])
        work_description = desc_tmpl.format(ward_num)
        
        min_c, max_c = CATEGORIES_BASE_COST[category]
        estimated_cost = round(random.uniform(min_c, max_c), -3)
        sanctioned_amount = estimated_cost
        
        rec_days = random.randint(0, 700)
        rec_date = start_base + timedelta(days=rec_days)
        sanc_date = rec_date + timedelta(days=random.randint(10, 60))
        st_date = sanc_date + timedelta(days=random.randint(7, 30))
        exp_comp_date = st_date + timedelta(days=random.randint(120, 365))
        
        agency_name = random.choice(AGENCIES)
        agency_id = f"AGY-{abs(hash(agency_name)) % 1000:03d}"

        work_status = random.choice(["In Progress", "Completed", "Sanctioned"])
        if work_status == "Completed":
            act_comp_date = exp_comp_date - timedelta(days=random.randint(-30, 60))
            physical_progress = 100.0
            financial_progress = 100.0
            expenditure = sanctioned_amount
        elif work_status == "In Progress":
            act_comp_date = None
            physical_progress = round(random.uniform(20.0, 95.0), 1)
            financial_progress = min(100.0, round(physical_progress + random.uniform(-8.0, 8.0), 1))
            expenditure = round(sanctioned_amount * (financial_progress / 100.0), -2)
        else:
            act_comp_date = None
            st_date = None
            physical_progress = 0.0
            financial_progress = 0.0
            expenditure = 0.0

        base_lat = 22.5 + random.uniform(-5.0, 5.0)
        base_lng = 78.0 + random.uniform(-5.0, 5.0)
        lat = round(base_lat, 6)
        lng = round(base_lng, 6)
        
        photo_cnt = random.randint(2, 10) if physical_progress > 20 else random.randint(0, 1)
        doc_cnt = random.randint(2, 5)

        record = {
            "work_id": work_id,
            "state": state_name,
            "district": district_name,
            "constituency": constituency_name,
            "mp_name": mp_name,
            "house": house,
            "work_category": category,
            "work_description": work_description,
            "recommendation_date": rec_date.strftime("%Y-%m-%d"),
            "sanction_date": sanc_date.strftime("%Y-%m-%d"),
            "start_date": st_date.strftime("%Y-%m-%d") if st_date else None,
            "expected_completion_date": exp_comp_date.strftime("%Y-%m-%d"),
            "actual_completion_date": act_comp_date.strftime("%Y-%m-%d") if act_comp_date else None,
            "estimated_cost": estimated_cost,
            "sanctioned_amount": sanctioned_amount,
            "expenditure": expenditure,
            "implementing_agency_id": agency_id,
            "implementing_agency_name": agency_name,
            "work_status": work_status,
            "physical_progress_pct": physical_progress,
            "financial_progress_pct": financial_progress,
            "latitude": lat,
            "longitude": lng,
            "photo_count": photo_cnt,
            "documents_count": doc_cnt
        }
        dataset.append(record)

    # -------------------------------------------------------------
    # INJECT 500 CONTROLLED GROUND TRUTH ANOMALIES (5% of 10,000)
    # -------------------------------------------------------------
    used_indices = set()

    # Category 1: Cost Anomalies (100 cases)
    for _ in range(100):
        idx = random.randint(0, total_records - 1)
        while idx in used_indices:
            idx = random.randint(0, total_records - 1)
        used_indices.add(idx)
        dataset[idx]["estimated_cost"] *= round(random.uniform(3.2, 5.5), 2)
        dataset[idx]["sanctioned_amount"] = dataset[idx]["estimated_cost"]
        if dataset[idx]["work_status"] == "Completed":
            dataset[idx]["expenditure"] = dataset[idx]["sanctioned_amount"]
        anomaly_ground_truth.setdefault(dataset[idx]["work_id"], []).append("COST_ANOMALY")

    # Category 2: Duplicate Work Candidates (100 cases = 50 pairs)
    for _ in range(50):
        idx1 = random.randint(0, total_records - 1)
        idx2 = random.randint(0, total_records - 1)
        if idx1 in used_indices or idx2 in used_indices or idx1 == idx2:
            continue
        used_indices.add(idx1)
        used_indices.add(idx2)

        dataset[idx2]["state"] = dataset[idx1]["state"]
        dataset[idx2]["district"] = dataset[idx1]["district"]
        dataset[idx2]["constituency"] = dataset[idx1]["constituency"]
        dataset[idx2]["latitude"] = dataset[idx1]["latitude"] + random.uniform(-0.0007, 0.0007)
        dataset[idx2]["longitude"] = dataset[idx1]["longitude"] + random.uniform(-0.0007, 0.0007)
        dataset[idx2]["work_category"] = dataset[idx1]["work_category"]
        dataset[idx2]["work_description"] = dataset[idx1]["work_description"].replace("Construction of", "Building of").replace("Installation of", "Erection of")
        dataset[idx2]["estimated_cost"] = dataset[idx1]["estimated_cost"] * random.uniform(0.96, 1.04)
        dataset[idx2]["sanctioned_amount"] = dataset[idx2]["estimated_cost"]

        anomaly_ground_truth.setdefault(dataset[idx1]["work_id"], []).append("DUPLICATE_WORK")
        anomaly_ground_truth.setdefault(dataset[idx2]["work_id"], []).append("DUPLICATE_WORK")

    # Category 3: Severe Timeline Delay Risk (100 cases)
    for _ in range(100):
        idx = random.randint(0, total_records - 1)
        if idx in used_indices:
            continue
        used_indices.add(idx)
        dataset[idx]["work_status"] = "In Progress"
        dataset[idx]["sanction_date"] = "2023-05-10"
        dataset[idx]["expected_completion_date"] = "2023-11-10"
        dataset[idx]["physical_progress_pct"] = 14.0
        dataset[idx]["financial_progress_pct"] = 62.0
        anomaly_ground_truth.setdefault(dataset[idx]["work_id"], []).append("EXCESSIVE_DELAY")

    # Category 4: Financial vs Physical Progress Mismatch (80 cases)
    for _ in range(80):
        idx = random.randint(0, total_records - 1)
        if idx in used_indices:
            continue
        used_indices.add(idx)
        dataset[idx]["work_status"] = "In Progress"
        dataset[idx]["financial_progress_pct"] = round(random.uniform(88.0, 98.0), 1)
        dataset[idx]["physical_progress_pct"] = round(random.uniform(5.0, 20.0), 1)
        dataset[idx]["expenditure"] = round(dataset[idx]["sanctioned_amount"] * (dataset[idx]["financial_progress_pct"] / 100.0), -2)
        dataset[idx]["photo_count"] = 0
        anomaly_ground_truth.setdefault(dataset[idx]["work_id"], []).append("PROGRESS_MISMATCH")

    # Category 5: Geographic Proximity Cluster (50 cases)
    for _ in range(50):
        idx = random.randint(0, total_records - 1)
        if idx in used_indices:
            continue
        used_indices.add(idx)
        dataset[idx]["latitude"] = dataset[0]["latitude"] + random.uniform(-0.0003, 0.0003)
        dataset[idx]["longitude"] = dataset[0]["longitude"] + random.uniform(-0.0003, 0.0003)
        dataset[idx]["work_category"] = dataset[0]["work_category"]
        anomaly_ground_truth.setdefault(dataset[idx]["work_id"], []).append("GIS_SPATIAL_PROXIMITY")

    # Category 6: Compliance / Missing Photo Violations (40 cases)
    for _ in range(40):
        idx = random.randint(0, total_records - 1)
        if idx in used_indices:
            continue
        used_indices.add(idx)
        dataset[idx]["financial_progress_pct"] = 75.0
        dataset[idx]["photo_count"] = 0
        anomaly_ground_truth.setdefault(dataset[idx]["work_id"], []).append("MISSING_EVIDENCE")

    # Category 7: Data Quality Flaws (30 cases for testing Data Quality Engine)
    for _ in range(30):
        idx = random.randint(0, total_records - 1)
        if idx in used_indices:
            continue
        used_indices.add(idx)
        dataset[idx]["latitude"] = 0.0
        dataset[idx]["longitude"] = 0.0

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "mplads_synthetic_dataset.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    gt_path = os.path.join("data", "anomaly_ground_truth.json")
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(anomaly_ground_truth, f, indent=2)

    print(f"[OK] Generated dataset with {len(dataset)} records using official MP database at: {out_path}")
    return dataset, anomaly_ground_truth


if __name__ == "__main__":
    generate_synthetic_dataset(10000)
