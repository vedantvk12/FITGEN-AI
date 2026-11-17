"""
PDF Export Module for FITGEN AI using ReportLab.
Generates an executive-grade, multi-page fitness routine dossier.
"""

import io
from typing import Union
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from models.workout_schema import WeeklyWorkoutPlan
from config.settings import settings


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total pages and render running academic header/footer."""

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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(
            36,
            756,
            f"FITGEN AI — {settings.APP_SUBTITLE} | Problem Statement {settings.ACADEMIC_PROBLEM_STMT}",
        )
        self.drawRightString(
            576,
            756,
            f"Student: {settings.ACADEMIC_STUDENT} (Roll: {settings.ACADEMIC_ROLL})",
        )
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 750, 576, 750)

        # Running Footer
        self.line(36, 40, 576, 40)
        self.drawString(
            36,
            28,
            "CONFIDENTIAL & PERSONALIZED FITNESS PLAN — For Educational & Academic Evaluation",
        )
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_text)
        self.restoreState()


def generate_workout_pdf(plan: WeeklyWorkoutPlan) -> bytes:
    """Generate a PDF document for a WeeklyWorkoutPlan and return raw bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0D9488"),
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SecHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=6,
    )

    day_heading = ParagraphStyle(
        "DayHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )

    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    table_header_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # Title Block
    story.append(Paragraph(f"FITGEN AI — {plan.plan_title}", title_style))
    story.append(
        Paragraph(
            f"Personalized 7-Day Routine | Goal: <b>{plan.fitness_goal}</b> | Level: <b>{plan.fitness_level}</b> | Generated on: {plan.created_at[:10]}",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    # Academic Project Context Box
    academic_data = [
        [
            Paragraph("<b>Academic Project:</b> Problem Statement 55", meta_label),
            Paragraph(f"<b>Student:</b> {settings.ACADEMIC_STUDENT} (Roll: {settings.ACADEMIC_ROLL})", meta_label),
            Paragraph(f"<b>Class:</b> {settings.ACADEMIC_CLASS}", meta_label),
        ]
    ]
    academic_table = Table(academic_data, colWidths=[180, 180, 180])
    academic_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(academic_table)
    story.append(Spacer(1, 8))

    # Profile & Summary Card Table
    eq_str = ", ".join(plan.equipment) if plan.equipment else "Bodyweight / No Equipment"
    summary_data = [
        [
            Paragraph("<b>Target Goal:</b>", meta_label),
            Paragraph(plan.fitness_goal, meta_val),
            Paragraph("<b>Training Days:</b>", meta_label),
            Paragraph(f"{plan.weekly_summary.total_workout_days} days / week", meta_val),
        ],
        [
            Paragraph("<b>Experience Level:</b>", meta_label),
            Paragraph(plan.fitness_level, meta_val),
            Paragraph("<b>Recovery Days:</b>", meta_label),
            Paragraph(f"{plan.weekly_summary.total_recovery_days} days / week", meta_val),
        ],
        [
            Paragraph("<b>Daily Duration:</b>", meta_label),
            Paragraph(f"{plan.daily_time_minutes} minutes", meta_val),
            Paragraph("<b>Estimated Total Time:</b>", meta_label),
            Paragraph(f"{plan.weekly_summary.estimated_total_minutes} mins / week", meta_val),
        ],
        [
            Paragraph("<b>Equipment:</b>", meta_label),
            Paragraph(eq_str, meta_val),
            Paragraph("<b>Split Methodology:</b>", meta_label),
            Paragraph(plan.weekly_summary.split_type, meta_val),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[110, 160, 120, 150])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 7-Day Schedule Breakdown
    story.append(Paragraph("Weekly Periodized Schedule (7 Days)", section_heading))

    for day in plan.schedule:
        day_elements = []

        is_training = day.day_type.lower() == "training"
        header_color = colors.HexColor("#0F766E") if is_training else colors.HexColor("#475569")
        badge_text = "TRAINING SESSION" if is_training else ("ACTIVE RECOVERY" if "recov" in day.day_type.lower() else "REST DAY")

        # Day Header Bar
        day_bar_data = [
            [
                Paragraph(f"<b>Day {day.day_number}: {day.day_name} — {day.focus}</b>", ParagraphStyle("DBH", parent=day_heading, textColor=colors.white)),
                Paragraph(f"<b>{badge_text}</b> ({day.estimated_minutes} min)", ParagraphStyle("DBR", parent=day_heading, alignment=2, textColor=colors.white)),
            ]
        ]
        day_bar = Table(day_bar_data, colWidths=[380, 160])
        day_bar.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), header_color),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        day_elements.append(day_bar)

        # Warmup and Cooldown info
        if day.warmup and day.warmup.activities:
            warmup_acts = ", ".join(day.warmup.activities)
            warmup_p = Paragraph(f"<b>Warm-up ({day.warmup.duration_minutes}m):</b> {warmup_acts}. <i>{day.warmup.instructions}</i>", body_style)
            day_elements.append(Spacer(1, 2))
            day_elements.append(warmup_p)

        # Exercise Table
        if day.exercises:
            ex_rows = [
                [
                    Paragraph("Exercise", table_header_style),
                    Paragraph("Target Muscle", table_header_style),
                    Paragraph("Sets", table_header_style),
                    Paragraph("Reps/Dur", table_header_style),
                    Paragraph("Rest", table_header_style),
                    Paragraph("Instructions & Form Cue", table_header_style),
                ]
            ]

            for ex in day.exercises:
                tip_text = f"<br/><b>Tip:</b> {ex.beginner_tip}" if ex.beginner_tip else ""
                cue_text = f"<br/><b>Form Cue:</b> {ex.form_cue}" if ex.form_cue else ""
                full_instr = f"{ex.instructions}{tip_text}{cue_text}"

                ex_rows.append([
                    Paragraph(f"<b>{ex.name}</b>", table_cell_style),
                    Paragraph(ex.muscle_group, table_cell_style),
                    Paragraph(str(ex.sets), table_cell_style),
                    Paragraph(ex.reps_or_duration, table_cell_style),
                    Paragraph(f"{ex.rest_seconds}s", table_cell_style),
                    Paragraph(full_instr, table_cell_style),
                ])

            ex_table = Table(ex_rows, colWidths=[105, 95, 30, 60, 35, 215])
            ex_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 3),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ])
            )
            day_elements.append(Spacer(1, 3))
            day_elements.append(ex_table)
        else:
            # Rest day message
            day_elements.append(Spacer(1, 3))
            rest_p = Paragraph(f"<i>Active Rest Protocol: Focus on full cellular recovery, gentle hydration, light walking, or mobility work.</i>", body_style)
            day_elements.append(rest_p)

        # Cooldown and recovery
        if day.cooldown and day.cooldown.activities:
            cd_acts = ", ".join(day.cooldown.activities)
            cd_p = Paragraph(f"<b>Cool-down ({day.cooldown.duration_minutes}m):</b> {cd_acts}. <i>{day.cooldown.instructions}</i>", body_style)
            day_elements.append(Spacer(1, 2))
            day_elements.append(cd_p)

        if day.recovery_recommendation:
            rec_p = Paragraph(f"<b>Daily Recovery Strategy:</b> {day.recovery_recommendation}", body_style)
            day_elements.append(Spacer(1, 2))
            day_elements.append(rec_p)

        day_elements.append(Spacer(1, 8))
        story.append(KeepTogether(day_elements))

    # General Recommendations Block
    story.append(Spacer(1, 6))
    story.append(Paragraph("Evidence-Based Lifestyle & Safety Recommendations", section_heading))

    recs = plan.general_recommendations
    rec_items = [
        Paragraph(f"<b>Hydration:</b> {recs.hydration_tip}", body_style),
        Paragraph(f"<b>Sleep & Neuro-Recovery:</b> {recs.sleep_and_recovery}", body_style),
        Paragraph(f"<b>Progressive Overload Strategy:</b> {recs.progressive_overload_advice}", body_style),
    ]

    for r in recs.nutrition_guidelines:
        rec_items.append(Paragraph(f"• <b>Nutrition:</b> {r}", body_style))

    for item in rec_items:
        story.append(item)
        story.append(Spacer(1, 2))

    # Safety Advisory
    story.append(Spacer(1, 6))
    safety_box = [
        [
            Paragraph(
                f"<b>CLINICAL & SAFETY NOTICE:</b> {recs.safety_warning} FITGEN AI is developed solely for academic research and personal demonstration.",
                ParagraphStyle("SafetyP", parent=body_style, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#991B1B")),
            )
        ]
    ]
    safety_table = Table(safety_box, colWidths=[540])
    safety_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F87171")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(safety_table)

    # Build PDF with dynamic header/footer
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
