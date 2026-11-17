"""
Helper utilities and formatting functions for FITGEN AI.
"""

from typing import Dict, Any, List
from models.workout_schema import WeeklyWorkoutPlan


def format_duration(minutes: int) -> str:
    """Format minutes into human-readable string."""
    if minutes < 60:
        return f"{minutes} mins"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours}h {rem}m" if rem > 0 else f"{hours}h"


def get_day_badge_color(day_type: str) -> Dict[str, str]:
    """Return styling parameters for day type badges."""
    dt = day_type.lower()
    if "recov" in dt:
        return {
            "bg": "rgba(245, 158, 11, 0.15)",
            "border": "#F59E0B",
            "text": "#FBBF24",
            "label": "Active Recovery",
            "icon": "⚡",
        }
    elif "rest" in dt:
        return {
            "bg": "rgba(148, 163, 184, 0.12)",
            "border": "#64748B",
            "text": "#94A3B8",
            "label": "Complete Rest",
            "icon": "☕",
        }
    else:
        return {
            "bg": "rgba(0, 255, 135, 0.12)",
            "border": "#00FF87",
            "text": "#00FF87",
            "label": "Training Day",
            "icon": "🏋️",
        }


def get_muscle_group_icon(muscle: str) -> str:
    """Return clean icon or symbol for target muscle group."""
    m = muscle.lower()
    if "chest" in m or "pec" in m:
        return "🛡️"
    elif "back" in m or "lat" in m:
        return "🦅"
    elif "leg" in m or "quad" in m or "hamstring" in m or "glute" in m:
        return "🦵"
    elif "shoulder" in m or "delt" in m:
        return "💪"
    elif "core" in m or "ab" in m:
        return "🎯"
    elif "cardio" in m or "heart" in m:
        return "❤️‍🔥"
    return "⚡"


def calculate_plan_metrics(plan: WeeklyWorkoutPlan) -> Dict[str, Any]:
    """Calculate analytics and distributions for visualization."""
    training_days = 0
    recovery_days = 0
    rest_days = 0
    total_exercises = 0
    muscle_counts: Dict[str, int] = {}
    daily_minutes: List[Dict[str, Any]] = []

    for day in plan.schedule:
        dt = day.day_type.lower()
        if dt == "training":
            training_days += 1
            total_exercises += len(day.exercises)
            for ex in day.exercises:
                # Group primary muscle
                primary_m = ex.muscle_group.split(",")[0].strip()
                muscle_counts[primary_m] = muscle_counts.get(primary_m, 0) + 1
        elif "recov" in dt:
            recovery_days += 1
        else:
            rest_days += 1

        daily_minutes.append({
            "Day": day.day_name,
            "Minutes": day.estimated_minutes,
            "Type": day.day_type.replace("_", " ").title()
        })

    return {
        "training_days": training_days,
        "recovery_days": recovery_days + rest_days,
        "active_recovery_days": recovery_days,
        "complete_rest_days": rest_days,
        "total_exercises": total_exercises,
        "total_minutes": sum(d["Minutes"] for d in daily_minutes),
        "muscle_distribution": muscle_counts,
        "daily_breakdown": daily_minutes,
    }
