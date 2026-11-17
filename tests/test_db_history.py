"""
Unit Tests for FITGEN AI SQLite Database and History Operations.
Verifies plan persistence, serialization, retrieval, statistics, and deletion.
"""

from database.history import (
    init_db,
    save_workout_plan,
    get_all_plans,
    get_plan_by_id,
    delete_plan_by_id,
    clear_history,
    get_history_stats,
)
from core.workout_generator import WorkoutGenerator
from models.workout_schema import WorkoutPreferences


def test_database_crud_workflow():
    """Test end-to-end database lifecycle: create, read, stats, and delete."""
    init_db()
    clear_history()

    # Verify initially empty
    stats = get_history_stats()
    assert stats["total_plans"] == 0

    # Generate a sample plan
    generator = WorkoutGenerator()
    prefs = WorkoutPreferences(
        fitness_goal="Strength Development",
        fitness_level="Intermediate",
        available_time=45,
        equipment=["Dumbbells"],
    )
    plan = generator.generate_evidence_based_plan(prefs)

    # 1. Save Plan
    success = save_workout_plan(plan, notes="Automated test routine")
    assert success is True

    # 2. Retrieve All
    plans = get_all_plans(limit=10)
    assert len(plans) == 1
    assert plans[0]["plan_id"] == plan.plan_id
    assert plans[0]["fitness_goal"] == "Strength Development"

    # 3. Retrieve by ID
    loaded_plan = get_plan_by_id(plan.plan_id)
    assert loaded_plan is not None
    assert loaded_plan.plan_id == plan.plan_id
    assert loaded_plan.fitness_level == "Intermediate"
    assert len(loaded_plan.schedule) == 7

    # 4. Check Stats
    new_stats = get_history_stats()
    assert new_stats["total_plans"] == 1
    assert new_stats["top_goal"] == "Strength Development"
    assert new_stats["avg_minutes"] == 45.0

    # 5. Delete Plan
    del_ok = delete_plan_by_id(plan.plan_id)
    assert del_ok is True

    # Verify deleted
    assert get_plan_by_id(plan.plan_id) is None
    assert len(get_all_plans()) == 0
