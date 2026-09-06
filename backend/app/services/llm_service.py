"""
LLM RAG & Natural Language Investigation Assistant Service
Answers natural-language questions about real eSAKSHI works, risk alerts,
high-risk districts, agencies, and vendor concentration. Supports the Gemini
API with a deterministic local SQL-backed retriever as fallback.
"""

import os
from typing import List, Dict, Any, Optional
import httpx

from app.db import get_connection


class LLMCopilotService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    # ------------------------------------------------------------------
    # Local structured retrieval over the real SQLite dataset
    # ------------------------------------------------------------------
    def _retrieve(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        conn = get_connection()

        try:
            total_works = conn.execute("SELECT COUNT(*) FROM works").fetchone()[0]
            total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            total_disbursed = conn.execute("SELECT COALESCE(SUM(total_disbursed),0) FROM works").fetchone()[0]
            total_sanctioned = conn.execute("SELECT COALESCE(SUM(sanction_amount),0) FROM works").fetchone()[0]

            high_risk = conn.execute(
                "SELECT work_id, work_description, risk_score, risk_level, district, state, total_disbursed, sanction_amount "
                "FROM works WHERE risk_level IN ('High','Critical') ORDER BY risk_score DESC LIMIT 5"
            ).fetchall()

            # State / district mentioned in the query?
            matched_state = None
            states = [r[0] for r in conn.execute("SELECT DISTINCT state FROM works WHERE state IS NOT NULL").fetchall()]
            for s in states:
                if s.lower() in q_lower:
                    matched_state = s
                    break

            matched_district = None
            if matched_state:
                districts = [r[0] for r in conn.execute(
                    "SELECT DISTINCT district FROM works WHERE state=? AND district IS NOT NULL", (matched_state,)).fetchall()]
                for d in districts:
                    if d.lower() in q_lower:
                        matched_district = d
                        break

            rel_works = [dict(r) for r in high_risk]
            answer = None

            if matched_state:
                state_stats = conn.execute(
                    "SELECT COUNT(*), COALESCE(SUM(sanction_amount),0), COALESCE(SUM(total_disbursed),0) "
                    "FROM works WHERE state=?", (matched_state,)).fetchone()
                state_high = conn.execute(
                    "SELECT COUNT(*) FROM works WHERE state=? AND risk_level IN ('High','Critical')",
                    (matched_state,)).fetchone()[0]
                if matched_district:
                    dist_stats = conn.execute(
                        "SELECT COUNT(*), COALESCE(SUM(sanction_amount),0), COALESCE(SUM(total_disbursed),0) "
                        "FROM works WHERE state=? AND district=?", (matched_state, matched_district)).fetchone()
                    dist_high = conn.execute(
                        "SELECT COUNT(*) FROM works WHERE state=? AND district=? AND risk_level IN ('High','Critical')",
                        (matched_state, matched_district)).fetchone()[0]
                    answer = (
                        f"Analysis for **{matched_district}, {matched_state}** (real eSAKSHI data):\n"
                        f"- Works Monitored in District: **{dist_stats[0]:,}**\n"
                        f"- Sanctioned: ₹{dist_stats[1]/1e7:,.1f} Cr | Disbursed: ₹{dist_stats[2]/1e7:,.1f} Cr\n"
                        f"- High / Critical Risk Works in District: **{dist_high}**\n\n"
                        f"Statewide, {matched_state} has **{state_stats[0]:,} works** with **{state_high}** high/critical risk flags."
                    )
                    rel_works = [dict(r) for r in conn.execute(
                        "SELECT work_id, work_description, risk_score, risk_level, district, state FROM works "
                        "WHERE state=? AND district=? ORDER BY risk_score DESC LIMIT 5",
                        (matched_state, matched_district)).fetchall()]
                else:
                    answer = (
                        f"Analysis for **{matched_state}** (real eSAKSHI data):\n"
                        f"- Total Works Monitored: **{state_stats[0]:,}**\n"
                        f"- Sanctioned: ₹{state_stats[1]/1e7:,.1f} Cr | Disbursed: ₹{state_stats[2]/1e7:,.1f} Cr\n"
                        f"- High / Critical Risk Works: **{state_high}**\n\n"
                        f"Ask about a specific district within {matched_state} for drill-down analysis."
                    )
                    rel_works = [dict(r) for r in conn.execute(
                        "SELECT work_id, work_description, risk_score, risk_level, district, state FROM works "
                        "WHERE state=? ORDER BY risk_score DESC LIMIT 5", (matched_state,)).fetchall()]

            elif "agency" in q_lower or "ida" in q_lower or "authority" in q_lower:
                top_agencies = conn.execute(
                    "SELECT agency_name, district, total_works, delayed_works, anomaly_count, agency_risk_score, agency_risk_level "
                    "FROM agencies ORDER BY agency_risk_score DESC LIMIT 5").fetchall()
                n_agencies = conn.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
                agency_lines = "\n".join(
                    f"  - {a['agency_name']} ({a['district']}): {a['total_works']} works, {a['delayed_works']} stalled, risk {a['agency_risk_score']}/100 ({a['agency_risk_level']})"
                    for a in top_agencies
                )
                answer = (
                    f"Agency Risk Analysis (real eSAKSHI data): Evaluated **{n_agencies}** District Authorities (IDAs).\n\n"
                    f"Top-risk authorities:\n{agency_lines}\n\n"
                    f"Field audits are recommended before assigning new sanction orders to high-risk authorities."
                )

            elif "vendor" in q_lower or "contractor" in q_lower or "nexus" in q_lower:
                top_vendors = conn.execute(
                    "SELECT vendor_name, work_count, total_disbursed, district_count, state_count "
                    "FROM vendors ORDER BY work_count DESC LIMIT 5").fetchall()
                n_vendors = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()[0]
                vendor_lines = "\n".join(
                    f"  - {v['vendor_name']}: paid for **{v['work_count']} distinct works** across "
                    f"{v['district_count']} district(s), total ₹{v['total_disbursed']/1e7:,.1f} Cr"
                    for v in top_vendors
                )
                answer = (
                    f"Vendor Concentration Analysis (real eSAKSHI expenditure ledger): **{n_vendors}** unique vendors.\n\n"
                    f"Most concentrated vendors:\n{vendor_lines}\n\n"
                    f"A single vendor receiving payments across hundreds of MPLADS works is a priority "
                    f"verification signal for procurement fairness review."
                )

            elif "duplicate" in q_lower:
                dup_alerts = conn.execute(
                    "SELECT work_id, work_title, district, state, duplicate_risk_score, duplicate_candidate_id "
                    "FROM alerts WHERE duplicate_candidate_id IS NOT NULL ORDER BY duplicate_risk_score DESC LIMIT 5").fetchall()
                n_dup = conn.execute(
                    "SELECT COUNT(*) FROM alerts WHERE duplicate_candidate_id IS NOT NULL").fetchone()[0]
                dup_lines = "\n".join(
                    f"  - Work {d['work_id']} in {d['district']}, {d['state']} ↔ candidate {d['duplicate_candidate_id']} (risk {d['duplicate_risk_score']}%)"
                    for d in dup_alerts
                )
                answer = (
                    f"Duplicate Work Detection (real eSAKSHI data): **{n_dup}** works flagged with similar/duplicate "
                    f"description candidates.\n\nTop candidates:\n{dup_lines or '  (none)'}"
                )

            elif "high risk" in q_lower or "critical" in q_lower or "anomal" in q_lower or "risk" in q_lower:
                sample_ids = [w["work_id"] for w in high_risk[:5]]
                n_high = conn.execute(
                    "SELECT COUNT(*) FROM works WHERE risk_level IN ('High','Critical')").fetchone()[0]
                answer = (
                    f"Currently, out of **{total_works:,}** real eSAKSHI works monitored, the multi-signal risk engine "
                    f"has identified **{n_high:,} high/critical risk works** requiring verification.\n\n"
                    f"Top flagged work IDs include: **{', '.join(sample_ids) or '—'}**. "
                    f"Primary risk drivers are vendor-disbursal overruns vs sanctioned amounts, duplicate descriptions "
                    f"within districts, and long-stalled works."
                )

            else:
                answer = (
                    f"MPLADS Risk Intelligence Summary (real eSAKSHI data):\n"
                    f"- Total Works Monitored: **{total_works:,}**\n"
                    f"- Total Sanctioned: ₹{total_sanctioned/1e7:,.0f} Cr | Total Disbursed: ₹{total_disbursed/1e7:,.0f} Cr\n"
                    f"- Active Explainable Alerts: **{total_alerts:,}**\n\n"
                    f"You can query specific states, districts, high-risk works, agencies, or vendor concentration "
                    f"for detailed evidence dossiers."
                )

            return {"answer": answer, "rel_works": rel_works, "total_works": total_works}
        finally:
            conn.close()

    async def answer_investigation_query(self, query: str) -> Dict[str, Any]:
        """Retrieves relevant evidence from the real dataset and returns a structured AI response."""
        retrieval = self._retrieve(query)
        q_lower = query.lower()

        # If Gemini API key is available, enrich the deterministic answer with the LLM
        if self.api_key:
            try:
                context_summary = f"Total works: {retrieval['total_works']:,}. Question: {query}"
                prompt = (
                    f"You are an expert AI risk analysis assistant for the MPLADS scheme (real eSAKSHI data). "
                    f"Context: {context_summary}\nDeterministic analysis from the platform database:\n{retrieval['answer']}\n"
                    f"User Question: {query}\n"
                    f"Refine and expand the deterministic analysis into a clear, authoritative executive answer "
                    f"with evidence numbers. Never invent work IDs or amounts not present in the analysis."
                )
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}",
                        json={"contents": [{"parts": [{"text": prompt}]}]}
                    )
                    if resp.status_code == 200:
                        res_json = resp.json()
                        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "answer": text,
                            "source": "Gemini 1.5 Flash API (real eSAKSHI context)",
                            "relevant_works": retrieval["rel_works"][:5]
                        }
            except Exception:
                pass

        return {
            "answer": retrieval["answer"],
            "source": "Local SQL Intelligence Engine (real eSAKSHI data)",
            "relevant_works": [
                {
                    "work_id": w.get("work_id"),
                    "description": w.get("work_description"),
                    "risk_score": w.get("risk_score"),
                    "risk_level": w.get("risk_level"),
                    "district": w.get("district")
                }
                for w in retrieval["rel_works"][:5]
            ]
        }
