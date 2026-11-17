"""
Unit Tests for FITGEN AI Validators and Input Sanitization.
Covers:
- Workout input validation
- Valid JSON responses
- Invalid JSON responses
- Missing workout fields
- Empty LLM responses
- 7-day schedule validation
"""

import pytest
from core.validators import (
    validate_user_preferences,
    clean_and_parse_llm_json,
    validate_workout_plan,
    ValidationError,
)
from models.workout_schema import WorkoutPreferences


def test_valid_user_preferences():
    """Test valid inputs conforming to Problem Statement 55."""
    data = {
        "fitness_goal": "Strength Development",
        "fitness_level": "Intermediate",
        "available_time": 45,
        "equipment": ["Dumbbells"],
        "preferred_days_per_week": 4,
    }
    is_valid, err, prefs = validate_user_preferences(data)
    assert is_valid is True
    assert err == ""
    assert isinstance(prefs, WorkoutPreferences)
    assert prefs.fitness_goal == "Strength Development"
    assert prefs.available_time == 45


def test_invalid_workout_time_below_min():
    """Test rejection of available time under 10 minutes."""
    data = {
        "fitness_goal": "General Fitness",
        "fitness_level": "Beginner",
        "available_time": 5,
        "equipment": ["No Equipment (Bodyweight)"],
    }
    is_valid, err, prefs = validate_user_preferences(data)
    assert is_valid is False
    assert "between 10 and 120 minutes" in err
    assert prefs is None


def test_invalid_workout_level():
    """Test rejection of unsupported fitness level."""
    data = {
        "fitness_goal": "General Fitness",
        "fitness_level": "Superhuman",
        "available_time": 30,
        "equipment": ["No Equipment (Bodyweight)"],
    }
    is_valid, err, prefs = validate_user_preferences(data)
    assert is_valid is False
    assert "Fitness level must be one of" in err


def test_severe_medical_limitation_warning():
    """Test detection of severe medical conditions prompting physician consultation."""
    data = {
        "fitness_goal": "General Fitness",
        "fitness_level": "Beginner",
        "available_time": 30,
        "equipment": ["No Equipment (Bodyweight)"],
        "limitations": "Recovering from heart attack surgery",
    }
    is_valid, err, prefs = validate_user_preferences(data)
    assert is_valid is False
    assert "Severe medical condition detected" in err


def test_clean_and_parse_valid_json():
    """Test parsing clean standard JSON."""
    raw = '{"plan_title": "Test Plan", "status": "ok"}'
    parsed = clean_and_parse_llm_json(raw)
    assert parsed["plan_title"] == "Test Plan"
    assert parsed["status"] == "ok"


def test_clean_and_parse_markdown_fence_json():
    """Test stripping markdown ```json ... ``` code fence."""
    raw = """
    Here is your requested workout routine:
    ```json
    {
      "plan_title": "Fenced Workout",
      "count": 7
    }
    ```
    I hope this helps!
    """
    parsed = clean_and_parse_llm_json(raw)
    assert parsed["plan_title"] == "Fenced Workout"
    assert parsed["count"] == 7


def test_clean_and_parse_trailing_commas():
    """Test regex correction for trailing commas in LLM JSON output."""
    raw = """
    {
      "items": [1, 2, 3,],
      "name": "Trailing Object",
    }
    """
    parsed = clean_and_parse_llm_json(raw)
    assert parsed["name"] == "Trailing Object"
    assert len(parsed["items"]) == 3


def test_empty_llm_response():
    """Test exception raising on empty LLM response."""
    with pytest.raises(ValidationError, match="LLM returned an empty response"):
        clean_and_parse_llm_json("")


def test_invalid_json_format():
    """Test exception raising when response contains no JSON object delimiters."""
    with pytest.raises(ValidationError, match="No valid JSON object delimiter found"):
        clean_and_parse_llm_json("I cannot fulfill this request without more details.")


def test_missing_workout_fields_validation():
    """Test validation failure when core required schema fields are missing."""
    incomplete_data = {
        "plan_title": "Incomplete Plan",
        # Missing fitness_goal, fitness_level, daily_time_minutes, schedule
    }
    with pytest.raises(ValidationError, match="Plan validation failed"):
        validate_workout_plan(incomplete_data)


def test_schedule_seven_days_enforcement():
    """Test that schedules with fewer than 7 days are automatically completed with rest days."""
    partial_data = {
        "plan_title": "Short Plan",
        "fitness_goal": "Endurance",
        "fitness_level": "Beginner",
        "daily_time_minutes": 20,
        "equipment": ["No Equipment (Bodyweight)"],
        "weekly_summary": {
            "total_workout_days": 2,
            "total_recovery_days": 5,
            "estimated_total_minutes": 40,
        },
        "schedule": [
            {
                "day_number": 1,
                "day_name": "Monday",
                "day_type": "training",
                "focus": "Aerobic Conditioning",
                "estimated_minutes": 20,
                "exercises": [
                    {
                        "name": "Brisk Walk",
                        "muscle_group": "Full Body",
                        "sets": 1,
                        "reps_or_duration": "20 min",
                        "rest_seconds": 0,
                        "instructions": "Maintain brisk pace.",
                        "beginner_tip": "Stay hydrated.",
                    }
                ],
            }
        ],
    }
    plan = validate_workout_plan(partial_data)
    assert len(plan.schedule) == 7
    assert plan.schedule[0].day_type == "training"
    assert plan.schedule[1].day_type == "rest"
