"""
Workout Generation Orchestrator for FITGEN AI.
Coordinates prompt construction, Ollama execution, schema validation, and database persistence.
"""

from typing import Optional, Dict, Any, List
from models.workout_schema import (
    WorkoutPreferences,
    WeeklyWorkoutPlan,
    DayWorkout,
    ExerciseItem,
    PhaseDetails,
    WeeklySummary,
    GeneralRecommendations,
)
from core.prompt_engine import PromptEngine
from core.ollama_client import OllamaClient, OllamaError, OllamaConnectionError, OllamaModelNotFoundError
from core.validators import clean_and_parse_llm_json, validate_workout_plan, ValidationError
from database.history import save_workout_plan


class WorkoutGenerator:
    """Orchestrates end-to-end workout routine generation."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.client = ollama_client or OllamaClient()

    def generate_plan(
        self,
        preferences: WorkoutPreferences,
        model: Optional[str] = None,
        is_demo_mode: bool = False,
    ) -> WeeklyWorkoutPlan:
        """
        Generate a fully validated 7-day workout routine.
        If is_demo_mode is False, invokes the Ollama LLM and enforces strict JSON validation.
        If is_demo_mode is True (explicit user toggle), generates an evidence-based demo routine.
        """
        if is_demo_mode:
            plan = self.generate_evidence_based_plan(preferences, is_demo=True)
            save_workout_plan(plan, notes="Generated in Offline/Demonstration Mode")
            return plan

        # 1. Prepare Prompts
        system_prompt = PromptEngine.SYSTEM_PROMPT
        user_prompt = PromptEngine.build_workout_prompt(preferences)

        # 2. Invoke LLM via Ollama
        try:
            raw_response = self.client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=model,
                format_json=True,
            )
        except (OllamaConnectionError, OllamaModelNotFoundError, OllamaError) as e:
            # Do NOT silently fabricate. Re-raise with user-facing clarity.
            raise e

        # 3. Clean and parse JSON
        try:
            parsed_data = clean_and_parse_llm_json(raw_response)
        except ValidationError as e:
            raise ValidationError(f"LLM produced invalid JSON structure: {str(e)}")

        # 4. Validate against Pydantic schema
        try:
            plan = validate_workout_plan(parsed_data, expected_prefs=preferences)
        except ValidationError as e:
            raise ValidationError(f"LLM response failed schema validation: {str(e)}")

        # 5. Persist to local database
        save_workout_plan(plan, notes=f"Generated via Ollama ({model or self.client.default_model})")

        return plan

    def generate_fitness_tips(
        self,
        goal: str,
        level: str,
        model: Optional[str] = None,
        is_demo_mode: bool = False,
    ) -> List[Dict[str, str]]:
        """Fetch targeted fitness guidance for the user's specific profile."""
        if is_demo_mode:
            return self._get_fallback_tips(goal, level)

        prompt = PromptEngine.build_tips_prompt(goal, level)
        try:
            raw = self.client.generate(prompt=prompt, model=model, format_json=True)
            data = clean_and_parse_llm_json(raw)
            tips = data.get("tips", [])
            if isinstance(tips, list) and len(tips) > 0:
                return tips
        except Exception:
            pass  # Fall back to curated tips if Ollama is unavailable for tips
        return self._get_fallback_tips(goal, level)

    def generate_evidence_based_plan(
        self,
        prefs: WorkoutPreferences,
        is_demo: bool = False,
    ) -> WeeklyWorkoutPlan:
        """
        Generate a physiologically sound, evidence-based 7-day routine tailored
        to user goal, level, equipment, and duration.
        Used for test verification, offline demonstration, and benchmark validation.
        """
        goal = prefs.fitness_goal
        level = prefs.fitness_level
        mins = prefs.available_time
        eq = prefs.equipment
        days_active = min(max(prefs.preferred_days_per_week, 3), 6)

        # Dynamic title
        demo_tag = "[OFFLINE DEMO] " if is_demo else ""
        plan_title = f"{demo_tag}{level} {goal} Routine ({mins}m Daily)"

        # Curate schedule based on goal and level
        schedule: List[DayWorkout] = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Determine daily training template
        exercise_catalog = self._get_exercises_for_config(goal, level, eq)

        # Build 7 days
        # E.g. for 4 active days: Day 1 (Train), Day 2 (Train), Day 3 (Active Rec), Day 4 (Train), Day 5 (Train), Day 6 (Active Rec), Day 7 (Rest)
        active_pattern = [True, True, False, True, True, False, False]
        if days_active == 3:
            active_pattern = [True, False, True, False, True, False, False]
        elif days_active == 5:
            active_pattern = [True, True, True, False, True, True, False]
        elif days_active >= 6:
            active_pattern = [True, True, True, True, True, True, False]

        for i in range(7):
            d_num = i + 1
            d_name = day_names[i]
            is_training = active_pattern[i]

            if is_training:
                # Rotate focus
                split_focuses = [
                    ("Upper Body & Core Foundation", "Chest, Back, Shoulders, Core"),
                    ("Lower Body & Posterior Chain", "Quadriceps, Glutes, Hamstrings, Calves"),
                    ("Cardiovascular Conditioning & Core", "Full Body, Core, Heart Rate"),
                    ("Functional Push/Pull Dynamics", "Chest, Lats, Deltoids, Biceps"),
                    ("Total Body Metabolic Circuit", "Compound Full Body"),
                    ("Endurance & Core Stability", "Core, Lats, Glutes"),
                ]
                focus_name, focus_muscles = split_focuses[i % len(split_focuses)]

                # Pick 3-5 exercises depending on time
                num_ex = 3 if mins <= 20 else (4 if mins <= 30 else (5 if mins <= 45 else 6))
                selected_ex = exercise_catalog.get(focus_name, exercise_catalog["default"])[:num_ex]

                day = DayWorkout(
                    day_number=d_num,
                    day_name=d_name,
                    day_type="training",
                    focus=f"{focus_name}",
                    estimated_minutes=mins,
                    warmup=PhaseDetails(
                        duration_minutes=max(3, mins // 8),
                        activities=["Dynamic Joint Circles", "Hip Openers", "Arm Swings", "Torso Rotations"],
                        instructions="Gradually increase core body temperature and joint range of motion.",
                    ),
                    exercises=selected_ex,
                    cooldown=PhaseDetails(
                        duration_minutes=max(3, mins // 8),
                        activities=["Standing Quadriceps Stretch", "Doorway Chest Opener", "Child's Pose"],
                        instructions="Hold each stretch for 30 seconds with calm nasal breathing.",
                    ),
                    recovery_recommendation="Hydrate with 500ml water and consume 20-30g protein within 90 minutes.",
                )
            else:
                # Rest or Active Recovery
                is_active_rec = (i % 2 == 0)
                day_type = "active_recovery" if is_active_rec else "rest"
                focus_title = "Active Mobility & Gentle Walk" if is_active_rec else "Rest & Cellular Repair"
                
                day = DayWorkout(
                    day_number=d_num,
                    day_name=d_name,
                    day_type=day_type,
                    focus=focus_title,
                    estimated_minutes=15 if is_active_rec else 0,
                    warmup=PhaseDetails(
                        duration_minutes=5 if is_active_rec else 0,
                        activities=["Light joint rolls", "Cat-Cow mobility"] if is_active_rec else [],
                        instructions="Keep intensity below Zone 1.",
                    ) if is_active_rec else None,
                    exercises=[] if not is_active_rec else [
                        ExerciseItem(
                            name="Light Outdoor Walk / Foam Rolling",
                            muscle_group="Full Body & Fascia",
                            sets=1,
                            reps_or_duration="15-20 min",
                            rest_seconds=0,
                            instructions="Engage in conversational-pace movement to facilitate venous return.",
                            beginner_tip="Keep shoulders relaxed and breathe steadily through your nose.",
                            form_cue="Focus on posture and diaphragmatic breathing.",
                        )
                    ],
                    cooldown=PhaseDetails(
                        duration_minutes=5 if is_active_rec else 0,
                        activities=["Pigeon Pose", "Diaphragmatic Breathing"] if is_active_rec else [],
                        instructions="Decompress spine and downregulate nervous system.",
                    ) if is_active_rec else None,
                    recovery_recommendation="Prioritize 8 hours of sleep and adequate micronutrient-rich hydration.",
                )
            schedule.append(day)

        active_days_count = sum(1 for d in schedule if d.day_type == "training")
        rec_days_count = 7 - active_days_count
        total_minutes = sum(d.estimated_minutes for d in schedule)

        summary = WeeklySummary(
            total_workout_days=active_days_count,
            total_recovery_days=rec_days_count,
            estimated_total_minutes=total_minutes,
            split_type=f"{level} {goal} Periodized Split",
            key_benefits=[
                f"Progressive overload adapted for {level} biomechanics",
                f"Optimized work-to-rest ratio for {goal.lower()}",
                "Integrated mobility to mitigate injury risk and postural fatigue",
            ],
        )

        recs = GeneralRecommendations(
            nutrition_guidelines=[
                "Aim for a balanced macronutrient distribution emphasizing lean protein sources (1.4-1.8g/kg).",
                "Hydrate consistently with 30-40ml water per kg of body mass.",
                "Consume wholesome complex carbs 1-2 hours before training sessions.",
            ],
            hydration_tip="Drink 500ml water upon waking and maintain straw-colored urine throughout the day.",
            sleep_and_recovery="Target 7.5 to 8.5 hours of uninterrupted sleep for peak physiological adaptation.",
            progressive_overload_advice=f"For {level} trainees: increase resistance or reps every 1-2 weeks once form is rock-solid.",
            safety_warning="If you experience sharp joint pain, stop the movement immediately. Always warm up thoroughly.",
        )

        return WeeklyWorkoutPlan(
            plan_title=plan_title,
            fitness_goal=goal,
            fitness_level=level,
            daily_time_minutes=mins,
            equipment=eq,
            weekly_summary=summary,
            schedule=schedule,
            general_recommendations=recs,
        )

    def _get_exercises_for_config(
        self, goal: str, level: str, eq: List[str]
    ) -> Dict[str, List[ExerciseItem]]:
        """Generate appropriate exercise libraries according to available equipment."""
        has_dumbbells = any("dumbbell" in e.lower() for e in eq) or any("gym" in e.lower() for e in eq)
        has_bands = any("band" in e.lower() for e in eq)
        is_beginner = level == "Beginner"

        upper_ex = [
            ExerciseItem(
                name="Dumbbell Floor Press" if has_dumbbells else ("Incline Push-Ups" if is_beginner else "Standard Floor Push-Ups"),
                muscle_group="Pectorals, Anterior Deltoids, Triceps",
                sets=3 if is_beginner else 4,
                reps_or_duration="8-10 reps" if is_beginner else "10-15 reps",
                rest_seconds=60 if is_beginner else 45,
                instructions="Lower with a controlled 3-second descent, pause slightly, then press upward.",
                beginner_tip="Keep elbows tucked at a 45-degree angle to protect shoulder joints.",
                form_cue="Brace core tight and drive shoulder blades into support.",
            ),
            ExerciseItem(
                name="Bent-Over Dumbbell Row" if has_dumbbells else ("Resistance Band Seated Row" if has_bands else "Prone Y-T-W Raises"),
                muscle_group="Latissimus Dorsi, Rhomboids, Rear Deltoids",
                sets=3,
                reps_or_duration="10-12 reps",
                rest_seconds=60,
                instructions="Hinge at hips with a neutral spine, pull weights toward hip crease, squeezing shoulder blades.",
                beginner_tip="Avoid rounding your upper back; keep chest proud throughout.",
                form_cue="Initiate movement by retracting scapulae before bending elbows.",
            ),
            ExerciseItem(
                name="Dumbbell Overhead Shoulder Press" if has_dumbbells else ("Banded Overhead Press" if has_bands else "Pike Push-Up Hold"),
                muscle_group="Deltoids, Upper Trapezius",
                sets=3,
                reps_or_duration="8-12 reps",
                rest_seconds=60,
                instructions="Press weights vertically until arms are fully extended overhead without arching lower back.",
                beginner_tip="Perform seated if lumbar stabilization feels challenged.",
                form_cue="Squeeze glutes and pull ribs down toward hips.",
            ),
            ExerciseItem(
                name="Plank with Shoulder Taps",
                muscle_group="Transverse Abdominis, Obliques, Shoulders",
                sets=3,
                reps_or_duration="30-45 seconds",
                rest_seconds=45,
                instructions="Hold stable push-up position and tap alternate shoulders with minimal hip sway.",
                beginner_tip="Widen feet stance to create greater lateral stability.",
                form_cue="Imagine balancing a cup of water on your lower back.",
            ),
        ]

        lower_ex = [
            ExerciseItem(
                name="Goblet Squat" if has_dumbbells else "Bodyweight Box/Chair Squat" if is_beginner else "Air Squat with Pause",
                muscle_group="Quadriceps, Gluteus Maximus, Adductors",
                sets=3 if is_beginner else 4,
                reps_or_duration="10-12 reps",
                rest_seconds=60,
                instructions="Stand shoulder-width apart, sit back and down between heels, keeping chest tall.",
                beginner_tip="Tap hips to a chair first to master hip-hinge mechanics.",
                form_cue="Track knees in line with second toes; distribute weight through midfoot.",
            ),
            ExerciseItem(
                name="Dumbbell Romanian Deadlift" if has_dumbbells else ("Resistance Band Good Mornings" if has_bands else "Glute Bridge with Hold"),
                muscle_group="Hamstrings, Gluteus Maximus, Erector Spinae",
                sets=3,
                reps_or_duration="10-12 reps",
                rest_seconds=60,
                instructions="Push hips back toward the wall behind you, maintaining slight knee bend and flat spine.",
                beginner_tip="Stop descending as soon as hips stop moving backward.",
                form_cue="Feel active stretch in hamstrings before snapping hips forward.",
            ),
            ExerciseItem(
                name="Walking Lunges" if not has_dumbbells else "Dumbbell Suitcase Reverse Lunges",
                muscle_group="Quadriceps, Glutes, Hamstrings",
                sets=3,
                reps_or_duration="10 reps per leg",
                rest_seconds=60,
                instructions="Step backward, lowering back knee until inches above floor, keeping front shin vertical.",
                beginner_tip="Reverse lunges place significantly less shear force on the knee cap.",
                form_cue="Keep torso tall and lean slightly forward into the front heel.",
            ),
            ExerciseItem(
                name="Standing Calf Raises",
                muscle_group="Gastrocnemius, Soleus",
                sets=3,
                reps_or_duration="15-20 reps",
                rest_seconds=45,
                instructions="Raise up on balls of feet, hold peak contraction for 1 second, lower slowly.",
                beginner_tip="Hold onto a sturdy wall or doorframe for balance.",
                form_cue="Push evenly through big and little toes.",
            ),
        ]

        cardio_ex = [
            ExerciseItem(
                name="Shadow Boxing / Mountain Climbers",
                muscle_group="Full Body, Cardiovascular System",
                sets=3,
                reps_or_duration="40 seconds on, 20s rest",
                rest_seconds=30,
                instructions="Maintain brisk cadence with controlled rhythmic breathing.",
                beginner_tip="Elevate hands on a bench to reduce wrist and shoulder fatigue.",
                form_cue="Stay light on balls of feet and keep hips level.",
            ),
            ExerciseItem(
                name="High Knee Skips / Low Impact March",
                muscle_group="Hip Flexors, Calves, Cardiovascular",
                sets=3,
                reps_or_duration="45 seconds",
                rest_seconds=30,
                instructions="Drive knees upward synchronously with contralateral arm drive.",
                beginner_tip="March firmly in place if jumping impact bothers knees.",
                form_cue="Maintain tall posture with engaged core.",
            ),
            ExerciseItem(
                name="Deadbug Exercise",
                muscle_group="Deep Anterior Core, Pelvic Stabilizers",
                sets=3,
                reps_or_duration="12 alternating reps",
                rest_seconds=45,
                instructions="Lie supine, extend opposite arm and leg while pressing lower back firmly into mat.",
                beginner_tip="Keep knees bent at 90 degrees without letting spine arch.",
                form_cue="Exhale forcefully as limbs extend away from body.",
            ),
        ]

        return {
            "Upper Body & Core Foundation": upper_ex,
            "Lower Body & Posterior Chain": lower_ex,
            "Cardiovascular Conditioning & Core": cardio_ex,
            "Functional Push/Pull Dynamics": upper_ex,
            "Total Body Metabolic Circuit": upper_ex[:2] + lower_ex[:2],
            "Endurance & Core Stability": cardio_ex + [upper_ex[3]],
            "default": upper_ex[:2] + lower_ex[:2],
        }

    def _get_fallback_tips(self, goal: str, level: str) -> List[Dict[str, str]]:
        """Curated high-value fitness insights."""
        return [
            {
                "title": "Progressive Overload Principle",
                "category": "Exercise",
                "description": f"For {level} goals in {goal}, focus on performing each repetition with immaculate control before increasing load or speed.",
            },
            {
                "title": "Electrolyte & Water Balance",
                "category": "Nutrition",
                "description": "Drink a glass of water with a pinch of Himalayan salt 30 minutes pre-session to optimize cellular hydration and prevent cramping.",
            },
            {
                "title": "Neuromuscular Sleep Optimization",
                "category": "Recovery",
                "description": "90% of growth hormone is secreted during deep slow-wave sleep. Keep bedroom cool (18-20°C) and avoid screens 45 minutes before bed.",
            },
            {
                "title": "Consistency Over Intensity",
                "category": "Mindset",
                "description": "Adherence beats perfection every single time. Completing 80% of scheduled workouts consistently beats sporadic 100% effort bursts.",
            },
        ]
