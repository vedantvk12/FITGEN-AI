"""
Unit Tests for FITGEN AI Prompt Engine.
Verifies system directives, safety guardrails, and user constraint injection.
"""

from core.prompt_engine import PromptEngine
from models.workout_schema import WorkoutPreferences


def test_system_prompt_safety_directives():
    """Verify system prompt contains safety, no-diagnosis, and JSON rules."""
    sp = PromptEngine.SYSTEM_PROMPT
    assert "Never diagnose any disease" in sp
    assert "FITGEN AI" in sp
    assert "STRICT OPERATIONAL DIRECTIVES" in sp
    assert "valid, raw JSON" in sp


def test_user_workout_prompt_formatting():
    """Verify user constraints are accurately injected into generation prompt."""
    prefs = WorkoutPreferences(
        fitness_goal="Muscle Building",
        fitness_level="Intermediate",
        available_time=45,
        equipment=["Dumbbells", "Resistance Bands"],
        preferred_days_per_week=5,
        target_areas=["Upper Body", "Core"],
        limitations="Knee friendly",
        notes="Prefer short rest periods",
    )
    prompt = PromptEngine.build_workout_prompt(prefs)
    assert "Fitness Goal: Muscle Building" in prompt
    assert "Experience Level: Intermediate" in prompt
    assert "Target Daily Workout Duration: 45 minutes" in prompt
    assert "Dumbbells" in prompt
    assert "Resistance Bands" in prompt
    assert "Knee friendly" in prompt
    assert "Prefer short rest periods" in prompt
    assert "EXACT JSON OUTPUT SCHEMA REQUIRED" in prompt
    assert "schedule" in prompt


def test_tips_prompt_formatting():
    """Verify tips prompt requests structured JSON output."""
    prompt = PromptEngine.build_tips_prompt("Weight Management", "Beginner")
    assert "Weight Management" in prompt
    assert "Beginner" in prompt
    assert "tips" in prompt
    assert "valid JSON" in prompt
