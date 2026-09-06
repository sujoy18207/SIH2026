"""
NLP Similarity & Duplicate Work Detection Engine for real eSAKSHI data.
Detects duplicate works via (a) exact normalized-description grouping and
(b) TF-IDF n-gram cosine similarity, blocked by (state, district) to keep
comparison feasible at national scale. Duplicate evidence combines text
similarity with amount proximity within the same district.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.mplads import AnomalySignal, RiskLevel


def normalize_description(desc: str) -> str:
    """Lowercase, collapse whitespace — used as the exact-duplicate key."""
    return " ".join((desc or "").lower().split())


class NLPDuplicateEngine:
    def __init__(self, sim_threshold: float = 0.75, max_block_size: int = 2000):
        self.sim_threshold = sim_threshold
        self.max_block_size = max_block_size   # skip TF-IDF on oversized blocks (exact-hash still runs)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words="english", max_features=50000)

    def find_duplicate_pairs(self, works: List[Dict[str, Any]]) -> Dict[str, Tuple[str, float, float, AnomalySignal]]:
        """
        Returns {work_id: (best_match_id, duplicate_risk_score, amount_ratio, signal)}.
        Only the strongest candidate per work is recorded.
        """
        if len(works) < 2:
            return {}

        # ---------------------------------------------------------------
        # Pass 1: exact normalized-description duplicates within district
        # ---------------------------------------------------------------
        desc_blocks: Dict[Tuple[str, str], Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        for idx, w in enumerate(works):
            key = (w.get("state") or "", w.get("district") or "")
            desc_blocks[key][normalize_description(w.get("work_description"))].append(idx)

        exact_map: Dict[int, int] = {}   # idx -> best duplicate idx
        for key, descs in desc_blocks.items():
            for desc, idxs in descs.items():
                if len(desc) >= 20 and len(idxs) > 1:
                    for i in idxs:
                        # Best match: pick the first other member with a sanction amount
                        for j in idxs:
                            if i != j:
                                exact_map[i] = j
                                break

        # ---------------------------------------------------------------
        # Pass 2: TF-IDF cosine similarity per (state, district) block
        # ---------------------------------------------------------------
        sim_map: Dict[int, Tuple[int, float]] = {}   # idx -> (best_idx, best_sim)
        blocks: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        for idx, w in enumerate(works):
            blocks[(w.get("state") or "", w.get("district") or "")].append(idx)

        for key, idxs in blocks.items():
            if len(idxs) < 2 or len(idxs) > self.max_block_size:
                continue
            corpus = [works[i].get("work_description") or "" for i in idxs]
            try:
                tfidf_matrix = self.vectorizer.fit_transform(corpus)
            except ValueError:
                # Empty vocabulary in block
                continue
            cos_sim = cosine_similarity(tfidf_matrix)
            n = len(idxs)
            for a in range(n):
                i = idxs[a]
                best_j, best_sim = None, 0.0
                for b in range(n):
                    if a == b:
                        continue
                    sim = float(cos_sim[a, b])
                    if sim >= self.sim_threshold and sim > best_sim:
                        best_sim = sim
                        best_j = idxs[b]
                if best_j is not None:
                    prev = sim_map.get(i)
                    if prev is None or best_sim > prev[1]:
                        sim_map[i] = (best_j, best_sim)

        # ---------------------------------------------------------------
        # Merge passes: exact dupes rank above fuzzy matches
        # ---------------------------------------------------------------
        duplicates: Dict[str, Tuple[str, float, float, AnomalySignal]] = {}

        def record(i: int, j: int, sim_pct: float, match_kind: str):
            wa, wb = works[i], works[j]
            sa = float(wa.get("sanction_amount") or 0.0)
            sb = float(wb.get("sanction_amount") or 0.0)
            amount_ratio = (min(sa, sb) / max(sa, sb)) if (sa > 0 and sb > 0) else 0.0

            # Amount proximity boosts risk when both costs are known
            if amount_ratio >= 0.85:
                score = min(100.0, sim_pct + 10.0)
            elif amount_ratio >= 0.5:
                score = sim_pct
            else:
                score = sim_pct * 0.8

            if match_kind == "exact":
                score = max(score, 85.0)

            severity = RiskLevel.CRITICAL if score >= 85.0 else RiskLevel.HIGH

            signal = AnomalySignal(
                signal_type="NLP_DUPLICATE_WORK",
                severity=severity,
                score=round(score, 1),
                title="Potentially Similar/Duplicate Work — Verification Required",
                details=(f"{'Identical' if match_kind == 'exact' else f'{sim_pct:.0f}% similar'} work "
                         f"description matches work {wb['work_id']} in {wa.get('district')}, "
                         f"{wa.get('state')}"
                         + (f", sanctioned at {amount_ratio:.0%} of its cost" if amount_ratio else "") + "."),
                evidence={
                    "candidate_work_id": wb["work_id"],
                    "similarity_pct": round(sim_pct, 1),
                    "match_kind": match_kind,
                    "amount_ratio": round(amount_ratio, 2),
                    "duplicate_risk_score": round(score, 1),
                    "work_a_desc": wa.get("work_description"),
                }
            )
            duplicates[wa["work_id"]] = (wb["work_id"], score, amount_ratio, signal)

        # Exact matches first (they override fuzzy ones for the same work)
        for i, j in exact_map.items():
            record(i, j, 100.0, "exact")

        for i, (j, sim) in sim_map.items():
            if i in exact_map:
                continue
            record(i, j, round(sim * 100.0, 1), "fuzzy")

        return duplicates
