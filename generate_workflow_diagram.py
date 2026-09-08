"""
Generate System Workflow Diagram for the MPLADS AI Anomaly & Risk Detection Platform.
Produces: system_workflow_diagram.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.patches import Polygon

# ---------- Canvas ----------
fig, ax = plt.subplots(figsize=(20, 15), dpi=200)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# ---------- Color palette ----------
NAVY   = "#0F172A"
BLUE   = "#2563EB"
SKY    = "#0EA5E9"
TEAL   = "#0D9488"
VIOLET = "#7C3AED"
AMBER  = "#D97706"
ORANGE = "#EA580C"
RED    = "#DC2626"
GREEN  = "#16A34A"
GRAY   = "#475569"
BG     = "#F1F5F9"
SOFT   = "#E2E8F0"
LINE   = "#94A3B8"

def box(x, y, w, h, text, fc=BLUE, tc="white", fs=10, bold=False,
        rounded=True, ec=None, lw=1.2, sub=None):
    """Draw a rounded rectangle labelled box. (x,y) is bottom-left."""
    style = "round,pad=0.02,rounding_size=0.5" if rounded else "square,pad=0.02"
    patch = FancyBboxPatch((x, y), w, h, boxstyle=style,
                           linewidth=lw, edgecolor=ec or fc,
                           facecolor=fc, zorder=2)
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    if sub:
        plt.text(x + w / 2, y + h - h * 0.32, text, ha="center", va="center",
                 fontsize=fs, color=tc, fontweight=weight, zorder=3)
        plt.text(x + w / 2, y + h * 0.24, sub, ha="center", va="center",
                 fontsize=fs - 2.6, color=tc, alpha=0.9, zorder=3)
    else:
        plt.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                 fontsize=fs, color=tc, fontweight=weight, zorder=3)
    return (x + w / 2, y + h)

def arrow(p1, p2, color=LINE, lw=1.8, style="-|>", pad="0,0"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=16,
                                 linewidth=lw, color=color,
                                 connectionstyle=f"arc3,rad=0", zorder=1))

def label(x, y, text, fs=8.5, color=GRAY, weight="normal", ha="center"):
    plt.text(x, y, text, ha=ha, va="center", fontsize=fs, color=color,
             fontweight=weight, zorder=4)

# =====================================================================
# TITLE
# =====================================================================
plt.text(50, 97.5, "MPLADS AI Anomaly & Risk Detection Platform", ha="center",
         fontsize=20, color=NAVY, fontweight="bold")
plt.text(50, 95.2, "End-to-End System Workflow  •  SIH 2026 — Problem Statement PS-102",
         ha="center", fontsize=11.5, color=GRAY)

# =====================================================================
# LAYER 1 — DATA INGESTION
# =====================================================================
label(8, 90.5, "DATA INGESTION", fs=9, color=NAVY, weight="bold", ha="left")
box(2, 84, 13, 5, "eSAKSHI / MPLADS\nReal CSV Dataset", fc=NAVY, fs=9, sub="14 files · 160MB")
box(17, 84, 12, 5, "Data Cleaning\n& Validation", fc=SKY, fs=9, sub="data_cleaning.py")
box(31, 84, 13, 5, "Data Integration\nMaster Project Table", fc=SKY, fs=9, sub="data_integration.py")
box(46, 84, 12, 5, "SQLite / PostgreSQL\nPersistent DB", fc=TEAL, fs=9, sub="db.py · schema.sql")
arrow((4, 84), (4, 82.5))
label(4, 82.6, "", fs=1)
box(46, 78.5, 12, 4, "GIS Spatial\nAnalysis (Stub)", fc=SKY, fs=9, sub="gis_analysis.py")
box(31, 78.5, 13, 4, "Agency / Contractor\nProfiling", fc=SKY, fs=9, sub="agency_profiler.py")
box(17, 78.5, 12, 4, "Feature\nEngineering", fc=SKY, fs=9, sub="feature_engineering.py")
arrow((38, 84), (38, 82.5))
arrow((8.5, 82.5), (8.5, 80.5))  # name conflict skip; handled in flow below

# =====================================================================
# LAYER 2 — ML DETECTION ENGINES (four parallel components)
# =====================================================================
label(8, 72.5, "ML DETECTION & COMPLIANCE INTELLIGENCE", fs=9, color=NAVY, weight="bold", ha="left")

engines = [
    (4,  "Rule Engine",            "rule_engine.py",     ORANGE, "Sanction/Expenditure\ndeviation rules"),
    (24, "Isolation Forest",       "train_isolation.py", VIOLET, "Unsupervised\nanomaly detection"),
    (44, "NLP Similarity",         "nlp_similarity.py",  AMBER,  "Duplicate work &\ncontractor detection"),
    (64, "Cost Benchmarking",      "risk_engine.py",     TEAL,   "Per-state / per-type\ncost baselines"),
    (83, "Agency Risk Profile",    "agency_profiler.py", RED,    "Historical risk\nscoring"),
]
for (x, name, mod, color, desc) in engines:
    box(x, 63.5, 15, 7.5, name, fc=color, fs=10, bold=True, sub=mod)
    bx = x + 7.5
    # multi-line sub-description
    plt.text(bx, 62.2, desc, ha="center", va="center", fontsize=8.2,
             color=NAVY, zorder=3)
    ax.add_patch(Polygon([[bx, 60.4], [bx - 0.8, 59.7], [bx + 0.8, 59.7]],
                         closed=True, color=color, zorder=2))

# =====================================================================
# LAYER 3 — FEATURE FUSION / RISK ENGINE
# =====================================================================
box(30, 52.5, 40, 7, "Composite Risk Fusion Engine (RiskEngine)", fc=BLUE,
    fs=11, bold=True, sub="Multi-signal fusion  •  anomaly + rule + NLP + cost + profile")
arrow((60, 52.5), (60, 51))

# =====================================================================
# LAYER 4 — EXPLANABLE OUTPUT
# =====================================================================
out = [
    (4,  "Explainable\n0–100 Risk Score",        RED,    "risk_engine.py"),
    (24, "Top Risk Reasons / Signals",           AMBER,  "explainable_alerts"),
    (44, "Data Quality Score",                   TEAL,   "data_audit"),
    (64, "Officer Review Queue",                 GREEN,  "officer_review"),
    (82, "Anomaly Alerts Feed",                  ORANGE, "risk_alerts"),
]
for (x, name, color, sub) in out:
    box(x, 45.5, 15, 6.5, name, fc=color, fs=9, bold=True, sub=sub)
    arrow((x + 7.5, 52.5), (x + 7.5, 52.0))

# =====================================================================
# LAYER 5 — PRESENTATION / API
# =====================================================================
label(8, 39.5, "DELIVERY & USER INTERFACE", fs=9, color=NAVY, weight="bold", ha="left")
app = [
    (2,  "FastAPI REST API", "backend/app/main.py", BLUE),
    (20, "Realtime Dashboards\n(Recharts)", "risk donut · pipeline", TEAL),
    (38, "Interactive Map\n(Leaflet / OSM)", "state-level view", GREEN),
    (56, "Investigation\nDrawer", "evidence drill-down", AMBER),
    (74, "LLM Copilot\nDecision Support", "llm_service.py", VIOLET),
]
for (x, name, sub, color) in app:
    box(x, 31.5, 15, 6, name, fc=color, fs=9, bold=True, sub=sub)
for (x, name, sub, color) in app:
    arrow((x + 7.5, 45.5), (x + 7.5, 37.5), color=color, lw=1.6)
# connect output row up to api
label(40, 29.4, "", fs=1)

# =====================================================================
# LAYER 6 — GOVERNMENT OFFICER DECISION LOOP
# =====================================================================
box(26, 24, 48, 6.5, "Government Officer Review & Decision Support", fc=GREEN,
    fs=10.5, bold=True, sub="Prioritized queue  •  Explainable evidence  •  Human-in-the-loop")
arrow((40, 24), (40, 22.2))

# Decision outcomes
box(24, 15.5, 24, 5.5, "Approve / Verify / Escalate", fc=TEAL, fs=9)
box(52, 15.5, 24, 5.5, "Flag for Further Investigation", fc=RED, fs=9)
arrow((34, 22.2), (34, 21))
arrow((52, 22.2), (62, 21))
arrow((64, 15.5), (64, 11))          # down to feedback loop
label(64, 13.5, "action recorded", fs=8, color=GRAY)

# =====================================================================
# FEEDBACK LOOP back to dataset
# =====================================================================
# feedback arrow from decision back to ingestion + model retraining
box(24, 6.5, 52, 4.5, "Continuous Feedback & Model Retraining Loop", fc=NAVY,
    fs=9.5, bold=True, sub="New evidence & officer decisions feed back to improve detection")
arrow((64, 6.5), (64, 4.6))
plt.text(64, 3.4, "enriched labels → re-run 11-stage pipeline → updated risk profiles",
         ha="center", fontsize=8, color=GRAY)

# feedback path along the left edge going up
arrow((25, 8.7), (4, 8.7), color=LINE, lw=1.4, style="-|>")
arrow((4, 8.7), (4, 80), color=LINE, lw=1.4, style="-|>")
arrow((4, 80), (4, 84), color=LINE, lw=1.4, style="-|>")

# =====================================================================
# Footer / Legend
# =====================================================================
plt.text(50, 1.6, "Human-in-the-loop: AI surfaces explainable signals;   Government officers make final compliance decisions.",
         ha="center", fontsize=9, color=GRAY)
plt.text(50, 0.6, "•  Real eSAKSHI data (131K recommended · 100K sanctioned works)   •  11-stage unsupervised ML pipeline   •  0–100 explainable risk score",
         ha="center", fontsize=8, color=LINE)

plt.tight_layout()
out = "system_workflow_diagram.png"
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved: {out}")
