"""
Integration and End-to-End Tests for FITGEN AI Workout Generator.
Tests the 5 mandatory academic user configurations specified in Problem Statement 55.
"""

from unittest.mock import MagicMock
import pytest
from core.workout_generator import WorkoutGenerator
from models.workout_schema import WorkoutPreferences, WeeklyWorkoutPlan


@pytest.fixture
def generator():
    """Create workout generator instance with mock client."""
    mock_client = MagicMock()
    return WorkoutGenerator(ollama_client=mock_client)


def test_configuration_1_beginner_general_fitness(generator):
    """
    Test 1:
    Beginner, General Fitness, 20 minutes, No Equipment.
    """
    prefs = WorkoutPreferences(
        fitness_goal="General Fitness",
        fitness_level="Beginner",
        available_time=20,
        equipment=["No Equipment (Bodyweight)"],
        preferred_days_per_week=4,
    )
    plan = generator.generate_evidence_based_plan(prefs)

    assert isinstance(plan, WeeklyWorkoutPlan)
    assert plan.fitness_goal == "General Fitness"
    assert plan.fitness_level == "Beginner"
    assert plan.daily_time_minutes == 20
    assert len(plan.schedule) == 7

    # Validate rest/recovery presence
    recovery_count = sum(1 for d in plan.schedule if d.day_type in ["rest", "active_recovery"])
    assert recovery_count >= 2, "Beginners require at least 2 recovery/rest days."

    # Validate workout days have exercises and warmup
    training_days = [d for d in plan.schedule if d.day_type == "training"]
    assert len(training_days) > 0
    for td in training_days:
        assert len(td.exercises) >= 3
        assert td.warmup is not None
        assert td.cooldown is not None
        for ex in td.exercises:
            assert ex.sets >= 1
            assert ex.rest_seconds >= 30
            assert ex.instructions != ""


def test_configuration_2_beginner_weight_management(generator):
    """
    Test 2:
    Beginner, Weight Management, 30 minutes, Yoga Mat.
    """
    prefs = WorkoutPreferences(
        fitness_goal="Weight Management",
        fitness_level="Beginner",
        available_time=30,
        equipment=["Yoga Mat"],
        preferred_days_per_week=4,
    )
    plan = generator.generate_evidence_based_plan(prefs)

    assert plan.fitness_goal == "Weight Management"
    assert plan.fitness_level == "Beginner"
    assert plan.daily_time_minutes == 30
    assert len(plan.schedule) == 7
    assert plan.weekly_summary.total_workout_days == 4
    assert plan.weekly_summary.total_recovery_days == 3


def test_configuration_3_intermediate_strength_development(generator):
    """
    Test 3:
    Intermediate, Strength Development, 45 minutes, Dumbbells.
    """
    prefs = WorkoutPreferences(
        fitness_goal="Strength Development",
        fitness_level="Intermediate",
        available_time=45,
        equipment=["Dumbbells"],
        preferred_days_per_week=5,
    )
    plan = generator.generate_evidence_based_plan(prefs)

    assert plan.fitness_goal == "Strength Development"
    assert plan.fitness_level == "Intermediate"
    assert plan.daily_time_minutes == 45
    assert len(plan.schedule) == 7

    training_days = [d for d in plan.schedule if d.day_type == "training"]
    assert len(training_days) == 5

    # Check dumbbell exercises programmed
    has_db_exercise = any(
        "dumbbell" in ex.name.lower()
        for d in training_days
        for ex in d.exercises
    )
    assert has_db_exercise is True


def test_configuration_4_intermediate_flexibility_mobility(generator):
    """
    Test 4:
    Intermediate, Flexibility and Mobility, 20 minutes, No Equipment.
    """
    prefs = WorkoutPreferences(
        fitness_goal="Flexibility and Mobility",
        fitness_level="Intermediate",
        available_time=20,
        equipment=["No Equipment (Bodyweight)"],
        preferred_days_per_week=4,
    )
    plan = generator.generate_evidence_based_plan(prefs)

    assert plan.fitness_goal == "Flexibility and Mobility"
    assert plan.daily_time_minutes == 20
    assert len(plan.schedule) == 7
    assert plan.general_recommendations.hydration_tip != ""


def test_configuration_5_advanced_endurance(generator):
    """
    Test 5:
    Advanced, Endurance, 60 minutes, Full Home Gym.
    """
    prefs = WorkoutPreferences(
        fitness_goal="Endurance",
        fitness_level="Advanced",
        available_time=60,
        equipment=["Full Home Gym"],
        preferred_days_per_week=6,
    )
    plan = generator.generate_evidence_based_plan(prefs)

    assert plan.fitness_goal == "Endurance"
    assert plan.fitness_level == "Advanced"
    assert plan.daily_time_minutes == 60
    assert len(plan.schedule) == 7
    assert plan.weekly_summary.total_workout_days == 6
    assert plan.weekly_summary.total_recovery_days == 1


