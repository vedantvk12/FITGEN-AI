"""
Analytics and visualization component for FITGEN AI.
Renders daily training volume distributions, muscle targeting split, and session metrics.
"""

import streamlit as st
import pandas as pd
from models.workout_schema import WeeklyWorkoutPlan
from utils.helpers import calculate_plan_metrics


def render_workout_analytics(plan: WeeklyWorkoutPlan):
    """Render analytical graphs and physiological breakdown for a plan."""
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">
                Weekly Volume & Physiology
            </div>
            <h2 style="margin: 0; font-weight: 800; color: #FFFFFF;">Training Analytics</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = calculate_plan_metrics(plan)

    # 3 Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Total Weekly Volume",
            value=f"{metrics['total_minutes']} mins",
            delta=f"{round(metrics['total_minutes'] / 60, 1)} hrs",
        )
    with m2:
        st.metric(
            label="Active Workout Days",
            value=f"{metrics['training_days']} Days",
            delta="Training Stimulus",
        )
    with m3:
        st.metric(
            label="Recovery & Rest Days",
            value=f"{metrics['recovery_days']} Days",
            delta="Tissue Repair",
        )
    with m4:
        st.metric(
            label="Total Exercises Programmed",
            value=f"{metrics['total_exercises']}",
            delta="Compound & Isolation",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<div style='font-weight: 700; font-size: 0.95rem; color: #F8FAFC; margin-bottom: 0.5rem;'>Daily Active Time (Minutes)</div>",
            unsafe_allow_html=True,
        )
        # Daily duration dataframe
        df_daily = pd.DataFrame(metrics["daily_breakdown"])
        if not df_daily.empty:
            df_chart = df_daily.set_index("Day")[["Minutes"]]
            st.bar_chart(df_chart, color="#00FF87", height=280)
        else:
            st.info("No daily metrics available.")

    with col2:
        st.markdown(
            "<div style='font-weight: 700; font-size: 0.95rem; color: #F8FAFC; margin-bottom: 0.5rem;'>Target Muscle Group Frequency</div>",
            unsafe_allow_html=True,
        )
        muscle_dict = metrics.get("muscle_distribution", {})
        if muscle_dict:
            df_muscle = pd.DataFrame(
                list(muscle_dict.items()),
                columns=["Muscle Group", "Exercise Count"],
            ).sort_values("Exercise Count", ascending=True)

            df_muscle_chart = df_muscle.set_index("Muscle Group")
            st.bar_chart(df_muscle_chart, color="#38BDF8", height=280)
        else:
            st.info("No exercise muscle groups detected for chart.")

    # Physiological adaptation notes
    st.markdown(
        f"""
        <div style="background: rgba(18, 24, 36, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
            <div style="font-weight: 700; color: #00FF87; font-size: 0.9rem; margin-bottom: 0.5rem;">
                🧬 Targeted Biomechanical Adaptations ({plan.fitness_goal})
            </div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.5;">
                This routine features a <b>{plan.weekly_summary.split_type}</b> split targeting <b>{plan.weekly_summary.total_workout_days} active training days</b> 
                interleaved with <b>{plan.weekly_summary.total_recovery_days} days of systemic recovery</b>. By pacing volume over 
                {plan.daily_time_minutes}-minute daily blocks, the routine optimizes mechanical tension while maintaining metabolic waste clearance.
            </div>
            <div style="margin-top: 0.75rem; display: flex; gap: 8px; flex-wrap: wrap;">
                {"".join(f'<span class="badge-tag badge-lime">{b}</span>' for b in plan.weekly_summary.key_benefits)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
