"""FITGEN AI Database Package."""
from database.history import (
    init_db,
    save_workout_plan,
    get_all_plans,
    get_plan_by_id,
    delete_plan_by_id,
    clear_history,
    get_history_stats,
)

__all__ = [
    "init_db",
    "save_workout_plan",
    "get_all_plans",
    "get_plan_by_id",
    "delete_plan_by_id",
    "clear_history",
    "get_history_stats",
]
