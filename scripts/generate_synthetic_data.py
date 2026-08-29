"""
Synthetic MPLADS Dataset Generator (Upgraded Scale: 10,000 records)
Generates 10,000 realistic eSAKSHI MPLADS records (95% normal, 5% injected ground-truth anomalies)
across 10 Indian states, 30 districts, and 50 constituencies with controlled anomaly distribution.
"""

import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

STATES_DATA = [
    {
        "state": "West Bengal",
        "districts": [
            {"district": "Nadia", "constituencies": ["Krishnanagar", "Ranaghat"], "coords": (23.4710, 88.5565)},
            {"district": "Murshidabad", "constituencies": ["Baharampur", "Jangipur"], "coords": (24.0988, 88.2679)},
            {"district": "Kolkata", "constituencies": ["Kolkata Uttar", "Kolkata Dakshin"], "coords": (22.5726, 88.3639)},
        ]
    },
    {
        "state": "Maharashtra",
        "districts": [
            {"district": "Pune", "constituencies": ["Pune", "Baramati", "Shirur"], "coords": (18.5204, 73.8567)},
            {"district": "Nagpur", "constituencies": ["Nagpur", "Ramtek"], "coords": (21.1458, 79.0882)},
            {"district": "Nashik", "constituencies": ["Nashik", "Dindori"], "coords": (19.9975, 73.7898)},
        ]
    },
    {
        "state": "Uttar Pradesh",
        "districts": [
            {"district": "Varanasi", "constituencies": ["Varanasi"], "coords": (25.3176, 82.9739)},
            {"district": "Lucknow", "constituencies": ["Lucknow", "Mohanlalganj"], "coords": (26.8467, 80.9462)},
            {"district": "Gorakhpur", "constituencies": ["Gorakhpur"], "coords": (26.7606, 83.3732)},
        ]
    },
    {
        "state": "Karnataka",
        "districts": [
            {"district": "Bengaluru Urban", "constituencies": ["Bengaluru South", "Bengaluru Central"], "coords": (12.9716, 77.5946)},
            {"district": "Mysuru", "constituencies": ["Mysore"], "coords": (12.2958, 76.6394)},
        ]
    },
    {
        "state": "Tamil Nadu",
        "districts": [
            {"district": "Chennai", "constituencies": ["Chennai South", "Chennai North"], "coords": (13.0827, 80.2707)},
            {"district": "Coimbatore", "constituencies": ["Coimbatore"], "coords": (11.0168, 76.9558)},
        ]
    }
]

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

MP_NAMES = {
    "Lok Sabha": [
        "Hon. Smt. Mahua Moitra", "Hon. Shri Kalyan Banerjee", "Hon. Shri Nitin Gadkari",
        "Hon. Shri Tejasvi Surya", "Hon. Shri Dayanidhi Maran", "Hon. Smt. Hema Malini",
        "Hon. Shri Rajnath Singh", "Hon. Shri Jagadambika Pal"
    ],
    "Rajya Sabha": [
        "Hon. Shri Derek O'Brien", "Hon. Shri Sharad Pawar", "Hon. Shri P. Chidambaram",
        "Hon. Smt. Jaya Bachchan", "Hon. Dr. Manmohan Singh"
    ]
}


def generate_synthetic_dataset(total_records=10000):
    dataset = []
    anomaly_ground_truth = {}
    
    start_base = datetime(2023, 4, 1)

    for i in range(1, total_records + 1):
        work_id = f"MPL-2024-{i:05d}"
        
        st = random.choice(STATES_DATA)
        state_name = st["state"]
        dist_info = random.choice(st["districts"])
        district_name = dist_info["district"]
        constituency_name = random.choice(dist_info["constituencies"])
        base_lat, base_lng = dist_info["coords"]
        
        house = random.choice(["Lok Sabha", "Rajya Sabha"])
        mp_name = random.choice(MP_NAMES[house])
        
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

        lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
        lng = round(base_lng + random.uniform(-0.05, 0.05), 6)
        
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
        # Place within 50m of work 0
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

    print(f"[OK] Generated synthetic dataset with {len(dataset)} records at: {out_path}")
    print(f"[OK] Generated ground truth labels for {len(anomaly_ground_truth)} anomalous works at: {gt_path}")
    return dataset, anomaly_ground_truth


if __name__ == "__main__":
    generate_synthetic_dataset(10000)
