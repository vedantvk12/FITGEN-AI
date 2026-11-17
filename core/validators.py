"""
Validation and sanitization module for FITGEN AI.
Handles input verification, LLM JSON extraction, and Pydantic validation.
"""

import json
import re
from typing import Dict, Any, Tuple
from config.settings import settings
from models.workout_schema import WorkoutPreferences, WeeklyWorkoutPlan, DayWorkout, WeeklySummary


class ValidationError(Exception):
    """Custom validation exception."""
    pass


def validate_user_preferences(prefs_dict: Dict[str, Any]) -> Tuple[bool, str, WorkoutPreferences]:
    """
    Validate user inputs against Problem Statement 55 requirements.
    Returns: (is_valid: bool, error_message: str, preferences_object)
    """
    try:
        goal = prefs_dict.get("fitness_goal", "").strip()
        if not goal:
            return False, "Please select a fitness goal.", None

        level = prefs_dict.get("fitness_level", "").strip()
        if level not in settings.FITNESS_LEVELS:
            return False, f"Fitness level must be one of {settings.FITNESS_LEVELS}.", None

        try:
            available_time = int(prefs_dict.get("available_time", 30))
        except (ValueError, TypeError):
            return False, "Available time must be a valid integer number of minutes.", None

        if available_time < 10 or available_time > 120:
            return False, "Daily workout time must be between 10 and 120 minutes.", None

        equipment = prefs_dict.get("equipment", [])
        if isinstance(equipment, str):
            equipment = [e.strip() for e in equipment.split(",") if e.strip()]
        if not equipment:
            equipment = ["No Equipment (Bodyweight)"]

        # Health limitation check
        limitations = prefs_dict.get("limitations", "").strip()
        severe_keywords = ["heart attack", "chest pain", "fracture", "torn", "hernia", "surgery", "severe chronic"]
        for kw in severe_keywords:
            if kw in limitations.lower():
                return False, f"Notice: Severe medical condition detected ('{kw}'). Please consult a licensed medical physician before starting any workout program.", None

        prefs = WorkoutPreferences(
            fitness_goal=goal,
            fitness_level=level,
            available_time=available_time,
            equipment=equipment,
            preferred_days_per_week=int(prefs_dict.get("preferred_days_per_week", 5)),
            target_areas=prefs_dict.get("target_areas", []),
            limitations=limitations or "None",
            notes=prefs_dict.get("notes", "")
        )
        return True, "", prefs

    except Exception as e:
        return False, f"Validation error: {str(e)}", None


def clean_and_parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    Sanitize and extract valid JSON from raw LLM output.
    Strips markdown code blocks, isolates outer JSON structure, and fixes common syntax traps.
    """
    if not raw_text or not raw_text.strip():
        raise ValidationError("LLM returned an empty response.")

    text = raw_text.strip()

    # 1. Strip markdown code fences if present
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, text)
    if match:
        text = match.group(1).strip()

    # 2. Locate outermost JSON object { ... }
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
        raise ValidationError("No valid JSON object delimiter found in the model response.")

    json_str = text[first_brace : last_brace + 1]

    # 3. Clean trailing commas in arrays/objects (common LLM failure mode)
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    # 4. Attempt direct parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as direct_err:
        # Fallback heuristic: replace unescaped control chars
        try:
            cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", json_str)
            return json.loads(cleaned)
        except Exception:
            raise ValidationError(
                f"Failed to parse LLM response into structured JSON: {direct_err.msg} at line {direct_err.lineno}, col {direct_err.colno}"
            )


def validate_workout_plan(data: Dict[str, Any], expected_prefs: WorkoutPreferences = None) -> WeeklyWorkoutPlan:
    """
    Validate parsed JSON dictionary against the WeeklyWorkoutPlan Pydantic model.
    Enforces 7 days, checks schedule coherence, and ensures recovery day presence.
    """
    try:
        # If schedule is present, verify day numbering and normalization
        if "schedule" in data and isinstance(data["schedule"], list):
            # Ensure exactly 7 days
            days = data["schedule"]
            if len(days) < 7:
                # If model returned fewer than 7 days, fill in rest days gracefully
                day_names = settings.DAYS_OF_WEEK
                while len(days) < 7:
                    idx = len(days) + 1
                    days.append({
                        "day_number": idx,
                        "day_name": day_names[idx - 1] if idx - 1 < len(day_names) else f"Day {idx}",
                        "day_type": "rest",
                        "focus": "Active Recovery & Mobility",
                        "estimated_minutes": 20,
                        "warmup": {"duration_minutes": 5, "activities": ["Light Walking", "Cat-Cow"], "instructions": "Gentle mobility"},
                        "exercises": [],
                        "cooldown": {"duration_minutes": 5, "activities": ["Child's Pose"], "instructions": "Deep diaphragmatic breathing"},
                        "recovery_recommendation": "Hydrate and get 8 hours of restorative sleep."
                    })
            elif len(days) > 7:
                data["schedule"] = days[:7]

            # Re-index days 1..7
            for i, day in enumerate(data["schedule"]):
                day["day_number"] = i + 1
                if "day_name" not in day or not day["day_name"]:
                    day["day_name"] = settings.DAYS_OF_WEEK[i]

        # Calculate or sync summary if missing
        if "weekly_summary" not in data or not isinstance(data["weekly_summary"], dict):
            workout_days = sum(1 for d in data.get("schedule", []) if d.get("day_type") == "training")
            recov_days = 7 - workout_days
            total_mins = sum(int(d.get("estimated_minutes", 30)) for d in data.get("schedule", []))
            data["weekly_summary"] = {
                "total_workout_days": workout_days if workout_days > 0 else 5,
                "total_recovery_days": recov_days,
                "estimated_total_minutes": total_mins if total_mins > 0 else 150,
                "split_type": "Personalized Routine",
                "key_benefits": ["Functional hypertrophy", "Cardiorespiratory conditioning", "Injury prevention"]
            }

        # Override/sync with user preferences if provided
        if expected_prefs:
            data["fitness_goal"] = expected_prefs.fitness_goal
            data["fitness_level"] = expected_prefs.fitness_level
            data["daily_time_minutes"] = expected_prefs.available_time
            data["equipment"] = expected_prefs.equipment

        # Instantiate and validate Pydantic model
        plan = WeeklyWorkoutPlan.model_validate(data)
        return plan

    except Exception as e:
        raise ValidationError(f"Plan validation failed: {str(e)}")
