"""
PHASE 9 — ISOLATION FOREST TRAINING
=====================================
Unsupervised anomaly detection using scikit-learn's Isolation Forest.

The algorithm identifies statistical outliers in the feature space without
requiring verified fraud labels.

IMPORTANT DISTINCTIONS:
    - Output is "MLAnomalyRisk" (0-100), NOT "FraudProbability"
    - Higher scores indicate more statistically unusual projects
    - Final interpretation requires human review

Normalization:
    Isolation Forest decision_function() returns scores where:
        - More negative = more anomalous
    We invert and scale to 0-100:
        MLAnomalyRisk = 100 × (1 - (score - min) / (max - min))

Hyperparameter experiments:
    contamination: [0.01, 0.02, 0.05, 0.10]
    n_estimators: [100, 200]

Output:
    models/v1/isolation_forest.joblib
    models/v1/preprocessing.joblib
    models/v1/feature_config.json
    models/v1/model_metadata.json
    data/ml_anomaly_scores.csv
    experiments/model_comparison.csv
"""

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from config import (OUTPUT_DIR, EXPERIMENT_DIR, CANDIDATE_FEATURES,
                    PRIMARY_CONTAMINATION, PRIMARY_N_ESTIMATORS, RANDOM_STATE,
                    CONTAMINATION_VALUES, N_ESTIMATORS_VALUES, get_current_model_dir)

DATA_DIR = OUTPUT_DIR
MODEL_DIR = get_current_model_dir("v1")


def prepare_feature_matrix(features_df: pd.DataFrame) -> tuple:
    """Prepare the feature matrix: select available features, impute, scale."""
    available = [f for f in CANDIDATE_FEATURES if f in features_df.columns]
    print(f"  Available features ({len(available)}/{len(CANDIDATE_FEATURES)}): {available}")

    unavailable = [f for f in CANDIDATE_FEATURES if f not in features_df.columns]
    if unavailable:
        print(f"  Unavailable features: {unavailable}")

    X = features_df[available].copy()

    # Replace infinities with NaN
    X = X.replace([np.inf, -np.inf], np.nan)

    # Impute missing values with median
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    print(f"  Feature matrix shape: {X_scaled.shape}")
    print(f"  NaN before imputation: {features_df[available].isna().sum().sum()}")

    return X_scaled, available, imputer, scaler


def train_isolation_forest(
    X: np.ndarray,
    contamination: float = 0.05,
    n_estimators: int = 100,
    random_state: int = 42,
) -> tuple:
    """Train Isolation Forest and return model + scores."""
    model = IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1,
    )

    start_time = time.time()
    model.fit(X)
    train_time = time.time() - start_time

    # Decision function: lower = more anomalous
    decision_scores = model.decision_function(X)
    predictions = model.predict(X)  # -1 for anomaly, 1 for normal

    # Normalize to 0-100 MLAnomalyRisk
    raw_min = decision_scores.min()
    raw_max = decision_scores.max()
    if raw_max > raw_min:
        anomaly_scores = 100.0 * (1.0 - (decision_scores - raw_min) / (raw_max - raw_min))
    else:
        anomaly_scores = np.full_like(decision_scores, 50.0)

    anomaly_scores = np.clip(anomaly_scores, 0, 100)

    n_anomalies = (predictions == -1).sum()

    return model, anomaly_scores, decision_scores, predictions, train_time, n_anomalies


def run_model_comparison(X: np.ndarray) -> pd.DataFrame:
    """Compare Isolation Forest, LOF, and One-Class SVM."""
    print("\n  Running model comparison…")
    results = []

    for contamination in CONTAMINATION_VALUES:
        for n_est in N_ESTIMATORS_VALUES:
            model, scores, _, preds, runtime, n_anom = train_isolation_forest(
                X, contamination=contamination, n_estimators=n_est
            )
            results.append({
                "model": "IsolationForest",
                "contamination": contamination,
                "n_estimators": n_est,
                "n_anomalies": int(n_anom),
                "anomaly_pct": round(n_anom / len(X) * 100, 2),
                "mean_anomaly_score": round(scores.mean(), 1),
                "std_anomaly_score": round(scores.std(), 1),
                "runtime_seconds": round(runtime, 2),
                "notes": "",
            })
            print(f"    IF(c={contamination}, n={n_est}): {n_anom} anomalies ({n_anom/len(X)*100:.1f}%), {runtime:.1f}s")

    # Local Outlier Factor
    for contamination in [0.02, 0.05]:
        try:
            start = time.time()
            lof = LocalOutlierFactor(contamination=contamination, n_neighbors=20, novelty=False)
            lof_preds = lof.fit_predict(X)
            lof_scores = -lof.negative_outlier_factor_
            lof_time = time.time() - start

            n_anom = (lof_preds == -1).sum()
            # Normalize LOF scores to 0-100
            lof_min, lof_max = lof_scores.min(), lof_scores.max()
            if lof_max > lof_min:
                lof_normalized = 100.0 * (lof_scores - lof_min) / (lof_max - lof_min)
            else:
                lof_normalized = np.full_like(lof_scores, 50.0)

            results.append({
                "model": "LocalOutlierFactor",
                "contamination": contamination,
                "n_estimators": "-",
                "n_anomalies": int(n_anom),
                "anomaly_pct": round(n_anom / len(X) * 100, 2),
                "mean_anomaly_score": round(lof_normalized.mean(), 1),
                "std_anomaly_score": round(lof_normalized.std(), 1),
                "runtime_seconds": round(lof_time, 2),
                "notes": f"n_neighbors=20",
            })
            print(f"    LOF(c={contamination}): {n_anom} anomalies, {lof_time:.1f}s")
        except Exception as e:
            print(f"    LOF(c={contamination}): FAILED — {e}")

    # One-Class SVM (only if dataset is small enough — very slow on large data)
    if len(X) <= 50000:
        try:
            start = time.time()
            svm = OneClassSVM(kernel="rbf", gamma="scale", nu=0.05)
            svm.fit(X)
            svm_preds = svm.predict(X)
            svm_time = time.time() - start

            n_anom = (svm_preds == -1).sum()
            results.append({
                "model": "OneClassSVM",
                "contamination": 0.05,
                "n_estimators": "-",
                "n_anomalies": int(n_anom),
                "anomaly_pct": round(n_anom / len(X) * 100, 2),
                "mean_anomaly_score": "-",
                "std_anomaly_score": "-",
                "runtime_seconds": round(svm_time, 2),
                "notes": "kernel=rbf, nu=0.05",
            })
            print(f"    OCSVM: {n_anom} anomalies, {svm_time:.1f}s")
        except Exception as e:
            print(f"    OCSVM: SKIPPED — {e}")
    else:
        print(f"    OCSVM: SKIPPED — dataset too large ({len(X)} rows)")

    return pd.DataFrame(results)


