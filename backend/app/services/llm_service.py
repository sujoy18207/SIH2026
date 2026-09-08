"""
LLM RAG & Natural Language Investigation Assistant Service
Answers natural-language questions about real eSAKSHI works, risk alerts,
high-risk districts, agencies, and vendor concentration. Supports DeepSeek-V4-Flash
(via Makora inference), Google Gemini API, and a robust deterministic local
SQL-backed retriever as fallback.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx
from dotenv import load_dotenv

from app.db import get_connection

# Load environment variables from potential .env locations
load_dotenv()
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(_repo_root / ".env")
load_dotenv(_repo_root / "backend" / ".env")

logger = logging.getLogger("mplads.copilot")


class LLMCopilotService:
    def __init__(self):
        pass

    @property
    def deepseek_api_key(self) -> str:
        """Fetch DeepSeek / Makora API key."""
        return os.getenv("DEEPSEEK_API_KEY", "").strip()

    @property
    def deepseek_base_url(self) -> str:
        """Fetch DeepSeek / OpenAI-compatible base URL."""
        url = os.getenv("DEEPSEEK_BASE_URL", "https://inference.makora.com/v1").strip().rstrip("/")
        return url

    @property
    def deepseek_model(self) -> str:
        """Fetch DeepSeek model identifier."""
        return os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V4-Flash").strip()

    @property
    def gemini_api_key(self) -> str:
        """Dynamically fetch Gemini API key to support runtime environment changes."""
        return os.getenv("GEMINI_API_KEY", "").strip()

    @property
    def gemini_model(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()

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

            rel_works = [dict(r) for r in high_risk]
            answer = None

            # 1. Check for specific Work ID in query (e.g., 'work 80688', '80688', '10748')
            work_ids = re.findall(r'\b\d{4,8}\b', query)
            if work_ids:
                target_id = work_ids[0]
                work_row = conn.execute("SELECT * FROM works WHERE work_id=?", (target_id,)).fetchone()
                if work_row:
                    w = dict(work_row)
                    rel_works = [w]
                    alert_row = conn.execute("SELECT * FROM alerts WHERE work_id=?", (target_id,)).fetchone()
                    alert_info = dict(alert_row) if alert_row else {}

                    pmts = conn.execute(
                        "SELECT vendor_name, fund_disbursed_amt, expenditure_date FROM payments WHERE work_id=? ORDER BY fund_disbursed_amt DESC LIMIT 3",
                        (target_id,)
                    ).fetchall()
                    pmt_text = "\n".join(
                        [f"  - {p['vendor_name']}: ₹{p['fund_disbursed_amt']:,.0f} ({p['expenditure_date'] or 'N/A'})" for p in pmts]
                    ) if pmts else "  (No vendor disbursement records found)"

                    overrun_txt = ""
                    sanc = w.get("sanction_amount") or 0
                    disb = w.get("total_disbursed") or 0
                    if disb > sanc and sanc > 0:
                        overrun_txt = f"\n⚠️ **Cost Overrun Detected:** Disbursed exceeds Sanctioned by ₹{(disb - sanc):,.0f} ({(disb/sanc - 1)*100:.1f}% overrun)!"

                    narrative = (
                        alert_info.get("narrative_explanation")
                        or alert_info.get("narrative")
                        or "No statutory alert flagged for this specific work."
                    )
                    signals = alert_info.get("triggering_signals") or "Standard monitoring."
                    action = alert_info.get("recommended_action") or "Routine audit review."

                    answer = (
                        f"### Work Investigation Dossier: Work #{w.get('work_id')}\n"
                        f"- **Description:** {w.get('work_description') or 'N/A'}\n"
                        f"- **Location:** {w.get('district') or 'N/A'}, {w.get('state') or 'N/A'} ({w.get('constituency') or 'N/A'} constituency)\n"
                        f"- **MP / House:** {w.get('mp_name') or 'N/A'} ({w.get('house') or 'N/A'})\n"
                        f"- **Status / Stage:** {w.get('work_status') or 'N/A'} | Stage: {w.get('work_stage') or 'N/A'}\n"
                        f"- **Financials:** Sanctioned: ₹{sanc:,.0f} | Disbursed: ₹{disb:,.0f}{overrun_txt}\n"
                        f"- **Risk Assessment:** **{w.get('risk_level')}** (Score: **{w.get('risk_score')}/100**)\n\n"
                        f"**Alert Narrative:**\n{narrative}\n\n"
                        f"**Triggering Signals:** {signals}\n"
                        f"**Recommended Action:** {action}\n\n"
                        f"**Top Vendor Payments:**\n{pmt_text}"
                    )
                    return {"answer": answer, "rel_works": rel_works, "total_works": total_works}

            # 2. Check for State and District directly (prioritize longer name match)
            matched_district = None
            matched_state = None

            # Collect states and districts sorted by length descending so e.g. "West Bengal" matches before "West"
            states = [r[0] for r in conn.execute("SELECT DISTINCT state FROM works WHERE state IS NOT NULL").fetchall()]
            dist_rows = conn.execute("SELECT DISTINCT district, state FROM works WHERE district IS NOT NULL").fetchall()

            # Check states first (or whichever has a longer match in the query)
            best_state_match = None
            for s in sorted(states, key=lambda x: len(x) if x else 0, reverse=True):
                if s and len(s) >= 3 and s.lower() in q_lower:
                    best_state_match = s
                    break

            best_dist_match = None
            best_dist_state = None
            for r in sorted(dist_rows, key=lambda x: len(x["district"]) if x["district"] else 0, reverse=True):
                d_name = r["district"]
                if d_name and len(d_name) >= 3 and d_name.lower() in q_lower:
                    best_dist_match = d_name
                    best_dist_state = r["state"]
                    break

            # If district match is longer or more specific within the state
            if best_dist_match and best_state_match:
                # If district belongs to the matched state, use district
                if best_dist_state == best_state_match:
                    matched_district = best_dist_match
                    matched_state = best_state_match
                elif len(best_dist_match) > len(best_state_match):
                    matched_district = best_dist_match
                    matched_state = best_dist_state
                else:
                    matched_state = best_state_match
            elif best_dist_match:
                matched_district = best_dist_match
                matched_state = best_dist_state
            elif best_state_match:
                matched_state = best_state_match

            # Build district / state response
            if matched_district and matched_state:
                dist_stats = conn.execute(
                    "SELECT COUNT(*), COALESCE(SUM(sanction_amount),0), COALESCE(SUM(total_disbursed),0) "
                    "FROM works WHERE state=? AND district=?", (matched_state, matched_district)).fetchone()
                dist_high = conn.execute(
                    "SELECT COUNT(*) FROM works WHERE state=? AND district=? AND risk_level IN ('High','Critical')",
                    (matched_state, matched_district)).fetchone()[0]
                answer = (
                    f"### District Risk Profile: **{matched_district}, {matched_state}** (real eSAKSHI data)\n"
                    f"- **Total Works Monitored:** **{dist_stats[0]:,}**\n"
                    f"- **Sanctioned Amount:** ₹{dist_stats[1]/1e7:,.2f} Cr\n"
                    f"- **Disbursed Amount:** ₹{dist_stats[2]/1e7:,.2f} Cr\n"
                    f"- **High / Critical Risk Flags:** **{dist_high}** works requiring verification.\n\n"
                    f"Below are the top flagged anomaly records in {matched_district}."
                )
                rel_works = [dict(r) for r in conn.execute(
                    "SELECT work_id, work_description, risk_score, risk_level, district, state FROM works "
                    "WHERE state=? AND district=? ORDER BY risk_score DESC LIMIT 5",
                    (matched_state, matched_district)).fetchall()]

            elif matched_state:
                state_stats = conn.execute(
                    "SELECT COUNT(*), COALESCE(SUM(sanction_amount),0), COALESCE(SUM(total_disbursed),0) "
                    "FROM works WHERE state=?", (matched_state,)).fetchone()
                state_high = conn.execute(
                    "SELECT COUNT(*) FROM works WHERE state=? AND risk_level IN ('High','Critical')",
                    (matched_state,)).fetchone()[0]
                answer = (
                    f"### State Risk Profile: **{matched_state}** (real eSAKSHI data)\n"
                    f"- **Total Works Monitored:** **{state_stats[0]:,}**\n"
                    f"- **Sanctioned Amount:** ₹{state_stats[1]/1e7:,.2f} Cr\n"
                    f"- **Disbursed Amount:** ₹{state_stats[2]/1e7:,.2f} Cr\n"
                    f"- **High / Critical Risk Works:** **{state_high}**\n\n"
                    f"You can ask about a specific district in {matched_state} for local drill-down analysis."
                )
                rel_works = [dict(r) for r in conn.execute(
                    "SELECT work_id, work_description, risk_score, risk_level, district, state FROM works "
                    "WHERE state=? ORDER BY risk_score DESC LIMIT 5", (matched_state,)).fetchall()]

            # 4. Implementing Agency Risk (fixed: agencies table does not have 'state')
            elif "agency" in q_lower or "ida" in q_lower or "authority" in q_lower:
                top_agencies = conn.execute(
                    "SELECT agency_name, district, total_works, delayed_works, anomaly_count, agency_risk_score, agency_risk_level "
                    "FROM agencies ORDER BY agency_risk_score DESC LIMIT 5").fetchall()
                n_agencies = conn.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
                agency_lines = "\n".join(
                    f"  - **{a['agency_name']}** ({a['district'] or 'N/A'}): {a['total_works']} works, {a['delayed_works']} delayed, risk **{a['agency_risk_score']}/100** ({a['agency_risk_level']})"
                    for a in top_agencies
                )
                answer = (
                    f"### Implementing Agency (IDA) Risk Profiling\n"
                    f"Evaluated **{n_agencies}** District Authorities across real eSAKSHI data.\n\n"
                    f"**Highest-Risk Authorities:**\n{agency_lines}\n\n"
                    f"Authorities with delay rates >50% and recurring cost deviations trigger priority pre-sanction inspection alerts."
                )

            # 5. Vendor Concentration / Contractor Nexus
            elif "vendor" in q_lower or "contractor" in q_lower or "nexus" in q_lower:
                top_vendors = conn.execute(
                    "SELECT vendor_name, work_count, total_disbursed, district_count, state_count "
                    "FROM vendors ORDER BY work_count DESC LIMIT 5").fetchall()
                n_vendors = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()[0]
                vendor_lines = "\n".join(
                    f"  - **{v['vendor_name']}**: awarded **{v['work_count']} distinct works** across "
                    f"{v['district_count']} district(s), total payout **₹{v['total_disbursed']/1e7:,.2f} Cr**"
                    for v in top_vendors
                )
                answer = (
                    f"### Vendor Concentration & Nexus Detection\n"
                    f"Analyzed **1,07,828 payments** across **{n_vendors}** unique vendors in the expenditure ledger.\n\n"
                    f"**Top Disbursal & Concentration Vendors:**\n{vendor_lines}\n\n"
                    f"Entities winning hundreds of works across multiple districts are prioritized for procurement collusion audits."
                )

            # 6. Duplicate Works / Ghost Projects
            elif "duplicate" in q_lower or "ghost" in q_lower or "identical" in q_lower:
                dup_alerts = conn.execute(
                    "SELECT work_id, work_title, district, state, duplicate_risk_score, duplicate_candidate_id "
                    "FROM alerts WHERE duplicate_candidate_id IS NOT NULL ORDER BY duplicate_risk_score DESC LIMIT 5").fetchall()
                n_dup = conn.execute(
                    "SELECT COUNT(*) FROM alerts WHERE duplicate_candidate_id IS NOT NULL").fetchone()[0]
                dup_lines = "\n".join(
                    f"  - Work #{d['work_id']} ({d['district']}, {d['state']}) ↔ Candidate #{d['duplicate_candidate_id']} (similarity: **{d['duplicate_risk_score']}%**)"
                    for d in dup_alerts
                )
                answer = (
                    f"### NLP Duplicate Work Detection\n"
                    f"Detected **{n_dup}** works with high textual similarity (TF-IDF cosine ≥ 0.85) in the same district.\n\n"
                    f"**Top Suspected Duplicate Pairs:**\n{dup_lines or '  (none)'}\n\n"
                    f"These works represent potential double-billing or re-sanctioning of existing infrastructure."
                )

            # 7. Financial Overrun / Cost Deviations / Budget
            elif any(w in q_lower for w in ["overrun", "excess", "disburs", "cost", "sanction", "budget", "amount"]):
                top_cost = conn.execute(
                    "SELECT work_id, work_description, district, state, sanction_amount, total_disbursed, risk_level, risk_score "
                    "FROM works ORDER BY sanction_amount DESC LIMIT 5"
                ).fetchall()
                cost_lines = "\n".join(
                    f"  - Work #{r['work_id']} ({r['district']}, {r['state']}): Sanctioned ₹{r['sanction_amount']:,.0f} | Disbursed ₹{r['total_disbursed']:,.0f} | Risk: {r['risk_level']} ({r['risk_score']}/100)"
                    for r in top_cost
                )
                answer = (
                    f"### Financial Allocation & Cost Intelligence\n"
                    f"Total Scheme Financials: **₹{total_sanctioned/1e7:,.1f} Cr Sanctioned** across **{total_works:,} works**.\n\n"
                    f"**Highest Sanctioned Infrastructure Works:**\n{cost_lines}\n\n"
                    f"Under MPLADS guidelines, administrative sanctions exceeding threshold limits require high-level state vigilance monitoring."
                )

            # 8. Project Stages & Status Breakdown
            elif "status" in q_lower or "completed" in q_lower or "progress" in q_lower or "pending" in q_lower:
                status_counts = conn.execute(
                    "SELECT work_status, COUNT(*), COALESCE(SUM(total_disbursed),0) FROM works GROUP BY work_status"
                ).fetchall()
                lines = [f"- **{r[0] or 'Unspecified'}:** {r[1]:,} works (Disbursed: ₹{r[2]/1e7:,.1f} Cr)" for r in status_counts]
                answer = (
                    f"### MPLADS Project Pipeline Status (1,28,670 Works)\n"
                    + "\n".join(lines) + "\n\n"
                    f"Works stalled for >180 days past completion deadline are automatically assigned High/Critical timeline anomaly weights."
                )

            # 9. MP Allocations & Member of Parliament info
            elif "mp" in q_lower or "parliament" in q_lower or "allocated" in q_lower or "limit" in q_lower:
                top_alloc = conn.execute(
                    "SELECT mp_name, house, state, constituency, allocated_amount FROM mp_allocations ORDER BY allocated_amount DESC LIMIT 5"
                ).fetchall()
                mp_lines = "\n".join(
                    f"  - **{m['mp_name']}** ({m['house']}, {m['state']}): ₹{m['allocated_amount']:,.0f}"
                    for m in top_alloc
                )
                answer = (
                    f"### MP Allocated Limits (774 Members of Parliament)\n"
                    f"Tracks statutory allocated entitlements across Lok Sabha and Rajya Sabha.\n\n"
                    f"**Sample Allocations:**\n{mp_lines}\n\n"
                    f"Every work recommended is cross-referenced against the MP's allocated balance."
                )

            # 10. Platform / Methodology / AI Architecture
            elif any(w in q_lower for w in ["how does", "what is this", "who are you", "algorithm", "model", "methodology", "pipeline", "isolation forest", "architecture"]):
                answer = (
                    f"### About MPLADS AI Risk Intelligence Platform (SIH 2026, PS-102)\n"
                    f"I am **सक्षम AI**, an explainable decision-support copilot monitoring **1,28,670 real eSAKSHI works**.\n\n"
                    f"**Our 5-Signal Fusion Algorithm (0–100 Risk Score):**\n"
                    f"- **35% Statutory Rules Engine:** Flags expenditure exceeding sanction, missing photos, impossible timelines.\n"
                    f"- **25% Isolation Forest (Unsupervised ML):** Multivariate anomaly detection on cost ratio, spending velocity, progress gap.\n"
                    f"- **20% NLP Text Similarity:** TF-IDF cosine matching detecting duplicate/ghost projects.\n"
                    f"- **10% Timeline Velocity:** Delays >180 days past expected completion.\n"
                    f"- **10% Implementing Agency Risk:** Historical delay and anomaly rates of executing authorities.\n\n"
                    f"Every flagged work provides an explainable evidence dossier for officer verification."
                )

            # 11. General High-Risk Anomaly Query
            elif any(w in q_lower for w in ["high risk", "critical", "anomal", "alert", "risk"]):
                n_high = conn.execute("SELECT COUNT(*) FROM works WHERE risk_level IN ('High','Critical')").fetchone()[0]
                sample_ids = [w["work_id"] for w in high_risk[:5]]
                answer = (
                    f"### High-Risk Anomaly Summary (real eSAKSHI dataset)\n"
                    f"Out of **{total_works:,}** monitored works, the multi-signal AI engine identified **{n_high:,} high/critical risk works**.\n\n"
                    f"- **Top Priority Work IDs:** {', '.join([f'#{wid}' for wid in sample_ids])}\n"
                    f"- **Primary Triggers:** Vendor disbursal > sanctioned amount, duplicate descriptions within district, and stalled works.\n\n"
                    f"Ask about any specific Work ID (e.g. `work {sample_ids[0]}`) or state/district for an in-depth breakdown."
                )

            # 12. Dynamic Keyword Search (Search work descriptions, categories, or MP names)
            else:
                keywords = [w for w in re.findall(r'[a-zA-Z]{4,}', q_lower) if w not in {
                    'show', 'find', 'what', 'which', 'tell', 'about', 'from', 'with', 'this', 'that', 'have', 'highest', 'lowest', 'most', 'least', 'where', 'when', 'does', 'please', 'help'
                }]
                matched_works = []
                if keywords:
                    clauses = " OR ".join(["work_description LIKE ? OR work_category LIKE ? OR mp_name LIKE ?" for _ in keywords[:3]])
                    params = []
                    for kw in keywords[:3]:
                        params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
                    matched_works = conn.execute(
                        f"SELECT work_id, work_description, risk_score, risk_level, district, state, sanction_amount, total_disbursed "
                        f"FROM works WHERE ({clauses}) ORDER BY risk_score DESC LIMIT 5",
                        tuple(params)
                    ).fetchall()

                if matched_works:
                    rel_works = [dict(r) for r in matched_works]
                    rows_txt = "\n".join([
                        f"  - Work #{r['work_id']} ({r['district']}, {r['state']}): {r['work_description']} (Risk: **{r['risk_level']}**, Sanction: ₹{r['sanction_amount']:,.0f})"
                        for r in matched_works
                    ])
                    answer = (
                        f"### Database Search Results matching '{' '.join(keywords[:3])}':\n"
                        f"Found matching records in the 1,28,670 eSAKSHI works dataset:\n\n"
                        f"{rows_txt}\n\n"
                        f"Ask about any specific Work ID for complete forensic evidence."
                    )
                else:
                    answer = (
                        f"### MPLADS Risk Intelligence Assistant (real eSAKSHI data)\n"
                        f"- **Works Monitored:** **{total_works:,}** works across all 37 States & UTs\n"
                        f"- **Financial Scope:** ₹{total_sanctioned/1e7:,.0f} Cr Sanctioned | ₹{total_disbursed/1e7:,.0f} Cr Disbursed\n"
                        f"- **Active Explainable Alerts:** **{total_alerts:,}** Priority Review items\n\n"
                        f"💡 **Suggested Questions:**\n"
                        f"- *'Show high-risk works in West Bengal'*\n"
                        f"- *'Investigate work 80688'*\n"
                        f"- *'Which vendors receive the most payments?'*\n"
                        f"- *'Which implementing agencies have severe delay risk?'*\n"
                        f"- *'How does the AI detection algorithm work?'*"
                    )

            return {"answer": answer, "rel_works": rel_works, "total_works": total_works}
        finally:
            conn.close()

    async def _call_deepseek(self, prompt: str) -> Optional[str]:
        """Calls DeepSeek-V4-Flash via Makora or OpenAI-compatible endpoint."""
        api_key = self.deepseek_api_key
        if not api_key:
            return None

        url = f"{self.deepseek_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.deepseek_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are सक्षम AI, the official AI Risk Intelligence & Anomaly Detection Copilot "
                        "for the MPLADS scheme (monitoring 1,28,670 real eSAKSHI works, Smart India Hackathon 2026, PS-102).\n"
                        "Use the provided database context to directly, accurately, and authoritatively answer the user's question.\n"
                        "Rules:\n"
                        "1. Answer concisely and professionally using markdown with bold statistics.\n"
                        "2. Never hallucinate works, figures, or locations not present in the database context.\n"
                        "3. If the user asks a general question about MPLADS or scheme rules, answer with domain expertise."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 800,
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {})
                        content = msg.get("content")
                        if content and content.strip():
                            return content.strip()
                else:
                    logger.warning(f"DeepSeek/Makora returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"DeepSeek/Makora API call failed: {e}")

        return None

    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """Fallback to Google Gemini API if configured."""
        api_key = self.gemini_api_key
        if not api_key:
            return None

        models = [self.gemini_model, "gemini-2.0-flash", "gemini-1.5-flash"]
        for m in list(dict.fromkeys(models)):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={"contents": [{"parts": [{"text": prompt}]}]}
                    )
                    if resp.status_code == 200:
                        candidates = resp.json().get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            text = candidates[0]["content"]["parts"][0]["text"]
                            return text.strip()
            except Exception as e:
                logger.warning(f"Gemini API request failed for {m}: {e}")

        return None

    async def answer_investigation_query(self, query: str) -> Dict[str, Any]:
        """Retrieves relevant evidence from real eSAKSHI data and enriches via DeepSeek-V4-Flash LLM."""
        retrieval = self._retrieve(query)
        evidence_context = retrieval.get("answer", "")

        user_prompt = (
            f"DATABASE RETRIEVAL CONTEXT:\n{evidence_context}\n\n"
            f"USER QUESTION: {query}\n\n"
            f"Please provide an executive, explainable answer based on the real eSAKSHI data above."
        )

        relevant_works = [
            {
                "work_id": w.get("work_id"),
                "description": w.get("work_description"),
                "risk_score": w.get("risk_score"),
                "risk_level": w.get("risk_level"),
                "district": w.get("district")
            }
            for w in retrieval.get("rel_works", [])[:5]
        ]

        # 1. Primary: DeepSeek-V4-Flash via Makora
        deepseek_res = await self._call_deepseek(user_prompt)
        if deepseek_res:
            return {
                "answer": deepseek_res,
                "source": "DeepSeek-V4-Flash (Makora) + Real eSAKSHI SQL Engine",
                "relevant_works": relevant_works
            }

        # 2. Secondary: Gemini (if configured)
        gemini_res = await self._call_gemini(user_prompt)
        if gemini_res:
            return {
                "answer": gemini_res,
                "source": "Gemini AI + Real eSAKSHI SQL Engine",
                "relevant_works": relevant_works
            }

        # 3. Deterministic Local SQL Engine fallback
        source_note = "Local SQL Intelligence Engine"
        if self.deepseek_api_key:
            source_note += " (DeepSeek API unreachable; showing real eSAKSHI data)"
        else:
            source_note += " (Offline mode)"

        return {
            "answer": retrieval["answer"],
            "source": source_note,
            "relevant_works": relevant_works
        }
