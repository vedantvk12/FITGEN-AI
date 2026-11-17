"""
Unit Tests for FITGEN AI PDF Export Engine.
Verifies ReportLab generation, byte stream integrity, and PDF headers.
"""

from utils.export_pdf import generate_workout_pdf
from core.workout_generator import WorkoutGenerator
from models.workout_schema import WorkoutPreferences


def test_pdf_generation_valid_output():
    """Verify PDF export creates a valid non-empty PDF document."""
    generator = WorkoutGenerator()
    prefs = WorkoutPreferences(
        fitness_goal="Muscle Building",
        fitness_level="Beginner",
        available_time=30,
        equipment=["Dumbbells", "Yoga Mat"],
    )
    plan = generator.generate_evidence_based_plan(prefs)

    pdf_bytes = generate_workout_pdf(plan)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000, "PDF document size is smaller than expected."
    # Standard PDF magic header
    assert pdf_bytes.startswith(b"%PDF"), "Generated stream does not have a valid PDF header."


def test_pdf_generation_bodyweight_plan():
    """Verify PDF export handles bodyweight plans without external equipment cleanly."""
    generator = WorkoutGenerator()
    prefs = WorkoutPreferences(
        fitness_goal="Flexibility and Mobility",
        fitness_level="Beginner",
        available_time=20,
        equipment=["No Equipment (Bodyweight)"],
    )
    plan = generator.generate_evidence_based_plan(prefs)

    pdf_bytes = generate_workout_pdf(plan)
    assert len(pdf_bytes) > 4000
    assert pdf_bytes.startswith(b"%PDF")