def main():
    print("=" * 70)
    print("MPLADS ISOLATION FOREST TRAINING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # Load feature matrix
    features_path = DATA_DIR / "features.csv"
    if not features_path.exists():
        print(f"ERROR: Feature matrix not found at {features_path}")
        return

    features_df = pd.read_csv(features_path, low_memory=False)
    print(f"  Loaded features: {features_df.shape}")

    # Prepare matrix
    X, used_features, imputer, scaler = prepare_feature_matrix(features_df)

    if X.shape[1] < 2:
        print("ERROR: Need at least 2 features for anomaly detection.")
        return

    # ─── Model Comparison ───
    comparison_df = run_model_comparison(X)
    comparison_path = EXPERIMENT_DIR / "model_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\n  Experiment results: {comparison_path}")

    # ─── Train primary model ───
    print(f"\n  Training primary model: IsolationForest(contamination={PRIMARY_CONTAMINATION}, n_estimators={PRIMARY_N_ESTIMATORS})")

    model, anomaly_scores, decision_scores, predictions, train_time, n_anomalies = train_isolation_forest(
        X, contamination=PRIMARY_CONTAMINATION, n_estimators=PRIMARY_N_ESTIMATORS
    )

    print(f"  Training time: {train_time:.2f}s")
    print(f"  Anomalies detected: {n_anomalies} ({n_anomalies / len(X) * 100:.1f}%)")
    print(f"  Anomaly score range: {anomaly_scores.min():.1f} – {anomaly_scores.max():.1f}")
    print(f"  Anomaly score mean: {anomaly_scores.mean():.1f} ± {anomaly_scores.std():.1f}")

    # ─── Save model artifacts ───
    joblib.dump(model, MODEL_DIR / "isolation_forest.joblib")
    joblib.dump(scaler, MODEL_DIR / "preprocessing_scaler.joblib")
    joblib.dump(imputer, MODEL_DIR / "preprocessing_imputer.joblib")

    feature_config = {
        "features": used_features,
        "candidate_features": CANDIDATE_FEATURES,
        "unavailable_features": [f for f in CANDIDATE_FEATURES if f not in used_features],
    }
    with open(MODEL_DIR / "feature_config.json", "w") as f:
        json.dump(feature_config, f, indent=2)

    model_metadata = {
        "model_version": "v1",
        "training_timestamp": datetime.now().isoformat(),
        "algorithm": "IsolationForest",
        "library": "scikit-learn",
        "hyperparameters": {
            "contamination": PRIMARY_CONTAMINATION,
            "n_estimators": PRIMARY_N_ESTIMATORS,
            "max_samples": "auto",
            "random_state": 42,
        },
        "dataset_version": "esakshi_real_data_v1",
        "number_of_records": int(X.shape[0]),
        "number_of_features": int(X.shape[1]),
        "features_used": used_features,
        "anomalies_detected": int(n_anomalies),
        "anomaly_rate": round(n_anomalies / len(X) * 100, 2),
        "training_time_seconds": round(train_time, 2),
        "normalization": "decision_function inverted and min-max scaled to 0-100",
        "important_note": "MLAnomalyRisk is NOT FraudProbability. It indicates statistical unusualness.",
    }
    with open(MODEL_DIR / "model_metadata.json", "w") as f:
        json.dump(model_metadata, f, indent=2)

    print(f"\n  Model saved: {MODEL_DIR}")

    # ─── Save per-project scores ───
    scores_df = features_df[["project_id"]].copy()
    scores_df["ml_anomaly_risk"] = anomaly_scores.round(1)
    scores_df["ml_prediction"] = np.where(predictions == -1, "ANOMALY", "NORMAL")
    scores_df["ml_decision_score"] = decision_scores.round(4)

    scores_path = DATA_DIR / "ml_anomaly_scores.csv"
    scores_df.to_csv(scores_path, index=False)
    print(f"\n✅ ML anomaly scores saved: {scores_path}")
    print(f"   Anomalies: {(scores_df['ml_prediction'] == 'ANOMALY').sum()}")
    print(f"   Normal: {(scores_df['ml_prediction'] == 'NORMAL').sum()}")


if __name__ == "__main__":
    main()
