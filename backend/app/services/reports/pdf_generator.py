"""
ExportIQ — ReportLab PDF Readiness Report Generator.
Generates a professional, structured PDF report for an assessment containing:
- MSME Profile summary
- Product and destination details
- Export Readiness Index (ERI) overall and category scores
- Compliance requirement results table
- Prioritized gap analysis and recommendations
- Official source references and disclaimers
"""
import io
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.msme_profile import MSMEProfile

logger = logging.getLogger(__name__)


def generate_assessment_pdf(assessment_id: int, db: Session) -> bytes:
    """
    Generate a PDF readiness report for the given assessment ID and return bytes.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise ValueError(f"Assessment {assessment_id} not found")

    user = assessment.user
    profile = db.query(MSMEProfile).filter(MSMEProfile.user_id == user.id).first()
    product = assessment.product
    destination = assessment.destination_country
    breakdown = assessment.score_breakdown or {}
    gaps = breakdown.get("gaps", [])
    recommendations = breakdown.get("recommendations", [])
    category_scores = assessment.category_scores or {}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    primary_color = colors.HexColor("#1d4ed8")  # brand-700
    text_dark = colors.HexColor("#1f2937")      # gray-800
    gray_light = colors.HexColor("#f3f4f6")     # gray-100
    accent_red = colors.HexColor("#dc2626")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=primary_color,
        fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6b7280"),
        fontName='Helvetica',
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=text_dark,
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=text_dark,
        fontName='Helvetica',
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor("#9ca3af"),
        fontName='Helvetica-Oblique',
    )

    story = []

    # Header
    story.append(Paragraph("ExportIQ — Export Readiness Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')} | Indicative Assessment # {assessment.id}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

    # Profile & Export Scope Table
    biz_name = profile.business_name if profile else user.full_name
    gstin = profile.gstin if profile and profile.gstin else "Not provided"
    iec = profile.iec_number if profile and profile.iec_number else "Not provided"

    meta_data = [
        [Paragraph("<b>Organization:</b>", body_style), Paragraph(biz_name, body_style),
         Paragraph("<b>Product:</b>", body_style), Paragraph(f"{product.name} (HS: {product.hs_code})", body_style)],
        [Paragraph("<b>GSTIN:</b>", body_style), Paragraph(gstin, body_style),
         Paragraph("<b>Destination:</b>", body_style), Paragraph(f"{destination.name} ({destination.iso_code})", body_style)],
        [Paragraph("<b>IEC Number:</b>", body_style), Paragraph(iec, body_style),
         Paragraph("<b>Evaluation Date:</b>", body_style), Paragraph(str(assessment.created_at.strftime('%Y-%m-%d')), body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[90, 160, 100, 180])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), gray_light),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ERI Score Banner
    eri = assessment.eri_score if assessment.eri_score is not None else 0.0
    score_data = [
        [
            Paragraph(f"<font size=28 color='#1d4ed8'><b>{eri:.1f}</b></font><font size=14 color='#6b7280'> / 100</font>", body_style),
            Paragraph("<b>Export Readiness Index (ERI)</b><br/><font size=8 color='#4b5563'>Indicative score evaluating legal, quality, and trade compliance. Not an official certification.</font>", body_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[130, 400])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # Category Scores
    if category_scores:
        story.append(Paragraph("Category Breakdown", h2_style))
        cat_rows = [[Paragraph("<b>Category</b>", body_style), Paragraph("<b>Score (%)</b>", body_style)]]
        for cat_key, score_val in category_scores.items():
            cat_rows.append([Paragraph(cat_key.replace('_', ' ').title(), body_style), Paragraph(f"{score_val}%", body_style)])
        cat_table = Table(cat_rows, colWidths=[350, 180])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), gray_light),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 14))

    # Requirement Results Table
    story.append(Paragraph("Compliance Requirements Evaluation", h2_style))
    req_rows = [[
        Paragraph("<b>Requirement</b>", body_style),
        Paragraph("<b>Category</b>", body_style),
        Paragraph("<b>Status</b>", body_style),
        Paragraph("<b>Explanation</b>", body_style),
    ]]

    for ar in assessment.requirement_results:
        req = ar.requirement
        status_str = ar.status.value.upper()
        status_color = "#16a34a" if ar.status.value == "compliant" else "#dc2626"
        req_rows.append([
            Paragraph(f"<b>{req.name}</b><br/><font size=7 color='#6b7280'>{req.code}</font>", body_style),
            Paragraph(req.category.replace('_', ' ').title(), body_style),
            Paragraph(f"<font color='{status_color}'><b>{status_str}</b></font>", body_style),
            Paragraph(ar.explanation or "—", body_style),
        ])

    req_table = Table(req_rows, colWidths=[150, 95, 80, 205])
    req_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), gray_light),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    story.append(req_table)
    story.append(Spacer(1, 14))

    # Recommendations & Gaps
    if recommendations:
        story.append(Paragraph("Prioritized Recommendations & Next Steps", h2_style))
        rec_rows = [[
            Paragraph("<b>Priority</b>", body_style),
            Paragraph("<b>Action Item</b>", body_style),
            Paragraph("<b>Issuing Authority / Source</b>", body_style),
        ]]
        for rec in recommendations:
            rec_rows.append([
                Paragraph(f"P{rec.get('priority', 1)}", body_style),
                Paragraph(rec.get('action', ''), body_style),
                Paragraph(f"{rec.get('issuing_authority', '—')}<br/><font size=7 color='#2563eb'>{rec.get('source_url', '')}</font>", body_style),
            ])
        rec_table = Table(rec_rows, colWidths=[55, 275, 200])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), gray_light),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 14))

    # Footer Disclaimer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db"), spaceAfter=8))
    story.append(Paragraph(
        "<b>Disclaimer:</b> ExportIQ is an academic decision-support tool. "
        "This report provides an indicative readiness assessment only and does not constitute official certification, legal approval, "
        "or a guarantee of export approval. All requirements and regulations should be verified directly with the relevant "
        "governmental authorities and trade professionals before undertaking export operations.",
        disclaimer_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
