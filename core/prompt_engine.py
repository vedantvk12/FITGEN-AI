"""
Prompt Engineering Module for FITGEN AI.
Encapsulates system instructions, few-shot schema cues, and safety guardrails.
"""

from typing import Dict, Any
from config.settings import settings
from models.workout_schema import WorkoutPreferences


class PromptEngine:
    """Manages system and user prompt formulation for Ollama."""

    SYSTEM_PROMPT = """You are FITGEN AI, an elite, evidence-based physical conditioning and routine planning system developed for academic research and personal fitness optimization.

Your duty is to generate realistic, scientifically sound, and safe 7-day weekly exercise routines tailored strictly to the user's fitness goal, fitness level, available time, and available equipment.

STRICT OPERATIONAL DIRECTIVES:
1. RESPONSIBILITY & SAFETY:
   - Never diagnose any disease, musculoskeletal injury, or medical condition.
   - If user notes mention an acute injury or severe pain, explicitly recommend clearance from a certified physician or physiotherapist.
   - For Beginners, emphasize compound foundational movements, controlled tempos, bodyweight mechanics, and conservative volume.
   - Never program extreme high-risk ballistic movements (e.g., behind-the-neck presses, uncontrolled max deadlifts) for beginners.
   - Do not promise guaranteed physiological outcomes (e.g. "lose 10kg in 7 days").

2. PERIODIZATION & STRUCTURE:
   - Provide exactly 7 sequential days (Day 1 through Day 7).
   - Program realistic recovery: Include 1 to 3 rest or active recovery days depending on fitness level (Beginners typically need 2-3 recovery days; Advanced need at least 1-2).
   - Every workout day must specify:
     * Warm-up routine (3-5 minutes) with dynamic mobility.
     * Core exercises with anatomical muscle groups, realistic sets (2-4), clear rep targets or seconds, and rest intervals (30-120s).
     * Cool-down protocol (3-5 minutes) with parasympathetic static stretches.
     * Specific daily recovery recommendation.

3. STRICT JSON OUTPUT FORMAT:
   - Output MUST be valid, raw JSON with NO conversational preambles, NO Markdown text outside the JSON, and NO explanatory commentary.
   - Adhere strictly to the requested JSON schema.
"""

    @classmethod
    def build_workout_prompt(cls, prefs: WorkoutPreferences) -> str:
        """
        Construct the generation prompt enforcing user parameters and JSON output schema.
        """
        equipment_str = ", ".join(prefs.equipment) if prefs.equipment else "Bodyweight / No Equipment"
        focus_areas_str = ", ".join(prefs.target_areas) if prefs.target_areas else "Balanced Full Body"
        limitations_str = prefs.limitations if prefs.limitations else "None reported"

        prompt = f"""Generate a personalized 7-Day Weekly Workout Plan adhering to the following parameters:

[USER PROFILE & CONSTRAINTS]
- Fitness Goal: {prefs.fitness_goal}
- Experience Level: {prefs.fitness_level}
- Target Daily Workout Duration: {prefs.available_time} minutes
- Available Equipment: {equipment_str}
- Preferred Training Frequency: {prefs.preferred_days_per_week} active days out of 7
- Target Focus Areas: {focus_areas_str}
- Physical Limitations / Avoid Movements: {limitations_str}
- User Notes: {prefs.notes or 'None'}

[EXACT JSON OUTPUT SCHEMA REQUIRED]
You must respond with a single JSON object matching this exact structure:
{{
  "plan_title": "Descriptive title for this routine",
  "fitness_goal": "{prefs.fitness_goal}",
  "fitness_level": "{prefs.fitness_level}",
  "daily_time_minutes": {prefs.available_time},
  "equipment": {list(prefs.equipment)},
  "weekly_summary": {{
    "total_workout_days": 4 or 5,
    "total_recovery_days": 2 or 3,
    "estimated_total_minutes": {prefs.available_time * prefs.preferred_days_per_week},
    "split_type": "e.g., Upper/Lower or Push/Pull/Legs or Full-Body Circuit",
    "key_benefits": [
      "Target benefit 1",
      "Target benefit 2",
      "Target benefit 3"
    ]
  }},
  "schedule": [
    {{
      "day_number": 1,
      "day_name": "Monday",
      "day_type": "training",
      "focus": "e.g. Upper Body Strength & Hypertrophy",
      "estimated_minutes": {prefs.available_time},
      "warmup": {{
        "duration_minutes": 5,
        "activities": ["Arm Circles", "Band Dislocates", "Torso Twists"],
        "instructions": "Increase blood flow and shoulder capsule mobility."
      }},
      "exercises": [
        {{
          "name": "Standard Push-Up (or modified incline)",
          "muscle_group": "Chest, Shoulders & Triceps",
          "sets": 3,
          "reps_or_duration": "10-12 reps",
          "rest_seconds": 60,
          "instructions": "Maintain rigid plank posture, lower chest to floor, press up explosively.",
          "beginner_tip": "Perform hands on an elevated surface or wall if regular push-ups compromise lumbar posture.",
          "form_cue": "Engage glutes and brace core throughout the eccentric descent."
        }}
      ],
      "cooldown": {{
        "duration_minutes": 5,
        "activities": ["Doorway Chest Stretch", "Child's Pose"],
        "instructions": "Hold each stretch for 30 seconds with slow nasal breathing."
      }},
      "recovery_recommendation": "Hydrate and ensure adequate protein intake post-session."
    }}
  ],
  "general_recommendations": {{
    "nutrition_guidelines": [
      "Consume adequate dietary protein to support myofibrillar protein synthesis.",
      "Time carbohydrates around your workout window for sustained energy.",
      "Incorporate unrefined whole foods and healthy essential fatty acids."
    ],
    "hydration_tip": "Drink at least 500ml water prior to training and maintain hydration throughout.",
    "sleep_and_recovery": "Aim for 7 to 9 hours of uninterrupted sleep for neuromuscular recovery.",
    "progressive_overload_advice": "When all sets can be completed with perfect form, increase resistance or add 1-2 repetitions.",
    "safety_warning": "Consult a physician before undertaking strenuous exercise. Stop if dizziness or sharp discomfort occurs."
  }}
}}

CRITICAL: Return exactly 7 days in the "schedule" list (Day 1 through Day 7). For rest days, set day_type to 'rest' or 'active_recovery' and keep the exercises array empty or light mobility drills. Provide realistic exercise names matching the equipment: {equipment_str}.
Return ONLY valid JSON.
"""
        return prompt

    @classmethod
    def build_tips_prompt(cls, goal: str, level: str) -> str:
        """Prompt for generating focused, evidence-based fitness tips."""
        return f"""You are FITGEN AI. Provide 4 concise, high-impact fitness & lifestyle tips for a {level} individual pursuing {goal}.
Format your response as valid JSON with this structure:
{{
  "category": "{goal}",
  "level": "{level}",
  "tips": [
    {{
      "title": "Short punchy title",
      "category": "Exercise / Nutrition / Recovery / Mindset",
      "description": "2-3 sentences of actionable, science-grounded advice."
    }}
  ]
}}
Return ONLY valid JSON.
"""
