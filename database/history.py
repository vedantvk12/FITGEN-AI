"""
Workout history management module for FITGEN AI.
Handles saving, retrieving, deleting, and analyzing previously generated routines.
"""

import json
from typing import List, Optional, Dict, Any
from database.db import get_db_connection, init_db
from models.workout_schema import WeeklyWorkoutPlan


def save_workout_plan(plan: WeeklyWorkoutPlan, notes: str = "") -> bool:
    """Save a generated WeeklyWorkoutPlan to local SQLite history."""
    init_db()
    try:
        equipment_str = ", ".join(plan.equipment) if plan.equipment else "None"
        plan_json_str = plan.model_dump_json()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workout_history (
                    plan_id, created_at, fitness_goal, fitness_level,
                    daily_time_minutes, equipment_list, plan_title,
                    total_workout_days, plan_json, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(plan_id) DO UPDATE SET
                    plan_json = excluded.plan_json,
                    notes = excluded.notes;
                """,
                (
                    plan.plan_id,
                    plan.created_at,
                    plan.fitness_goal,
                    plan.fitness_level,
                    plan.daily_time_minutes,
                    equipment_str,
                    plan.plan_title,
                    plan.weekly_summary.total_workout_days,
                    plan_json_str,
                    notes,
                ),
            )
            return True
    except Exception as e:
        print(f"Error saving workout plan to database: {e}")
        return False


def get_all_plans(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve list of saved workout plans with metadata."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, plan_id, created_at, fitness_goal, fitness_level,
                   daily_time_minutes, equipment_list, plan_title,
                   total_workout_days, notes
            FROM workout_history
            ORDER BY datetime(created_at) DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_plan_by_id(plan_id: str) -> Optional[WeeklyWorkoutPlan]:
    """Fetch complete WeeklyWorkoutPlan instance by plan_id."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plan_json FROM workout_history WHERE plan_id = ?;",
            (plan_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        try:
            data = json.loads(row["plan_json"])
            return WeeklyWorkoutPlan.model_validate(data)
        except Exception as e:
            print(f"Error validating saved plan JSON: {e}")
            return None


def delete_plan_by_id(plan_id: str) -> bool:
    """Delete a plan from history."""
    init_db()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workout_history WHERE plan_id = ?;", (plan_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting plan: {e}")
        return False


def clear_history() -> bool:
    """Clear all records from workout history."""
    init_db()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workout_history;")
            return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False


def get_history_stats() -> Dict[str, Any]:
    """Compute aggregate statistics of generated workout history."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_count FROM workout_history;")
        total_count = cursor.fetchone()["total_count"]

        if total_count == 0:
            return {
                "total_plans": 0,
                "top_goal": "N/A",
                "avg_minutes": 0,
                "top_level": "N/A",
            }

        cursor.execute(
            """
            SELECT fitness_goal, COUNT(*) AS count
            FROM workout_history
            GROUP BY fitness_goal
            ORDER BY count DESC
            LIMIT 1;
            """
        )
        top_goal_row = cursor.fetchone()
        top_goal = top_goal_row["fitness_goal"] if top_goal_row else "N/A"

        cursor.execute("SELECT AVG(daily_time_minutes) AS avg_time FROM workout_history;")
        avg_time_row = cursor.fetchone()
        avg_minutes = round(avg_time_row["avg_time"] or 0, 1)

        cursor.execute(
            """
            SELECT fitness_level, COUNT(*) AS count
            FROM workout_history
            GROUP BY fitness_level
            ORDER BY count DESC
            LIMIT 1;
            """
        )
        top_level_row = cursor.fetchone()
        top_level = top_level_row["fitness_level"] if top_level_row else "N/A"

        return {
            "total_plans": total_count,
            "top_goal": top_goal,
            "avg_minutes": avg_minutes,
            "top_level": top_level,
        }
