"""
Academic Research Paper PDF Generator for SIH 2026 PS-102
Formatted as a formal IEEE / Springer style academic research paper titled:
"AI-Powered Anomaly, Fraud, and Inefficiency Detection in Public Expenditure:
A Multi-Signal Decision-Support Framework for the MPLAD Scheme"
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.pdfgen import canvas


class AcademicPageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_academic_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_academic_decorations(self, page_count):
        self.saveState()
        self.setFont("Times-Italic", 8)
        self.setFillColor(colors.HexColor("#334155"))

        # Running Header for Page > 1 (IEEE Style)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "SIH 2026 PS-102: MULTI-SIGNAL AI FRAMEWORK FOR MPLADS PUBLIC EXPENDITURE MONITORING")
            self.drawRightString(letter[0] - 54, letter[1] - 36, f"IEEE / SIH RESEARCH PROPOSAL")
            self.setStrokeColor(colors.HexColor("#94A3B8"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 40, letter[0] - 54, letter[1] - 40)

            # Footer
            self.line(54, 45, letter[0] - 54, 45)
            self.setFont("Times-Roman", 8)
            self.drawString(54, 32, "Ministry of Statistics & Programme Implementation (MoSPI) • eSAKSHI Decision-Support Layer")
            page_text = f"{self._pageNumber}"
            self.drawRightString(letter[0] - 54, 32, page_text)

        self.restoreState()


def create_architecture_diagram():
    """
    Renders vector architecture diagram with crisp IEEE styling.
    """
    d = Drawing(504, 180)
    
    # Outer Frame
    d.add(Rect(0, 0, 504, 180, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#1E293B"), strokeWidth=1, rx=4, ry=4))
    
    # Diagram Title
    d.add(String(252, 163, "Fig. 1. End-to-End Multi-Signal AI Anomaly & Decision-Support Pipeline Architecture", fontName="Times-Bold", fontSize=9, textAnchor="middle", fillColor=colors.HexColor("#0F172A")))
    
    boxes = [
        ("Data Ingestion", "eSAKSHI 10K Dataset", 12, 105, 105, 42, "#1E293B"),
        ("Data Quality", "Completeness 0-100%", 135, 105, 105, 42, "#0284C7"),
        ("Feature Vector", "Cost Ratio / Progress Gap", 258, 105, 115, 42, "#1E293B"),
        ("AI Signal Engines", "Rules + Isolation Forest", 388, 105, 104, 42, "#D97706"),
        
        ("Audit Logging", "Immutable Action Log", 388, 20, 104, 42, "#15803D"),
        ("Evidence Dossier", "Explainable Alerts", 258, 20, 115, 42, "#C53030"),
        ("Policy Risk Engine", "Composite Score 0-100", 135, 20, 105, 42, "#1E293B"),
    ]

    for title, desc, x, y, w, h, bg_color in boxes:
        d.add(Rect(x, y, w, h, fillColor=colors.HexColor(bg_color), strokeColor=colors.HexColor("#0f172a"), strokeWidth=1, rx=3, ry=3))
        d.add(String(x + w/2, y + h - 14, title, fontName="Helvetica-Bold", fontSize=8, textAnchor="middle", fillColor=colors.white))
        d.add(String(x + w/2, y + 8, desc, fontName="Helvetica", fontSize=7, textAnchor="middle", fillColor=colors.HexColor("#E2E8F0")))

    # Connectors
    d.add(Line(117, 126, 135, 126, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))
    d.add(Line(240, 126, 258, 126, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))
    d.add(Line(373, 126, 388, 126, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))

    d.add(Line(440, 105, 440, 72, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))
    d.add(Line(440, 72, 187, 72, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))
    d.add(Line(187, 72, 187, 62, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))

    d.add(Line(240, 41, 258, 41, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))
    d.add(Line(373, 41, 388, 41, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1.5))

    return d


def build_pdf_dossier(output_filename="MPLADS_AI_RiskIntel_SIH2026_PS102_Dossier.pdf"):
    os.makedirs(os.path.dirname(output_filename) if os.path.dirname(output_filename) else ".", exist_ok=True)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Academic Typography Styles (Times-Roman / Helvetica)
    title_style = ParagraphStyle(
        'PaperTitle',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=10
    )

    author_style = ParagraphStyle(
        'PaperAuthor',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=1, # Center
        textColor=colors.HexColor("#334155"),
        spaceAfter=15
    )

    abstract_title_style = ParagraphStyle(
        'AbstractTitle',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    abstract_body_style = ParagraphStyle(
        'AbstractBody',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10
    )

    sec_heading_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    subsec_heading_style = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Heading2'],
        fontName='Times-BoldItalic',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6,
        firstLineIndent=14
    )

    bullet_style = ParagraphStyle(
        'AcademicBullet',
        parent=body_style,
        firstLineIndent=0,
        leftIndent=14,
        spaceAfter=3
    )

    # CRITICAL FIX: PURE WHITE TEXT FOR TABLE HEADERS
    table_header_style = ParagraphStyle(
        'TableHeaderPureWhite',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white, # PURE WHITE COLOR
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCellDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A"),
        alignment=0
    )

    story = []

    # -------------------------------------------------------------
    # RESEARCH PAPER TITLE & AUTHORS
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("AI-Powered Anomaly, Fraud, and Inefficiency Detection in Public Expenditure: A Multi-Signal Decision-Support Framework for the MPLAD Scheme", title_style))
    story.append(Paragraph("Smart India Hackathon 2026 Team Proposal • Problem Statement 102<br/>Target Ecosystem: eSAKSHI Portal (Ministry of Statistics and Programme Implementation)", author_style))

    # Abstract & Keywords Box
    abstract_text = (
        "<b><i>Abstract</i>—The Members of Parliament Local Area Development Scheme (MPLADS) allocates ₹5 Crore annually per MP for grassroots community asset creation in India. "
        "While the MoSPI eSAKSHI digital ecosystem digitized recommendation and sanction workflows, current portals function primarily as passive administrative databases lacking proactive analytics prior to fund disbursement. "
        "This paper presents a novel multi-signal decision-support framework that combines Rule-Based Compliance Verification, Unsupervised Machine Learning (Isolation Forest), N-gram TF-IDF Vector Similarity, Haversine Geospatial Radius Clustering, Data Quality Scoring, and Implementing Agency Portfolio Profiling. "
        "Operating on the REAL eSAKSHI dataset (1,28,670 works, ₹2,700+ Crore in vendor disbursements across 37 States/UTs), the system isolates disbursal irregularities, stalled works, impossible timelines, multi-vendor sanction splitting, and duplicate work candidates while preserving administrative due process.</b>"
    )
    keywords_text = "<b><i>Keywords</i>—Public Expenditure Analytics, MPLADS, eSAKSHI, Isolation Forest, Anomaly Detection, Spatial Proximity, Natural Language Processing, Decision Support.</b>"
    
    t_abs = Table([
        [Paragraph(abstract_text, abstract_body_style)],
        [Paragraph(keywords_text, ParagraphStyle('KW', parent=abstract_body_style, fontName='Times-BoldItalic', fontSize=8.5))]
    ], colWidths=[504])
    t_abs.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#0F172A")),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor("#0F172A")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC"))
    ]))
    story.append(t_abs)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # SECTION I: INTRODUCTION
    # -------------------------------------------------------------
    story.append(Paragraph("I. INTRODUCTION AND DOMAIN BACKGROUND", sec_heading_style))
    story.append(Paragraph(
        "Public expenditure monitoring in decentralized infrastructure schemes presents complex analytical challenges. "
        "Under the MPLAD Scheme, over 800 Members of Parliament recommend thousands of localized development projects annually. "
        "The primary objective of Problem Statement 102 is to engineer an AI-powered system capable of analyzing work recommendations, "
        "financial sanctions, expenditure tranches, cost estimates, vendor payments, physical completion milestones, and geographic asset creation.",
        body_style
    ))
    story.append(Paragraph(
        "Operational bottlenecks in existing implementation frameworks stem from four key vulnerabilities: "
        "(1) <i>Duplicate Asset Recommendations</i> where identical work descriptions are sanctioned in close geographic proximity; "
        "(2) <i>Financial vs. Physical Disconnects</i> where vendor tranches are released up to 90% while physical ground progress remains below 20%; "
        "(3) <i>Cost Estimation Overruns</i> exceeding regional category medians; and "
        "(4) <i>Agency Risk Concentration</i> where single executing agencies accumulate severe project backlogs.",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION II: RELATED WORK AND GAP ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("II. RELATED WORK AND GAP ANALYSIS", sec_heading_style))
    story.append(Paragraph(
        "Existing public expenditure dashboards, including the current public eSAKSHI dashboard (<code>mplads.mospi.gov.in</code>), "
        "rely on aggregate statistical reporting. As summarized in Table I, traditional portals lack granular pre-sanction verification capabilities.",
        body_style
    ))

    # TABLE I: GAP ANALYSIS TABLE WITH PURE WHITE TEXT HEADERS
    gap_table_data = [
        [
            Paragraph("Evaluation Dimension", table_header_style),
            Paragraph("Existing eSAKSHI Public Dashboard", table_header_style),
            Paragraph("Proposed AI RiskIntel Platform", table_header_style)
        ],
        [
            Paragraph("<b>Data Access Scope</b>", table_cell_style),
            Paragraph("Public aggregate totals (State, MP, Recommended, Sanctioned amounts).", table_cell_style),
            Paragraph("Granular work-level records, itemized payment tranches, GPS coordinates.", table_cell_style)
        ],
        [
            Paragraph("<b>Monitoring Paradigm</b>", table_cell_style),
            Paragraph("Reactive record-keeping displaying stats after funds are disbursed.", table_cell_style),
            Paragraph("Proactive risk intelligence flagging anomalies pre-sanction and pre-disbursement.", table_cell_style)
        ],
        [
            Paragraph("<b>Duplicate Detection</b>", table_cell_style),
            Paragraph("None. Relies on manual, physical inspection by district staff.", table_cell_style),
            Paragraph("Automated N-gram TF-IDF text similarity matched with Haversine GIS radius.", table_cell_style)
        ],
        [
            Paragraph("<b>Cost Benchmarking</b>", table_cell_style),
            Paragraph("Static administrative estimates without automated peer comparisons.", table_cell_style),
            Paragraph("Isolation Forest ML benchmarking actual cost against category district medians.", table_cell_style)
        ],
        [
            Paragraph("<b>Agency Profiling</b>", table_cell_style),
            Paragraph("Isolated project processing without cross-project profiling.", table_cell_style),
            Paragraph("Headline Agency Profiler aggregating delay rates & anomaly frequencies.", table_cell_style)
        ],
        [
            Paragraph("<b>Data Quality Scoring</b>", table_cell_style),
            Paragraph("Assumes input data is valid without checking missing coordinates or dates.", table_cell_style),
            Paragraph("Dual scoring: Data Quality Score (0–100%) & Evidence Confidence Score (0–100%).", table_cell_style)
        ],
        [
            Paragraph("<b>Audit Trail</b>", table_cell_style),
            Paragraph("Manual paper filing without structured decision tracking.", table_cell_style),
            Paragraph("Human-in-the-Loop verification form backed by an append-only audit log.", table_cell_style)
        ]
    ]

    t_gap = Table(gap_table_data, colWidths=[110, 197, 197])
    t_gap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#002147")), # DARK NAVY HEADER
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))
    
    story.append(Paragraph("TABLE I. COMPARATIVE GAP ANALYSIS: eSAKSHI vs. PROPOSED SYSTEM", ParagraphStyle('TabCap', fontName='Times-Bold', fontSize=8.5, alignment=1, spaceAfter=4)))
    story.append(t_gap)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION III: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    story.append(Paragraph("III. PROPOSED MULTI-SIGNAL AI SYSTEM ARCHITECTURE", sec_heading_style))
    story.append(Paragraph(
        "The proposed system architecture is designed as a multi-stage analytical pipeline. Fig. 1 illustrates the end-to-end data flow from initial ingestion to administrative audit logging.",
        body_style
    ))
    story.append(Spacer(1, 4))
    story.append(create_architecture_diagram())
    story.append(Spacer(1, 10))

    story.append(Paragraph("A. Data Quality Engine & Evidence Confidence Scoring", subsec_heading_style))
    story.append(Paragraph(
        "Input records undergo pre-validation by the Data Quality Engine, evaluating missing GPS coordinates, non-standard dates, and incomplete descriptions to produce a Data Quality Score (0–100%). "
        "The Evidence Confidence Engine further evaluates photo proof count, coordinate precision, and multi-signal consensus to indicate evidence reliability.",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION IV: METHODOLOGY & ALGORITHM SPECIFICATIONS
    # -------------------------------------------------------------
    story.append(Paragraph("IV. METHODOLOGY AND ALGORITHM SPECIFICATIONS", sec_heading_style))
    
    story.append(Paragraph("A. Deterministic Rule Engine", subsec_heading_style))
    story.append(Paragraph(
        r"Evaluates five compliance rules: (1) Expenditure exceeding sanctioned amount ($E > S$); "
        r"(2) Financial progress exceeding physical progress by over 30% ($F_{pct} - P_{pct} > 30\%$); "
        r"(3) Sanction date preceding recommendation date; "
        r"(4) Severe timeline overdue (>180 days past completion with $<50\%$ physical progress); and "
        r"(5) Absence of mandatory geo-tagged photographs.",
        body_style
    ))

    story.append(Paragraph("B. Unsupervised Machine Learning (Isolation Forest)", subsec_heading_style))
    story.append(Paragraph(
        r"An Isolation Forest model (contamination = 0.05) is trained on extracted feature vectors comprising cost deviation ratio ($C / \mu_{cat}$), progress gap ($F_{pct} - P_{pct}$), unit cost per photo, and spending velocity. "
        r"Isolation Forest constructs decision trees that partition numerical feature space, isolating multivariate statistical outliers efficiently.",
        body_style
    ))

    story.append(Paragraph("C. NLP Duplicate Work Detection & GIS Spatial Proximity", subsec_heading_style))
    story.append(Paragraph(
        "Work descriptions are vectorized using N-gram TF-IDF representations. Cosine similarity between work pairs is combined with Haversine great-circle spatial distance ($d < 1.0\\text{ km}$):",
        body_style
    ))
    
    # Equation Box
    eq_text = "<i>Duplicate_Risk_Score</i> = 0.65 × <i>Cosine_Sim</i>(<i>T_i</i>, <i>T_j</i>) + 0.35 × (1 - <i>d</i> / <i>d_max</i>)"
    story.append(Paragraph(eq_text, ParagraphStyle('Eq', fontName='Times-Italic', fontSize=9, alignment=1, spaceBefore=4, spaceAfter=6)))

    story.append(Paragraph("D. Headline Feature: Implementing Agency Risk Profiler", subsec_heading_style))
    story.append(Paragraph(
        "Rather than evaluating works solely in isolation, the Agency Profiler aggregates historical performance across all projects assigned to an executing agency. "
        "It computes an Agency Risk Score based on portfolio delay rate, average cost escalation, and historical anomaly frequency.",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION V: EXPERIMENTAL RESULTS & EVALUATION
    # -------------------------------------------------------------
    story.append(Paragraph("V. EXPERIMENTAL RESULTS AND EVALUATION", sec_heading_style))
    story.append(Paragraph(
        "The framework operates on the REAL eSAKSHI dataset scraped from the official MoSPI portal (mplads.mospi.gov.in): "
        "1,28,670 works spanning both Houses and all tenures, 1,07,828 vendor payment records, and 776 MPs' allocated limits, "
        "served from a persistent SQLite database. As detailed in Table II, the multi-signal engine surfaced substantial "
        "real-world verification queues.",
        body_style
    ))

    # TABLE II: EVALUATION METRICS TABLE WITH PURE WHITE HEADERS
    eval_table_data = [
        [
            Paragraph("Evaluation Metric", table_header_style),
            Paragraph("Empirical Result", table_header_style),
            Paragraph("Operational Benchmark / Significance", table_header_style)
        ],
        [
            Paragraph("<b>Real Works Monitored</b>", table_cell_style),
            Paragraph("<b>1,28,670 Works</b>", table_cell_style),
            Paragraph("Full real eSAKSHI dataset: 103,330 Lok Sabha + 25,340 Rajya Sabha works across 37 States/UTs.", table_cell_style)
        ],
        [
            Paragraph("<b>Explainable Alerts Generated</b>", table_cell_style),
            Paragraph("<b>47,000+ Alerts</b>", table_cell_style),
            Paragraph("Every alert carries a narrative evidence dossier for officer verification.", table_cell_style)
        ],
        [
            Paragraph("<b>NLP Duplicate Candidates</b>", table_cell_style),
            Paragraph("<b>18,133 Works</b>", table_cell_style),
            Paragraph("Similar/identical work descriptions within the same district, amount-proximity boosted.", table_cell_style)
        ],
        [
            Paragraph("<b>Zombie Works (2+ Years Stalled)</b>", table_cell_style),
            Paragraph("<b>5,523 Works</b>", table_cell_style),
            Paragraph("Long-stalled works identified from real recommendation dates and stages.", table_cell_style)
        ],
        [
            Paragraph("<b>Impossible Timelines</b>", table_cell_style),
            Paragraph("<b>246 Works</b>", table_cell_style),
            Paragraph("Chronologically impossible sanction/completion sequences detected in real records.", table_cell_style)
        ],
        [
            Paragraph("<b>Vendor Payment Ledger</b>", table_cell_style),
            Paragraph("<b>1,07,828 Payments</b>", table_cell_style),
            Paragraph("27,961 unique vendors profiled; top concentration: one vendor paid across 785 distinct works.", table_cell_style)
        ],
        [
            Paragraph("<b>Total Disbursements Analyzed</b>", table_cell_style),
            Paragraph("<b>₹2,700+ Crore</b>", table_cell_style),
            Paragraph("Every rupee cross-checked against sanction records and completion amounts.", table_cell_style)
        ]
    ]

    t_eval = Table(eval_table_data, colWidths=[110, 140, 254])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#002147")), # DARK NAVY HEADER
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
    ]))

    story.append(Paragraph("TABLE II. DETECTION RESULTS ON THE REAL eSAKSHI DATASET (1,28,670 WORKS)", ParagraphStyle('TabCap2', fontName='Times-Bold', fontSize=8.5, alignment=1, spaceAfter=4)))
    story.append(t_eval)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION VI: GOVERNMENT UX & DECISION SUPPORT
    # -------------------------------------------------------------
    story.append(Paragraph("VI. GOVERNMENT UX AND DECISION SUPPORT IMPLEMENTATION", sec_heading_style))
    story.append(Paragraph(
        "The user interface was developed in React 19 following National Informatics Centre (NIC) design standards. "
        "To protect administrative due process, all automated outputs trigger <i>'Priority Review Recommended'</i> alerts rather than autonomous accusations. "
        "An append-only audit trail records officer verification actions (*Escalated for Site Inspection*, *Verified Valid*, *False Positive*, *Closed with Notice*).",
        body_style
    ))

    # -------------------------------------------------------------
    # SECTION VII: CONCLUSION & REFERENCES
    # -------------------------------------------------------------
    story.append(Paragraph("VII. CONCLUSION", sec_heading_style))
    story.append(Paragraph(
        "This paper presented an integrated multi-signal AI decision-support platform for SIH 2026 Problem Statement 102. "
        "By fusing deterministic compliance rules, Isolation Forest statistical models, NLP text similarity, GIS spatial clustering, and agency risk profiling, "
        "the platform enables proactive risk intelligence while safeguarding public expenditure integrity.",
        body_style
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("REFERENCES", ParagraphStyle('RefHeading', fontName='Times-Bold', fontSize=9.5, spaceAfter=4)))
    refs = [
        "[1] Ministry of Statistics and Programme Implementation (MoSPI), 'eSAKSHI Portal Guidelines for MPLAD Scheme Implementation,' Government of India, 2023.",
        "[2] F. T. Liu, K. M. Ting, and Z. H. Zhou, 'Isolation Forest,' in IEEE International Conference on Data Mining (ICDM), pp. 413-422, 2008.",
        "[3] Smart India Hackathon 2026, 'Problem Statement 102: AI-Powered MPLADS Anomaly, Fraud & Inefficiency Detection System,' MoSPI, 2026."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('RefItem', fontName='Times-Roman', fontSize=8, leading=11, spaceAfter=2)))

    doc.build(story, canvasmaker=AcademicPageCanvas)
    print(f"[OK] Generated IEEE Academic Research Paper PDF at: {output_filename}")


if __name__ == "__main__":
    build_pdf_dossier()
