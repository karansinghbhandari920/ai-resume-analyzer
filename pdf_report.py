"""
pdf_report.py
Builds a downloadable PDF summary of an analysis: ATS score + breakdown,
skill analysis, AI review, job match (if available), and suggestions.

Design note: unlike the app's dark "scan readout" theme, the PDF uses a
light background - reports like this usually get printed or skimmed in an
email client, where a near-black page wastes ink and reads poorly. The
mint/amber accent colors are reused at print-safe, slightly deeper shades
to keep the artifact visually tied to the product without the dark chrome.
"""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)

MINT = colors.HexColor("#1F9D6E")
AMBER = colors.HexColor("#B5790F")
INK = colors.HexColor("#1A1F26")
MUTED = colors.HexColor("#5B6470")
BORDER = colors.HexColor("#D8DEE4")


def _styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("ReportTitle", parent=base["Title"], textColor=INK, fontSize=22, spaceAfter=4))
    base.add(ParagraphStyle("ReportSub", parent=base["Normal"], textColor=MUTED, fontSize=10, spaceAfter=18))
    base.add(ParagraphStyle("SectionHead", parent=base["Heading2"], textColor=MINT, spaceBefore=16, spaceAfter=8))
    base.add(ParagraphStyle("Body", parent=base["Normal"], textColor=INK, fontSize=10.5, leading=15))
    base.add(ParagraphStyle("Muted", parent=base["Normal"], textColor=MUTED, fontSize=9))
    return base


def _score_color(score: float):
    if score >= 75:
        return MINT
    if score >= 50:
        return AMBER
    return colors.HexColor("#C13C4B")


def generate_pdf_report(analysis: dict) -> bytes:
    """analysis expects keys: resume_name, role, ats_score, score_breakdown,
    parsed_data, ai_review (optional dict), job_match (optional dict)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    styles = _styles()
    story = []

    # Header
    story.append(Paragraph("AI Resume Analyzer — Report", styles["ReportTitle"]))
    generated = datetime.now().strftime("%B %d, %Y")
    role = analysis.get("role") or "No role specified"
    story.append(Paragraph(
        f"{analysis.get('resume_name', 'Resume')}  ·  Target role: {role}  ·  Generated {generated}",
        styles["ReportSub"],
    ))

    # ATS Score
    score = analysis.get("ats_score", 0)
    score_color = _score_color(score)
    story.append(Paragraph("ATS Score", styles["SectionHead"]))
    score_table = Table([[f"{score:.0f} / 100"]], colWidths=[1.8 * inch])
    score_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 22),
        ("TEXTCOLOR", (0, 0), (-1, -1), score_color),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    breakdown = analysis.get("score_breakdown", {})
    if breakdown:
        rows = [["Component", "Score"]] + [[k, f"{v:.1f}"] for k, v in breakdown.items()]
        bt = Table(rows, colWidths=[3.5 * inch, 1.5 * inch])
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F4F7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), INK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(bt)

    # Skill analysis
    parsed = analysis.get("parsed_data", {}) or {}
    story.append(Paragraph("Skill Analysis", styles["SectionHead"]))
    skills = parsed.get("skills", [])
    story.append(Paragraph(", ".join(skills) if skills else "No skills detected.", styles["Body"]))

    # AI review
    ai_review = analysis.get("ai_review") or {}
    if ai_review:
        story.append(Paragraph("AI Review", styles["SectionHead"]))
        if ai_review.get("summary"):
            story.append(Paragraph(ai_review["summary"], styles["Body"]))
            story.append(Spacer(1, 6))
        for label, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses"),
                            ("Missing Skills", "missing_skills")]:
            items = ai_review.get(key) or []
            if items:
                story.append(Paragraph(label, ParagraphStyle("h4", parent=styles["Body"], fontName="Helvetica-Bold")))
                story.append(ListFlowable(
                    [ListItem(Paragraph(str(i), styles["Body"])) for i in items],
                    bulletType="bullet", leftIndent=14,
                ))
        if ai_review.get("recruiter_verdict"):
            story.append(Paragraph("Recruiter Verdict", ParagraphStyle("h4b", parent=styles["Body"], fontName="Helvetica-Bold")))
            story.append(Paragraph(ai_review["recruiter_verdict"], styles["Body"]))

    # Job match
    job_match = analysis.get("job_match")
    if job_match:
        story.append(Paragraph("Job Description Match", styles["SectionHead"]))
        story.append(Paragraph(f"Match score: {job_match.get('match_percent', 0)}%", styles["Body"]))
        if job_match.get("matching_skills"):
            story.append(Paragraph(
                "Matching skills: " + ", ".join(job_match["matching_skills"]), styles["Body"]
            ))
        if job_match.get("missing_keywords"):
            story.append(Paragraph(
                "Missing keywords: " + ", ".join(job_match["missing_keywords"]), styles["Body"]
            ))

    # Suggestions
    tips = analysis.get("tips") or (ai_review.get("improvement_suggestions") if ai_review else None)
    if tips:
        story.append(Paragraph("Suggestions", styles["SectionHead"]))
        story.append(ListFlowable(
            [ListItem(Paragraph(str(t), styles["Body"])) for t in tips],
            bulletType="bullet", leftIndent=14,
        ))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Generated by AI Resume Analyzer", styles["Muted"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
