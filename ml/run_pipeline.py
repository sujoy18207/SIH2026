"""
MPLADS ANOMALY DETECTION PIPELINE ORCHESTRATOR
================================================
Runs the entire ML pipeline end-to-end:
  Stage 1: Data Audit
  Stage 2: Data Cleaning
  Stage 3: Data Integration (Master Project Table)
  Stage 4: Feature Engineering
  Stage 5: Rule Engine Evaluation
  Stage 6: NLP Similarity Detection
  Stage 7: GIS Spatial Analysis (Stub)
  Stage 8: Agency / Contractor Profiling
  Stage 9: Isolation Forest Model Training
  Stage 10: Model Evaluation & Benchmark
  Stage 11: Composite Risk Engine & Explanations

Usage:
    python ml/run_pipeline.py [--skip-audit] [--skip-nlp]
"""

import sys
import time
import io
import argparse
from pathlib import Path
from datetime import datetime

# Set stdout/stderr encoding to UTF-8 for Windows console support
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import data_audit
import data_cleaning
import data_integration
import feature_engineering
import rule_engine
import nlp_similarity
import gis_analysis
import agency_profiler
import train_isolation_forest
import evaluate_model
import risk_engine


def run_full_pipeline(skip_audit: bool = False, skip_nlp: bool = False):
    start_time = time.time()
    print("=" * 80)
    print("      MPLADS ANOMALY DETECTION & RISK INTELLIGENCE PIPELINE")
    print(f"      Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    stages = []

    # Stage 1: Data Audit
    if not skip_audit:
        print("\n=== STAGE 1/11: Data Audit ===")
        t0 = time.time()
        data_audit.main()
        stages.append(("Stage 1: Data Audit", round(time.time() - t0, 2)))
    else:
        print("\n=== STAGE 1/11: Data Audit (Skipped) ===")

    # Stage 2: Data Cleaning
    print("\n=== STAGE 2/11: Data Cleaning ===")
    t0 = time.time()
    data_cleaning.main()
    stages.append(("Stage 2: Data Cleaning", round(time.time() - t0, 2)))

    # Stage 3: Data Integration
    print("\n=== STAGE 3/11: Master Table Integration ===")
    t0 = time.time()
    data_integration.main()
    stages.append(("Stage 3: Data Integration", round(time.time() - t0, 2)))

    # Stage 4: Feature Engineering
    print("\n=== STAGE 4/11: Feature Engineering ===")
    t0 = time.time()
    feature_engineering.main()
    stages.append(("Stage 4: Feature Engineering", round(time.time() - t0, 2)))

    # Stage 5: Rule Engine
    print("\n=== STAGE 5/11: Rule Engine Evaluation ===")
    t0 = time.time()
    rule_engine.main()
    stages.append(("Stage 5: Rule Engine", round(time.time() - t0, 2)))

    # Stage 6: NLP Similarity
    if not skip_nlp:
        print("\n=== STAGE 6/11: NLP Similarity Detection ===")
        t0 = time.time()
        nlp_similarity.main()
        stages.append(("Stage 6: NLP Similarity", round(time.time() - t0, 2)))
    else:
        print("\n=== STAGE 6/11: NLP Similarity Detection (Skipped) ===")

    # Stage 7: GIS Analysis
    print("\n=== STAGE 7/11: GIS Analysis (Stub) ===")
    t0 = time.time()
    gis_analysis.main()
    stages.append(("Stage 7: GIS Analysis", round(time.time() - t0, 2)))

    # Stage 8: Agency Profiling
    print("\n=== STAGE 8/11: Agency & Contractor Profiling ===")
    t0 = time.time()
    agency_profiler.main()
    stages.append(("Stage 8: Agency Profiling", round(time.time() - t0, 2)))

    # Stage 9: Isolation Forest Training
    print("\n=== STAGE 9/11: Isolation Forest Training ===")
    t0 = time.time()
    train_isolation_forest.main()
    stages.append(("Stage 9: Isolation Forest Training", round(time.time() - t0, 2)))

    # Stage 10: Model Evaluation
    print("\n=== STAGE 10/11: Model Evaluation ===")
    t0 = time.time()
    evaluate_model.main()
    stages.append(("Stage 10: Model Evaluation", round(time.time() - t0, 2)))

    # Stage 11: Composite Risk Engine
    print("\n=== STAGE 11/11: Composite Risk Engine ===")
    t0 = time.time()
    risk_engine.main()
    stages.append(("Stage 11: Composite Risk Engine", round(time.time() - t0, 2)))

    total_time = round(time.time() - start_time, 2)

    print("\n" + "=" * 80)
    print("      PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    for stage_name, duration in stages:
        print(f"  - {stage_name:<40} : {duration:>6.2f}s")
    print("-" * 80)
    print(f"  TOTAL EXECUTION TIME                       : {total_time:>6.2f}s")
    print("=" * 80)
    print("✅ ML Anomaly Detection Pipeline completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MPLADS ML Pipeline")
    parser.add_argument("--skip-audit", action="store_true", help="Skip Data Audit stage")
    parser.add_argument("--skip-nlp", action="store_true", help="Skip NLP Similarity stage")
    args = parser.parse_args()

    run_full_pipeline(skip_audit=args.skip_audit, skip_nlp=args.skip_nlp)