def test_generator_with_mocked_llm_json(generator):
    """Test full generation flow when Ollama returns structured JSON string."""
    sample_json = """
    {
      "plan_title": "AI Synthesized Hypertrophy Plan",
      "fitness_goal": "Muscle Building",
      "fitness_level": "Intermediate",
      "daily_time_minutes": 45,
      "equipment": ["Dumbbells"],
      "weekly_summary": {
        "total_workout_days": 4,
        "total_recovery_days": 3,
        "estimated_total_minutes": 180,
        "split_type": "Upper / Lower Split",
        "key_benefits": ["Hypertrophy", "Strength", "Posture"]
      },
      "schedule": [
        {
          "day_number": 1,
          "day_name": "Monday",
          "day_type": "training",
          "focus": "Upper Body Push & Pull",
          "estimated_minutes": 45,
          "warmup": {
            "duration_minutes": 5,
            "activities": ["Arm Circles", "Band Pull-Aparts"],
            "instructions": "Warm up rotator cuffs."
          },
          "exercises": [
            {
              "name": "Dumbbell Bench Press",
              "muscle_group": "Pectorals",
              "sets": 3,
              "reps_or_duration": "10-12 reps",
              "rest_seconds": 60,
              "instructions": "Press weights upward with controlled tempo.",
              "beginner_tip": "Keep wrists stacked directly above elbows.",
              "form_cue": "Retract scapula into bench."
            }
          ],
          "cooldown": {
            "duration_minutes": 5,
            "activities": ["Chest Stretch"],
            "instructions": "Breathe deeply."
          },
          "recovery_recommendation": "Hydrate and sleep 8 hours."
        },
        {"day_number": 2, "day_name": "Tuesday", "day_type": "rest", "focus": "Rest", "estimated_minutes": 0, "exercises": [], "recovery_recommendation": "Active walk."},
        {"day_number": 3, "day_name": "Wednesday", "day_type": "training", "focus": "Lower Body", "estimated_minutes": 45, "exercises": [{"name": "Goblet Squat", "muscle_group": "Quads", "sets": 3, "reps_or_duration": "10 reps", "rest_seconds": 60, "instructions": "Squat down.", "beginner_tip": "Keep chest tall."}], "recovery_recommendation": "Rest."},
        {"day_number": 4, "day_name": "Thursday", "day_type": "rest", "focus": "Rest", "estimated_minutes": 0, "exercises": [], "recovery_recommendation": "Hydrate."},
        {"day_number": 5, "day_name": "Friday", "day_type": "training", "focus": "Upper Body", "estimated_minutes": 45, "exercises": [{"name": "Dumbbell Row", "muscle_group": "Lats", "sets": 3, "reps_or_duration": "12 reps", "rest_seconds": 60, "instructions": "Row weight.", "beginner_tip": "Do not swing."}], "recovery_recommendation": "Rest."},
        {"day_number": 6, "day_name": "Saturday", "day_type": "training", "focus": "Lower Body", "estimated_minutes": 45, "exercises": [{"name": "Lunges", "muscle_group": "Glutes", "sets": 3, "reps_or_duration": "10 reps", "rest_seconds": 60, "instructions": "Step forward.", "beginner_tip": "Keep balance."}], "recovery_recommendation": "Rest."},
        {"day_number": 7, "day_name": "Sunday", "day_type": "rest", "focus": "Rest", "estimated_minutes": 0, "exercises": [], "recovery_recommendation": "Rest."}
      ],
      "general_recommendations": {
        "nutrition_guidelines": ["Eat 1.6g/kg protein."],
        "hydration_tip": "Drink 3L water.",
        "sleep_and_recovery": "Sleep 8 hours.",
        "progressive_overload_advice": "Add 1 rep weekly.",
        "safety_warning": "Stop on joint pain."
      }
    }
    """
    generator.client.generate.return_value = sample_json
    prefs = WorkoutPreferences(
        fitness_goal="Muscle Building",
        fitness_level="Intermediate",
        available_time=45,
        equipment=["Dumbbells"],
    )
    plan = generator.generate_plan(prefs, is_demo_mode=False)

    assert plan.plan_title == "AI Synthesized Hypertrophy Plan"
    assert len(plan.schedule) == 7
    assert plan.schedule[0].exercises[0].name == "Dumbbell Bench Press"
