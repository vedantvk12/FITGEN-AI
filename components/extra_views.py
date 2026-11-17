"""
Additional View Components for FITGEN AI.
Renders Fitness Tips, Saved Workout History, and Academic Viva Preparation.
"""

import streamlit as st
import pandas as pd
from config.settings import settings
from database.history import (
    get_all_plans,
    get_plan_by_id,
    delete_plan_by_id,
    clear_history,
    get_history_stats,
)
from utils.export_pdf import generate_workout_pdf
from core.workout_generator import WorkoutGenerator


def render_fitness_tips_view(generator: WorkoutGenerator, is_demo_mode: bool):
    """Render interactive AI fitness tips and science explorer."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">
                Evidence-Based Guidance
            </div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF;">AI Fitness & Lifestyle Tips</h2>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Generate actionable nutrition, training mechanics, and neuro-recovery micro-habits tailored to your profile.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tcol1, tcol2, tcol3 = st.columns([2, 2, 1.5])
    with tcol1:
        tip_goal = st.selectbox("Focus Goal", options=settings.FITNESS_GOALS, index=0)
    with tcol2:
        tip_level = st.selectbox("Experience Tier", options=settings.FITNESS_LEVELS, index=0)
    with tcol3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        gen_tips_btn = st.button("💡 Generate Tips", type="primary", use_container_width=True)

    if gen_tips_btn or "cached_tips" not in st.session_state:
        with st.spinner("Synthesizing evidence-based fitness recommendations..."):
            tips = generator.generate_fitness_tips(tip_goal, tip_level, is_demo_mode=is_demo_mode)
            st.session_state["cached_tips"] = tips

    tips_to_show = st.session_state.get("cached_tips", [])
    if tips_to_show:
        cols = st.columns(len(tips_to_show) if len(tips_to_show) <= 4 else 2)
        cat_colors = {
            "Exercise": "#00FF87",
            "Nutrition": "#38BDF8",
            "Recovery": "#F59E0B",
            "Mindset": "#A78BFA",
        }
        for idx, tip in enumerate(tips_to_show):
            cat = tip.get("category", "General")
            accent = cat_colors.get(cat, "#00FF87")
            col = cols[idx % len(cols)]
            with col:
                st.markdown(
                    f"""
                    <div class="stat-card" style="border-top: 3px solid {accent}; height: 100%; margin-bottom: 1rem;">
                        <span class="badge-tag" style="background: rgba(255,255,255,0.06); color: {accent}; margin-bottom: 0.5rem;">
                            {cat}
                        </span>
                        <div style="font-weight: 800; font-size: 1rem; color: #FFFFFF; margin-bottom: 0.5rem;">
                            {tip.get('title', 'Guideline')}
                        </div>
                        <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.5;">
                            {tip.get('description', '')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_history_view(on_load_plan=None):
    """Render saved workout routine records from local SQLite."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">
                SQLite Database Records
            </div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF;">Saved Workout History</h2>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Locally persisted plans generated during your sessions. Inspect past plans or export to PDF anytime.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_history_stats()
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Total Saved Routines", stats["total_plans"])
    with sc2:
        st.metric("Most Popular Goal", stats["top_goal"])
    with sc3:
        st.metric("Avg Daily Session", f"{stats['avg_minutes']} min")
    with sc4:
        st.metric("Primary Tier", stats["top_level"])

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    records = get_all_plans(limit=50)
    if not records:
        st.info("No routine records found in SQLite history. Generate a routine from the Routine Planner tab to save it here.")
        return

    # Render table of records
    for row in records:
        plan_id = row["plan_id"]
        with st.container():
            st.markdown(
                f"""
                <div class="stat-card" style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">
                                {row['plan_title']}
                            </div>
                            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">
                                Date: <b style="color: #F8FAFC;">{row['created_at'][:19].replace('T', ' ')}</b> • Goal: <b style="color: #00FF87;">{row['fitness_goal']}</b> • Level: <b style="color: #38BDF8;">{row['fitness_level']}</b> • Duration: {row['daily_time_minutes']} min/day
                            </div>
                            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">
                                Equipment: {row['equipment_list']} • Plan ID: <span style="font-family: monospace;">{plan_id[:8]}...</span>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
            with btn_col1:
                if st.button(f"📥 Load Plan ({plan_id[:8]})", key=f"load_{plan_id}", use_container_width=True):
                    full_plan = get_plan_by_id(plan_id)
                    if full_plan and on_load_plan:
                        on_load_plan(full_plan)
                        st.success("Plan loaded into Routine Planner!")
                        st.rerun()
            with btn_col2:
                # PDF quick download
                full_plan = get_plan_by_id(plan_id)
                if full_plan:
                    pdf_bytes = generate_workout_pdf(full_plan)
                    st.download_button(
                        f"📄 PDF ({plan_id[:8]})",
                        data=pdf_bytes,
                        file_name=f"FITGEN_{row['fitness_goal'].replace(' ', '_')}_{plan_id[:6]}.pdf",
                        mime="application/pdf",
                        key=f"dl_{plan_id}",
                        use_container_width=True,
                    )
            with btn_col3:
                if st.button(f"🗑️ Delete", key=f"del_{plan_id}", use_container_width=True):
                    delete_plan_by_id(plan_id)
                    st.success("Deleted record.")
                    st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    if st.button("⚠️ Clear Entire History Database", type="secondary"):
        clear_history()
        st.success("Workout history successfully reset.")
        st.rerun()


def render_academic_view():
    """Render university project details and viva voce revision guide."""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <div class="hero-badge">University Final-Year B.Tech Mini Project</div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF;">Problem Statement 55 Documentation</h2>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Complete academic metadata, architectural overview, and viva examination defense notes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="stat-card" style="margin-bottom: 1rem;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #00FF87; margin-bottom: 0.75rem;">
                    🎓 Student & Academic Profile
                </div>
                <table style="width: 100%; font-size: 0.85rem; color: #CBD5E1; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Student Name:</td>
                        <td style="padding: 6px 0; font-weight: 700; color: #FFFFFF;">{settings.ACADEMIC_STUDENT}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Roll Number:</td>
                        <td style="padding: 6px 0; font-weight: 700; color: #00FF87;">{settings.ACADEMIC_ROLL}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Class / Degree:</td>
                        <td style="padding: 6px 0;">{settings.ACADEMIC_CLASS}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Problem Statement:</td>
                        <td style="padding: 6px 0; font-weight: 700; color: #38BDF8;">Problem Statement {settings.ACADEMIC_PROBLEM_STMT}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Project Domain:</td>
                        <td style="padding: 6px 0;">Generative AI / Large Language Model Application</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-card" style="margin-bottom: 1rem;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #38BDF8; margin-bottom: 0.75rem;">
                    ⚙️ Technical Stack & Architecture
                </div>
                <table style="width: 100%; font-size: 0.85rem; color: #CBD5E1; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">LLM Runtime:</td>
                        <td style="padding: 6px 0; font-weight: 700; color: #FFFFFF;">Ollama Local Engine</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Primary Model:</td>
                        <td style="padding: 6px 0; font-weight: 700; color: #00FF87;">Llama 3.2 (Configurable)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Frontend:</td>
                        <td style="padding: 6px 0;">Streamlit with Custom Dark Theme</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Validation:</td>
                        <td style="padding: 6px 0;">Pydantic v2 Strict JSON Schema</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; color: #94A3B8;">Database & Export:</td>
                        <td style="padding: 6px 0;">SQLite (Local History) + ReportLab (PDF)</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Core Problem Statement Specification
    st.markdown(
        """
        <div style="background: rgba(18, 24, 36, 0.95); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 800; font-size: 1rem; color: #FFFFFF; margin-bottom: 0.5rem;">
                📋 Problem Statement 55 Compliance Matrix
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.85rem; color: #CBD5E1;">
                <div>
                    <b style="color: #00FF87;">Required Inputs:</b>
                    <ul style="margin: 4px 0 0 16px; padding: 0;">
                        <li>Fitness Goal (Weight Mgmt, Muscle Building, Strength, etc.)</li>
                        <li>Fitness Level (Beginner, Intermediate, Advanced)</li>
                        <li>Available Minutes per Day (15 to 90 min)</li>
                        <li>Available Equipment (Bodyweight, Dumbbells, Bands, etc.)</li>
                    </ul>
                </div>
                <div>
                    <b style="color: #38BDF8;">Required Outputs:</b>
                    <ul style="margin: 4px 0 0 16px; padding: 0;">
                        <li>Weekly workout schedule (Complete 7-day periodization)</li>
                        <li>Exercise names with anatomical muscle groups</li>
                        <li>Sets, repetitions / duration, and rest intervals</li>
                        <li>Recovery and active rest days</li>
                        <li>General fitness recommendations (nutrition, sleep, safety)</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Viva Voce Q&A Expander
    with st.expander("🎓 Final Viva Voce Examiner Questions & Model Answers", expanded=True):
        st.markdown(
            """
            **Q1: Why did you choose Ollama and Llama 3.2 over cloud-based APIs like OpenAI or Gemini for this application?**
            > **Answer:** Ollama allows running open-weights LLMs entirely on-device with zero cloud API costs, no external latency, and complete user data privacy. Llama 3.2 was chosen for its exceptional instruction-following capability in constrained parameter budgets, making it fast and lightweight for consumer machines while reliably returning structured JSON.

            **Q2: How does FITGEN AI prevent LLM hallucinations or broken outputs from crashing the user experience?**
            > **Answer:** We implemented a multi-stage defensive engineering pipeline:
            > 1. Strict system prompting with few-shot schema cues.
            > 2. Ollama JSON mode enforcement (`format: 'json'`).
            > 3. Regex-based JSON cleaner to remove code fences and trailing commas.
            > 4. Pydantic v2 data models with validators for schedule completeness (7 days), realistic set/rep ranges, and day type normalization.
            > 5. Graceful exception handling that never shows raw stack traces to the end user.

            **Q3: How is recovery programmed into the weekly schedule?**
            > **Answer:** Training stimuli require systemic recovery for myofibrillar protein synthesis and central nervous system replenishment. Beginners receive 2 to 3 rest/active recovery days, while intermediate and advanced trainees receive 1 to 2 recovery days, preventing overtraining syndrome.

            **Q4: How does the application maintain security and state?**
            > **Answer:** No secrets or credentials are hardcoded. Configurations are decoupled via `.env`. Routine history uses parameterized SQLite queries to prevent SQL injection, and all operations operate entirely on local disk.
            """
        )
