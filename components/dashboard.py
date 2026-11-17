"""
Dashboard component for FITGEN AI.
Renders hero section, configuration form, and workflow explanation cards.
"""

import streamlit as st
from config.settings import settings


def render_hero():
    """Render branded hero banner with academic metadata."""
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="hero-badge">AI-Powered Personal Routine Engine</div>
                    <div class="hero-title">{settings.APP_NAME} <span style="color: #00FF87; font-size: 1.2rem; font-weight: 600;">v{settings.VERSION}</span></div>
                    <div class="hero-subtitle">{settings.TAGLINE}</div>
                </div>
                <div class="academic-pill">
                    <span>🎓 Problem Statement {settings.ACADEMIC_PROBLEM_STMT}</span>
                    <span>•</span>
                    <span>{settings.ACADEMIC_STUDENT} (Roll {settings.ACADEMIC_ROLL})</span>
                </div>
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; color: #94A3B8; max-width: 850px; line-height: 1.6;">
                Engineered for university demonstration and everyday fitness optimization. FITGEN AI integrates local
                LLM intelligence (Llama 3.2 via Ollama) to synthesize periodized 7-day training routines complete with warm-ups,
                exact sets, reps, rest intervals, and physiological recovery strategies.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_it_works():
    """Render 3-step workflow explanation cards."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.25rem;">
                Methodology & Workflow
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 1rem;">
                How FITGEN AI Synthesizes Your Routine
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem;">
                <div class="stat-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
                    <div style="font-weight: 700; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.25rem;">1. Constraint Capture</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.4;">
                        Specify fitness goal, experience level, daily time budget, and available equipment.
                    </div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🧠</div>
                    <div style="font-weight: 700; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.25rem;">2. Local LLM Reasoning</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.4;">
                        Ollama Llama 3.2 processes biomechanical prompts to build a 7-day periodized schedule with recovery balance.
                    </div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📄</div>
                    <div style="font-weight: 700; color: #FFFFFF; font-size: 1rem; margin-bottom: 0.25rem;">3. Structured Output & PDF</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.4;">
                        Pydantic validates the JSON schedule. Inspect sets, reps, form cues, and export to an executive PDF dossier.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_configuration_form(existing_prefs=None) -> tuple:
    """
    Render workout configuration inputs adhering to Problem Statement 55.
    Returns: (submitted: bool, reset_clicked: bool, preferences_dict)
    """
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div>
                <span style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">Input Parameters</span>
                <h3 style="margin: 0; font-weight: 800; color: #FFFFFF;">Configure Your Routine</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("workout_config_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        # 1. Fitness Goal (Core Input)
        with col1:
            default_goal_idx = 1  # Muscle Building default
            if existing_prefs and existing_prefs.get("fitness_goal") in settings.FITNESS_GOALS:
                default_goal_idx = settings.FITNESS_GOALS.index(existing_prefs["fitness_goal"])

            fitness_goal = st.selectbox(
                "1. Fitness Goal *",
                options=settings.FITNESS_GOALS,
                index=default_goal_idx,
                help="Select the primary physiological adaptation to target.",
            )

        # 2. Fitness Level (Core Input)
        with col2:
            default_level_idx = 0  # Beginner default
            if existing_prefs and existing_prefs.get("fitness_level") in settings.FITNESS_LEVELS:
                default_level_idx = settings.FITNESS_LEVELS.index(existing_prefs["fitness_level"])

            fitness_level = st.selectbox(
                "2. Fitness Level *",
                options=settings.FITNESS_LEVELS,
                index=default_level_idx,
                help="Determines exercise complexity, volume, and recovery demands.",
            )

        col3, col4 = st.columns(2)

        # 3. Available Workout Time (Core Input)
        with col3:
            time_val = existing_prefs.get("available_time", 30) if existing_prefs else 30
            available_time = st.slider(
                "3. Available Workout Time (Minutes / Day) *",
                min_value=15,
                max_value=90,
                value=int(time_val),
                step=5,
                help="Select available time per workout session.",
            )

        # 4. Available Equipment (Core Input)
        with col4:
            default_eq = ["No Equipment (Bodyweight)"]
            if existing_prefs and existing_prefs.get("equipment"):
                default_eq = [e for e in existing_prefs["equipment"] if e in settings.EQUIPMENT_OPTIONS]
                if not default_eq:
                    default_eq = ["No Equipment (Bodyweight)"]

            equipment = st.multiselect(
                "4. Available Equipment *",
                options=settings.EQUIPMENT_OPTIONS,
                default=default_eq,
                help="Select all equipment you have access to. Select 'No Equipment' for bodyweight only.",
            )

        # Additional Preferences Expander (Optional)
        with st.expander("⚙️ Additional Preferences & Physical Considerations (Optional)", expanded=False):
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                days_per_week = st.slider(
                    "Preferred Training Frequency (Days/Week)",
                    min_value=3,
                    max_value=6,
                    value=int(existing_prefs.get("preferred_days_per_week", 4)) if existing_prefs else 4,
                    help="Active training days out of 7. The remaining days will be programmed as recovery.",
                )
                target_areas = st.multiselect(
                    "Target Focus Areas",
                    options=["Full Body", "Upper Body", "Lower Body", "Core & Abs", "Cardio Conditioning", "Mobility & Posture"],
                    default=["Full Body"],
                    help="Optional muscle or conditioning focus.",
                )
            with exp_col2:
                limitations = st.text_input(
                    "Movements to Avoid / General Limitations",
                    value=existing_prefs.get("limitations", "None") if existing_prefs else "None",
                    placeholder="e.g. knee-friendly, avoid jumping, lower back sensitivity",
                    help="AI will replace high-strain movements with safe alternatives.",
                )
                notes = st.text_input(
                    "Custom Notes for AI",
                    value=existing_prefs.get("notes", "") if existing_prefs else "",
                    placeholder="e.g. preference for circuit training or short warmups",
                )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            submitted = st.form_submit_button(
                "⚡ Generate My Workout Routine",
                type="primary",
                use_container_width=True,
            )
        with btn_col2:
            reset_clicked = st.form_submit_button(
                "🔄 Reset",
                use_container_width=True,
            )

    prefs = {
        "fitness_goal": fitness_goal,
        "fitness_level": fitness_level,
        "available_time": available_time,
        "equipment": equipment if equipment else ["No Equipment (Bodyweight)"],
        "preferred_days_per_week": days_per_week,
        "target_areas": target_areas,
        "limitations": limitations,
        "notes": notes,
    }

    return submitted, reset_clicked, prefs
