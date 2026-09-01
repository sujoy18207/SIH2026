"""
PHASE 10 — MODEL EVALUATION
=============================
Evaluates the trained unsupervised anomaly detection models.

Since verified fraud labels are NOT available:
    - Traditional accuracy/precision/recall CANNOT be computed on real data
    - We evaluate using: stability analysis, anomaly ranking, synthetic injection

Evaluation Strategy:
    1. Anomaly Ranking Analysis — inspect top-K anomalies for reasonableness
    2. Stability Analysis — how stable are rankings across contamination values?
    3. Synthetic Anomaly Injection — inject known anomalies and test detection
    4. Feature Importance — which features most influence anomaly scores?
    5. Score Distribution — analyze the distribution of anomaly scores

Output:
    reports/model_evaluation_report.json
    experiments/stability_analysis.csv
    experiments/synthetic_evaluation.csv
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from config import OUTPUT_DIR, EXPERIMENT_DIR, REPORT_DIR, get_current_model_dir

DATA_DIR = OUTPUT_DIR
MODEL_DIR = get_current_model_dir("v1")


def anomaly_ranking_analysis(scores_df: pd.DataFrame, master_df: pd.DataFrame, top_k: int = 20):
    """Analyze top-K highest risk projects for reasonableness."""
    print(f"\n  Anomaly Ranking — Top {top_k} Projects:")
    print("  " + "-" * 80)

    merged = scores_df.merge(master_df[["project_id", "work_description", "state_name",
                                         "constituency", "sanction_amount", "total_expenditure",
                                         "work_category"]], on="project_id", how="left")
    top = merged.nlargest(top_k, "ml_anomaly_risk")

    ranking_records = []
    for rank, (_, row) in enumerate(top.iterrows(), 1):
        exp = pd.to_numeric(row.get("total_expenditure"), errors="coerce")
        san = pd.to_numeric(row.get("sanction_amount"), errors="coerce")
        ratio = (exp / san) if pd.notna(san) and san > 0 and pd.notna(exp) else None

        record = {
            "rank": rank,
            "project_id": int(row["project_id"]) if pd.notna(row["project_id"]) else None,
            "ml_anomaly_risk": round(row["ml_anomaly_risk"], 1),
            "state": str(row.get("state_name", "")),
            "category": str(row.get("work_category", "")),
            "sanction_amount": float(san) if pd.notna(san) else None,
            "total_expenditure": float(exp) if pd.notna(exp) else None,
            "expenditure_ratio": round(ratio, 2) if ratio else None,
            "description_preview": str(row.get("work_description", ""))[:80],
        }
        ranking_records.append(record)

        print(f"    #{rank:2d} | Risk={record['ml_anomaly_risk']:5.1f} | "
              f"Exp/San={record['expenditure_ratio'] or 'N/A'} | "
              f"{record['state'][:15]} | {record['description_preview'][:50]}")

    return ranking_records


def stability_analysis(features_df: pd.DataFrame, feature_cols: list):
    """Test ranking stability across different contamination values."""
    print("\n  Stability Analysis — Ranking consistency across contamination values:")

    from train_isolation_forest import prepare_feature_matrix
    X, used_features, _, _ = prepare_feature_matrix(features_df)

    contaminations = [0.01, 0.02, 0.05, 0.10]
    all_rankings = {}

    for c in contaminations:
        model = IsolationForest(contamination=c, n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X)
        scores = model.decision_function(X)
        # Higher anomaly = more negative decision score
        rankings = np.argsort(scores)  # Indices from most anomalous to least
        top_100 = set(rankings[:100])
        all_rankings[c] = top_100

    # Pairwise overlap of top-100 anomalies
    stability_results = []
    keys = list(all_rankings.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            overlap = len(all_rankings[keys[i]] & all_rankings[keys[j]])
            stability_results.append({
                "contamination_a": keys[i],
                "contamination_b": keys[j],
                "top_100_overlap": overlap,
                "overlap_pct": round(overlap / 100 * 100, 1),
            })
            print(f"    c={keys[i]} vs c={keys[j]}: {overlap}% overlap in top-100")

    return stability_results


def synthetic_injection_evaluation(features_df: pd.DataFrame, feature_cols: list):
    """
    Inject synthetic anomalies and test detection rate.
    
    IMPORTANT: This is a SYNTHETIC benchmark, not real-world fraud detection accuracy.
    """
    print("\n  Synthetic Anomaly Injection Evaluation:")
    print("  ⚠️  These results are SYNTHETIC benchmarks, NOT real-world accuracy.")

    from train_isolation_forest import prepare_feature_matrix
    X, used_features, imputer, scaler = prepare_feature_matrix(features_df)

    n_synthetic = min(100, int(len(X) * 0.02))

    # Create synthetic anomalies: extreme values on multiple features
    rng = np.random.RandomState(42)
    synthetic_anomalies = rng.normal(0, 1, (n_synthetic, X.shape[1]))
    # Make them extreme: multiply by large factor and add offset
    synthetic_anomalies = synthetic_anomalies * 5 + 3

    # Combine
    X_combined = np.vstack([X, synthetic_anomalies])
    labels = np.zeros(len(X_combined))
    labels[len(X):] = 1  # 1 = synthetic anomaly

    # Train and predict
    model = IsolationForest(contamination=0.05, n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_combined)
    predictions = model.predict(X_combined)

    # Evaluate detection of synthetic anomalies
    synthetic_preds = predictions[len(X):]
    detected = (synthetic_preds == -1).sum()
    detection_rate = detected / n_synthetic

    # False positives on real data
    real_preds = predictions[:len(X)]
    false_positives = (real_preds == -1).sum()
    fp_rate = false_positives / len(X)

    results = {
        "evaluation_type": "SYNTHETIC_INJECTION (NOT real-world accuracy)",
        "n_synthetic_anomalies": n_synthetic,
        "n_detected": int(detected),
        "detection_rate": round(detection_rate, 4),
        "n_false_positives_on_real": int(false_positives),
        "false_positive_rate": round(fp_rate, 4),
        "disclaimer": "Synthetic benchmarks do NOT represent real-world fraud detection accuracy.",
    }

    print(f"    Synthetic anomalies injected: {n_synthetic}")
    print(f"    Detected: {detected}/{n_synthetic} ({detection_rate*100:.1f}%)")
    print(f"    False positives on real data: {false_positives} ({fp_rate*100:.1f}%)")

    return results


def score_distribution_analysis(scores_df: pd.DataFrame):
    """Analyze the distribution of anomaly scores."""
    print("\n  Score Distribution Analysis:")

    scores = scores_df["ml_anomaly_risk"]
    distribution = {
        "count": int(len(scores)),
        "mean": round(scores.mean(), 1),
        "std": round(scores.std(), 1),
        "min": round(scores.min(), 1),
        "max": round(scores.max(), 1),
        "percentiles": {
            "p25": round(scores.quantile(0.25), 1),
            "p50": round(scores.quantile(0.50), 1),
            "p75": round(scores.quantile(0.75), 1),
            "p90": round(scores.quantile(0.90), 1),
            "p95": round(scores.quantile(0.95), 1),
            "p99": round(scores.quantile(0.99), 1),
        },
        "risk_categories": {
            "LOW (0-29)": int((scores < 30).sum()),
            "MEDIUM (30-59)": int(((scores >= 30) & (scores < 60)).sum()),
            "HIGH (60-79)": int(((scores >= 60) & (scores < 80)).sum()),
            "CRITICAL (80-100)": int((scores >= 80).sum()),
        },
    }

    for cat, count in distribution["risk_categories"].items():
        print(f"    {cat}: {count} ({count/len(scores)*100:.1f}%)")

    return distribution


def main():
    print("=" * 70)
    print("MPLADS MODEL EVALUATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # Load data
    scores_path = DATA_DIR / "ml_anomaly_scores.csv"
    features_path = DATA_DIR / "features.csv"
    master_path = DATA_DIR / "master_projects.csv"

    if not scores_path.exists():
        print("ERROR: ML anomaly scores not found. Run train_isolation_forest.py first.")
        return

    scores_df = pd.read_csv(scores_path)
    features_df = pd.read_csv(features_path) if features_path.exists() else pd.DataFrame()
    master_df = pd.read_csv(master_path, low_memory=False) if master_path.exists() else pd.DataFrame()

    # Load feature config
    config_path = MODEL_DIR / "feature_config.json"
    if config_path.exists():
        with open(config_path) as f:
            feature_config = json.load(f)
        feature_cols = feature_config.get("features", [])
    else:
        feature_cols = []

    report = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "model_version": "v1",
        "total_projects": len(scores_df),
        "labels_available": False,
        "evaluation_note": "No verified fraud labels available. Using unsupervised evaluation methods.",
    }

    # 1. Score Distribution
    report["score_distribution"] = score_distribution_analysis(scores_df)

    # 2. Anomaly Ranking
    if not master_df.empty:
        report["top_anomalies"] = anomaly_ranking_analysis(scores_df, master_df)

    # 3. Stability Analysis
    if not features_df.empty and feature_cols:
        report["stability_analysis"] = stability_analysis(features_df, feature_cols)

    # 4. Synthetic Injection
    if not features_df.empty and feature_cols:
        report["synthetic_evaluation"] = synthetic_injection_evaluation(features_df, feature_cols)

    # Save report
    report_path = REPORT_DIR / "model_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n✅ Evaluation report saved: {report_path}")


if __name__ == "__main__":
    main()
