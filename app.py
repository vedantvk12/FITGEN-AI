"""
FITGEN AI — Intelligent Fitness Routine Planner
Main Streamlit Application Entrypoint
Problem Statement 55 | Student: Vedant Kirange (Roll 55) | B.Tech CSE (AI & Analytics)
"""

from pathlib import Path
import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="FITGEN AI — Intelligent Fitness Routine Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Core imports
from config.settings import settings
from core.ollama_client import OllamaClient, OllamaConnectionError, OllamaModelNotFoundError, OllamaTimeoutError, OllamaError
from core.workout_generator import WorkoutGenerator
from core.validators import validate_user_preferences, ValidationError
from database.db import init_db
from database.history import save_workout_plan
from components.sidebar import render_sidebar
from components.dashboard import render_hero, render_configuration_form, render_how_it_works
from components.workout_cards import render_workout_plan_view
from components.charts import render_workout_analytics
from components.extra_views import render_fitness_tips_view, render_history_view, render_academic_view


def load_custom_css():
    """Inject custom dark fitness-tech styling."""
    css_path = Path(__file__).resolve().parent / "assets" / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def main():
    # 1. Initialize local SQLite Database
    init_db()

    # 2. Inject CSS
    load_custom_css()

    # 3. Instantiate Ollama Client & Engine
    ollama_client = OllamaClient(
        base_url=settings.OLLAMA_BASE_URL,
        default_model=settings.OLLAMA_MODEL,
        timeout=settings.OLLAMA_TIMEOUT,
    )
    generator = WorkoutGenerator(ollama_client=ollama_client)

    # 4. Session State Management
    if "current_plan" not in st.session_state:
        st.session_state["current_plan"] = None
    if "last_prefs" not in st.session_state:
        st.session_state["last_prefs"] = None
    if "show_modify" not in st.session_state:
        st.session_state["show_modify"] = False

    # 5. Render Sidebar Navigation & Settings
    sidebar_state = render_sidebar(ollama_client)
    active_view = sidebar_state["view"]
    selected_model = sidebar_state["model"]
    is_demo_mode = sidebar_state["is_demo_mode"]

    # 6. View Routing
    if active_view == "🏋️ Routine Planner":
        render_hero()

        # If user clicked Modify or no plan is generated yet, show configuration form
        if st.session_state["current_plan"] is None or st.session_state["show_modify"]:
            render_how_it_works()

            submitted, reset_clicked, prefs_dict = render_configuration_form(
                existing_prefs=st.session_state["last_prefs"]
            )

            if reset_clicked:
                st.session_state["current_plan"] = None
                st.session_state["last_prefs"] = None
                st.session_state["show_modify"] = False
                st.rerun()

            if submitted:
                # Validate user inputs against Problem Statement 55 rules
                is_valid, err_msg, validated_prefs = validate_user_preferences(prefs_dict)

                if not is_valid:
                    st.error(f"❌ {err_msg}")
                else:
                    st.session_state["last_prefs"] = prefs_dict
                    spinner_msg = (
                        f"🧠 Synthesizing 7-day periodized routine with {selected_model} via Ollama..."
                        if not is_demo_mode
                        else "⚡ Synthesizing evidence-based 7-day routine in Evaluation Mode..."
                    )

                    with st.spinner(spinner_msg):
                        try:
                            plan = generator.generate_plan(
                                preferences=validated_prefs,
                                model=selected_model,
                                is_demo_mode=is_demo_mode,
                            )
                            st.session_state["current_plan"] = plan
                            st.session_state["show_modify"] = False
                            st.success("✨ 7-Day Workout Routine synthesized and validated successfully!")
                            st.rerun()

                        except OllamaConnectionError as e:
                            st.error(
                                f"🔌 **Ollama Connection Failed**: Could not reach local Ollama daemon at `{settings.OLLAMA_BASE_URL}`.\n\n"
                                f"**How to resolve:**\n"
                                f"1. Run `ollama serve` in your terminal.\n"
                                f"2. Or toggle **'Offline / Demonstration Mode'** in the sidebar to test all features immediately without a running server."
                            )
                        except OllamaModelNotFoundError as e:
                            st.error(
                                f"⚠️ **Model Not Found**: Model `{selected_model}` is not pulled locally.\n\n"
                                f"**How to resolve:** Run `ollama pull {selected_model}` in your terminal."
                            )
                        except OllamaTimeoutError as e:
                            st.error(f"⏳ **Request Timeout**: Generation took longer than {settings.OLLAMA_TIMEOUT}s. Please retry or simplify preferences.")
                        except ValidationError as e:
                            st.error(f"⚠️ **JSON Validation Error**: The model output could not be strictly validated. Details: {e}")
                        except Exception as e:
                            st.error(f"⚠️ **Unexpected Error**: {str(e)}")

        else:
            # Plan is generated and active: render 7-day schedule view
            def handle_regenerate():
                if st.session_state["last_prefs"]:
                    _, _, validated_prefs = validate_user_preferences(st.session_state["last_prefs"])
                    with st.spinner(f"Regenerating routine with {selected_model}..."):
                        try:
                            new_plan = generator.generate_plan(
                                preferences=validated_prefs,
                                model=selected_model,
                                is_demo_mode=is_demo_mode,
                            )
                            st.session_state["current_plan"] = new_plan
                            st.success("Regenerated plan successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to regenerate: {e}")

            def handle_modify():
                st.session_state["show_modify"] = True
                st.rerun()

            render_workout_plan_view(
                plan=st.session_state["current_plan"],
                on_regenerate=handle_regenerate,
                on_modify=handle_modify,
            )

    elif active_view == "📊 Weekly Analytics":
        render_hero()
        if st.session_state["current_plan"] is not None:
            render_workout_analytics(st.session_state["current_plan"])
        else:
            st.info("🏋️ No active workout routine generated yet. Please generate a routine from the 'Routine Planner' tab to view volume distributions and muscle targeting analytics.")

    elif active_view == "💡 AI Fitness Tips":
        render_hero()
        render_fitness_tips_view(generator, is_demo_mode=is_demo_mode)

    elif active_view == "📂 Saved Routines":
        render_hero()

        def handle_load_plan(plan):
            st.session_state["current_plan"] = plan
            st.session_state["show_modify"] = False
            st.session_state["active_nav_view"] = "🏋️ Routine Planner"

        render_history_view(on_load_plan=handle_load_plan)

    elif active_view == "🎓 Academic Info & Viva":
        render_hero()
        render_academic_view()


if __name__ == "__main__":
    main()
