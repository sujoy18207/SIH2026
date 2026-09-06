"""
PHASE 6 — NLP SIMILARITY DETECTION
====================================
Detects duplicate/similar work descriptions using TF-IDF + Cosine Similarity.
Blocks comparisons by constituency/district to avoid O(n²) on 400K records.

Mathematical Basis:
    TF(t,d) = term frequency of term t in document d
    IDF(t)  = log(N / df(t))   where N = total docs, df(t) = docs containing t
    TF-IDF(t,d) = TF(t,d) × IDF(t)
    
    CosineSimilarity(A,B) = (A · B) / (||A|| × ||B||)

Output:
    ml/data/nlp_similarity_results.csv — project pairs with similarity scores
    ml/data/nlp_duplicate_risk.csv — per-project duplicate risk score
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

from config import (OUTPUT_DIR, REPORT_DIR, SIMILARITY_THRESHOLD,
                    MAX_PAIRS_PER_BLOCK, MIN_DESCRIPTION_LENGTH)

DATA_DIR = OUTPUT_DIR


def find_similar_pairs_in_block(
    project_ids: List,
    descriptions: List[str],
    threshold: float = SIMILARITY_THRESHOLD,
) -> List[dict]:
    """Find similar description pairs within a single block (e.g., same constituency)."""
    if len(descriptions) < 2:
        return []

    # TF-IDF with word + character n-grams for robustness
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer="word",
        stop_words="english",
        max_features=10000,
        min_df=1,
        max_df=0.95,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(descriptions)
    except ValueError:
        return []

    # Compute cosine similarity (sparse-aware)
    sim_matrix = cosine_similarity(tfidf_matrix)

    pairs = []
    n = len(project_ids)
    for i in range(n):
        for j in range(i + 1, n):
            sim = float(sim_matrix[i, j])
            if sim >= threshold:
                pairs.append({
                    "project_id_1": project_ids[i],
                    "project_id_2": project_ids[j],
                    "similarity": round(sim, 4),
                    "similarity_pct": round(sim * 100, 1),
                    "desc_1_preview": descriptions[i][:100],
                    "desc_2_preview": descriptions[j][:100],
                })

            if len(pairs) >= MAX_PAIRS_PER_BLOCK:
                break
        if len(pairs) >= MAX_PAIRS_PER_BLOCK:
            break

    return pairs


def run_nlp_similarity(master: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Run NLP similarity detection blocked by constituency."""
    print(f"\n  Running NLP similarity on {len(master)} projects…")

    # Filter to projects with valid descriptions
    valid_mask = (
        master["work_description"].notna()
        & (master["work_description"].str.len() >= MIN_DESCRIPTION_LENGTH)
        & (master["work_description"] != "NOT_AVAILABLE_IN_CURRENT_DATASET")
    )
    df = master[valid_mask].copy()
    print(f"  Projects with valid descriptions: {len(df)}")

    # Block by constituency for efficiency
    block_col = "constituency"
    if block_col not in df.columns or df[block_col].isna().all():
        block_col = "state_name"
    
    blocks = df.groupby(block_col)
    print(f"  Number of blocks ({block_col}): {blocks.ngroups}")

    all_pairs = []
    block_count = 0
    for block_name, block_df in blocks:
        if len(block_df) < 2:
            continue

        ids = block_df["project_id"].tolist()
        descs = block_df["work_description"].fillna("").tolist()

        pairs = find_similar_pairs_in_block(ids, descs, SIMILARITY_THRESHOLD)
        if pairs:
            for p in pairs:
                p["block"] = str(block_name)
            all_pairs.extend(pairs)

        block_count += 1
        if block_count % 50 == 0:
            print(f"    Processed {block_count} blocks, found {len(all_pairs)} pairs so far…")

    print(f"  Total similar pairs found: {len(all_pairs)}")

    # Create pairs DataFrame
    pairs_df = pd.DataFrame(all_pairs) if all_pairs else pd.DataFrame(columns=[
        "project_id_1", "project_id_2", "similarity", "similarity_pct", "block"
    ])

    # Create per-project duplicate risk score
    # DuplicateRisk = max similarity score found for this project, scaled to 0-100
    if not pairs_df.empty:
        max_sim_1 = pairs_df.groupby("project_id_1")["similarity_pct"].max().reset_index()
        max_sim_1.columns = ["project_id", "max_similarity_pct"]

        max_sim_2 = pairs_df.groupby("project_id_2")["similarity_pct"].max().reset_index()
        max_sim_2.columns = ["project_id", "max_similarity_pct"]

        all_max = pd.concat([max_sim_1, max_sim_2]).groupby("project_id")["max_similarity_pct"].max().reset_index()
        all_max.columns = ["project_id", "duplicate_risk"]
        # Clamp to 0-100
        all_max["duplicate_risk"] = all_max["duplicate_risk"].clip(0, 100)
    else:
        all_max = pd.DataFrame(columns=["project_id", "duplicate_risk"])

    # Merge with all projects (default 0 for no duplicates)
    dup_risk_df = master[["project_id"]].merge(all_max, on="project_id", how="left")
    dup_risk_df["duplicate_risk"] = dup_risk_df["duplicate_risk"].fillna(0.0)

    return pairs_df, dup_risk_df


def main():
    print("=" * 70)
    print("MPLADS NLP SIMILARITY DETECTION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    master_path = DATA_DIR / "master_projects.csv"
    if not master_path.exists():
        print(f"ERROR: Master table not found at {master_path}")
        return

    master = pd.read_csv(master_path, low_memory=False)
    print(f"  Loaded: {master.shape}")

    pairs_df, dup_risk_df = run_nlp_similarity(master)

    # Save results
    pairs_path = DATA_DIR / "nlp_similarity_results.csv"
    pairs_df.to_csv(pairs_path, index=False)
    print(f"\n✅ Similarity pairs saved: {pairs_path} ({len(pairs_df)} pairs)")

    dup_path = DATA_DIR / "nlp_duplicate_risk.csv"
    dup_risk_df.to_csv(dup_path, index=False)
    print(f"   Duplicate risk scores: {dup_path} ({len(dup_risk_df)} projects)")

    # Summary
    if not dup_risk_df.empty:
        high_dup = (dup_risk_df["duplicate_risk"] >= 70).sum()
        print(f"   Projects with high duplicate risk (≥70): {high_dup}")

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_projects": len(master),
        "total_pairs": len(pairs_df),
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "blocking_strategy": "by constituency",
        "high_duplicate_risk_count": int(high_dup) if not dup_risk_df.empty else 0,
        "note": "Without GPS data, duplicate risk is based solely on text similarity.",
    }
    report_path = REPORT_DIR / "nlp_similarity_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"   Report: {report_path}")


if __name__ == "__main__":
    main()
