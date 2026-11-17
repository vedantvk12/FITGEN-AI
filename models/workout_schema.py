"""
Pydantic Schemas for FITGEN AI Workout Engine.
Strict validation of user input and AI-generated workout structures.
"""

from datetime import datetime, timezone
from typing import List, Optional, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class ExerciseItem(BaseModel):
    """Individual exercise specification within a daily workout."""
    name: str = Field(..., description="Standard anatomical name of the exercise")
    muscle_group: str = Field(..., description="Target muscle group, e.g. Chest, Quads, Core, Hamstrings")
    sets: int = Field(..., ge=1, le=10, description="Number of sets to perform")
    reps_or_duration: str = Field(..., description="Repetitions (e.g. '10-12 reps') or timed duration ('30 sec')")
    rest_seconds: int = Field(..., ge=0, le=300, description="Rest period in seconds between sets")
    instructions: str = Field(..., description="Clear, progressive step-by-step cue for proper movement execution")
    beginner_tip: str = Field(..., description="Safety modification or common mistake cue")
    form_cue: Optional[str] = Field(default=None, description="Key mental cue for optimal biomechanics")


class PhaseDetails(BaseModel):
    """Warmup or Cooldown protocol details."""
    duration_minutes: int = Field(default=5, ge=2, le=20, description="Estimated duration in minutes")
    activities: List[str] = Field(default_factory=list, description="List of dynamic mobility drills or cool-down stretches")
    instructions: str = Field(default="", description="Protocol guidance for this phase")


class DayWorkout(BaseModel):
    """Complete regimen for a specific day of the 7-day schedule."""
    day_number: int = Field(..., ge=1, le=7, description="Day index 1 through 7")
    day_name: str = Field(..., description="Day label, e.g., 'Monday' or 'Day 1'")
    day_type: Literal["training", "active_recovery", "rest"] = Field(
        default="training",
        description="Type of session: training, active_recovery, or rest"
    )
    focus: str = Field(..., description="Primary stimulus, e.g., 'Upper Body Strength', 'Active Mobility & Walk'")
    estimated_minutes: int = Field(..., ge=0, le=120, description="Total expected time in minutes")
    warmup: Optional[PhaseDetails] = Field(
        default_factory=lambda: PhaseDetails(duration_minutes=5, activities=["Dynamic Arm Circles", "Leg Swings"], instructions="Elevate heart rate and lubricate joints.")
    )
    exercises: List[ExerciseItem] = Field(
        default_factory=list,
        description="List of exercises (empty for complete rest days)"
    )
    cooldown: Optional[PhaseDetails] = Field(
        default_factory=lambda: PhaseDetails(duration_minutes=5, activities=["Static Hamstring Stretch", "Child's Pose"], instructions="Lower heart rate and initiate parasympathetic recovery.")
    )
    recovery_recommendation: str = Field(
        default="Maintain adequate hydration and sleep 7-8 hours.",
        description="Targeted recovery advice for this day"
    )

    @field_validator("day_type", mode="before")
    @classmethod
    def normalize_day_type(cls, v: str) -> str:
        if isinstance(v, str):
            val = v.strip().lower().replace(" ", "_").replace("-", "_")
            if "recov" in val or "active" in val:
                return "active_recovery"
            elif "rest" in val or "off" in val:
                return "rest"
            elif "train" in val or "workout" in val:
                return "training"
        return "training"


class WeeklySummary(BaseModel):
    """Aggregated insights and physiological metrics for the week."""
    total_workout_days: int = Field(..., ge=1, le=7)
    total_recovery_days: int = Field(..., ge=0, le=6)
    estimated_total_minutes: int = Field(..., ge=15)
    split_type: str = Field(default="Balanced Full Body Split", description="Training methodology description")
    key_benefits: List[str] = Field(default_factory=list, description="Key physiological adaptations targeted")


class GeneralRecommendations(BaseModel):
    """Holistic lifestyle and biomechanical guidelines."""
    nutrition_guidelines: List[str] = Field(
        default_factory=lambda: [
            "Prioritize lean protein (1.4-1.8g per kg bodyweight) to facilitate tissue synthesis.",
            "Incorporate complex carbohydrates pre-workout for glycogen replenishment.",
            "Include colorful vegetables rich in micronutrients and antioxidants."
        ]
    )
    hydration_tip: str = Field(
        default="Aim for 2.5 to 3.5 liters of water daily, adding electrolytes during intense sweating.",
        description="Hydration strategy"
    )
    sleep_and_recovery: str = Field(
        default="Prioritize 7-9 hours of consistent nocturnal sleep to maximize cellular repair and endocrine balance.",
        description="Recovery guidance"
    )
    progressive_overload_advice: str = Field(
        default="Gradually increase reps, load, or decrease rest periods weekly as movements become easier.",
        description="Progression advice"
    )
    safety_warning: str = Field(
        default="Stop immediately if you experience sharp, joint-related pain or dizziness. Consult a licensed physician before starting any rigorous fitness regimen.",
        description="Mandatory health disclaimer"
    )


class WeeklyWorkoutPlan(BaseModel):
    """Complete 7-day intelligent fitness routine."""
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    plan_title: str = Field(default="FITGEN Personalized Weekly Routine")
    fitness_goal: str = Field(..., description="Target goal, e.g., Muscle Building")
    fitness_level: str = Field(..., description="Experience level: Beginner, Intermediate, Advanced")
    daily_time_minutes: int = Field(..., ge=10, le=120)
    equipment: List[str] = Field(default_factory=list)
    weekly_summary: WeeklySummary
    schedule: List[DayWorkout] = Field(..., min_length=7, max_length=7, description="Exact 7-day schedule")
    general_recommendations: GeneralRecommendations = Field(default_factory=GeneralRecommendations)


class WorkoutPreferences(BaseModel):
    """User input configuration for workout planning."""
    fitness_goal: str
    fitness_level: str
    available_time: int
    equipment: List[str]
    preferred_days_per_week: int = 5
    target_areas: List[str] = Field(default_factory=list)
    limitations: str = "None"
    notes: Optional[str] = ""

    @field_validator("available_time")
    @classmethod
    def validate_time(cls, v: int) -> int:
        if v < 10 or v > 120:
            raise ValueError("Available workout time must be between 10 and 120 minutes.")
        return v
