"""
Workout plan visualization component for FITGEN AI.
Renders summary statistics, 7-day schedule tabs, exercise cards, and PDF export trigger.
"""

import streamlit as st
from models.workout_schema import WeeklyWorkoutPlan
from utils.export_pdf import generate_workout_pdf
from utils.helpers import get_day_badge_color, get_muscle_group_icon


def render_workout_plan_view(plan: WeeklyWorkoutPlan, on_regenerate=None, on_modify=None):
    """Render full interactive 7-day workout routine."""
    # Top Action Bar
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 1rem; gap: 10px;">
            <div>
                <div style="font-size: 0.8rem; font-weight: 700; color: #00FF87; text-transform: uppercase; letter-spacing: 1px;">
                    Generated Routine
                </div>
                <h2 style="margin: 0; font-weight: 800; color: #FFFFFF;">{plan.plan_title}</h2>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                    Split: <b style="color: #F8FAFC;">{plan.weekly_summary.split_type}</b> • Target: <b style="color: #38BDF8;">{plan.fitness_goal}</b> ({plan.fitness_level})
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Executive Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Training Days</div>
                <div class="stat-value" style="color: #00FF87;">{plan.weekly_summary.total_workout_days} <span style="font-size: 1rem; color: #94A3B8;">/ 7</span></div>
                <div class="stat-sub">Active Sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Recovery Days</div>
                <div class="stat-value" style="color: #F59E0B;">{plan.weekly_summary.total_recovery_days} <span style="font-size: 1rem; color: #94A3B8;">/ 7</span></div>
                <div class="stat-sub">Active/Rest Days</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Daily Session</div>
                <div class="stat-value" style="color: #38BDF8;">{plan.daily_time_minutes} <span style="font-size: 1rem; color: #94A3B8;">min</span></div>
                <div class="stat-sub">Time Budget</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Weekly Time</div>
                <div class="stat-value" style="color: #FFFFFF;">{plan.weekly_summary.estimated_total_minutes} <span style="font-size: 1rem; color: #94A3B8;">min</span></div>
                <div class="stat-sub">Cumulative Volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Action Toolbar (PDF Export, Regenerate, Modify)
    act_col1, act_col2, act_col3, act_col4 = st.columns([2, 1.5, 1.5, 1.5])

    with act_col1:
        # Generate PDF bytes
        try:
            pdf_bytes = generate_workout_pdf(plan)
            st.download_button(
                label="📥 Download Executive PDF Plan",
                data=pdf_bytes,
                file_name=f"FITGEN_{plan.fitness_goal.replace(' ', '_')}_{plan.fitness_level}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF creation failed: {e}")

    with act_col2:
        if st.button("🔄 Regenerate Routine", use_container_width=True):
            if on_regenerate:
                on_regenerate()

    with act_col3:
        if st.button("✏️ Modify Parameters", use_container_width=True):
            if on_modify:
                on_modify()

    with act_col4:
        st.markdown(
            """
            <div style="height: 100%; display: flex; align-items: center; justify-content: center; background: rgba(0,255,135,0.06); border: 1px solid rgba(0,255,135,0.2); border-radius: 8px; font-size: 0.8rem; color: #00FF87; font-weight: 600; padding: 6px;">
                ✅ Saved in History
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 7-Day Tabs View
    st.markdown(
        "<div style='font-size: 0.9rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.5rem;'>Weekly 7-Day Periodized Schedule:</div>",
        unsafe_allow_html=True,
    )

    tab_titles = [f"Day {d.day_number} ({d.day_name[:3]})" for d in plan.schedule]
    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        day = plan.schedule[i]
        badge_meta = get_day_badge_color(day.day_type)

        with tab:
            # Day Card Container
            st.markdown(
                f"""
                <div class="day-card {day.day_type.lower()}" style="margin-top: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 0.75rem;">
                        <div>
                            <span style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
                                Day {day.day_number} • {day.day_name}
                            </span>
                            <h3 style="margin: 0; font-weight: 800; color: #FFFFFF;">{day.focus}</h3>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="badge-tag" style="background: {badge_meta['bg']}; border: 1px solid {badge_meta['border']}; color: {badge_meta['text']};">
                                {badge_meta['icon']} {badge_meta['label']}
                            </span>
                            <span class="badge-tag" style="background: rgba(255, 255, 255, 0.08); color: #F8FAFC;">
                                ⏱️ {day.estimated_minutes} min
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Warm-up block
            if day.warmup and day.warmup.activities:
                warmup_drills = " • ".join(day.warmup.activities)
                st.markdown(
                    f"""
                    <div style="background: rgba(56, 189, 248, 0.06); border-left: 3px solid #38BDF8; padding: 10px 14px; border-radius: 6px; margin-bottom: 1rem;">
                        <div style="font-weight: 700; color: #38BDF8; font-size: 0.85rem; margin-bottom: 2px;">
                            🔥 Dynamic Warm-Up ({day.warmup.duration_minutes} Minutes)
                        </div>
                        <div style="font-size: 0.85rem; color: #E2E8F0; margin-bottom: 4px;"><b>Drills:</b> {warmup_drills}</div>
                        <div style="font-size: 0.8rem; color: #94A3B8;"><i>{day.warmup.instructions}</i></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Exercise list
            if day.exercises:
                st.markdown(
                    f"<div style='font-size: 0.85rem; font-weight: 700; color: #00FF87; text-transform: uppercase; margin-bottom: 0.5rem;'>Exercises ({len(day.exercises)} Movements)</div>",
                    unsafe_allow_html=True,
                )

                for ex_idx, ex in enumerate(day.exercises):
                    m_icon = get_muscle_group_icon(ex.muscle_group)
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="exercise-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                                    <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">
                                        <span style="color: #00FF87; margin-right: 6px;">{ex_idx + 1}.</span> {ex.name}
                                    </div>
                                    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                                        <span class="badge-tag badge-cyan">{m_icon} {ex.muscle_group}</span>
                                        <span class="badge-tag badge-lime"><b>{ex.sets} Sets</b> × <b>{ex.reps_or_duration}</b></span>
                                        <span class="badge-tag badge-amber">⏱️ {ex.rest_seconds}s Rest</span>
                                    </div>
                                </div>
                                <div style="margin-top: 0.6rem; font-size: 0.85rem; color: #CBD5E1; line-height: 1.45;">
                                    <b>Execution:</b> {ex.instructions}
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.8rem;">
                                    <div style="color: #94A3B8;">
                                        <b style="color: #38BDF8;">💡 Form Cue:</b> {ex.form_cue or 'Maintain controlled tempo'}
                                    </div>
                                    <div style="color: #94A3B8;">
                                        <b style="color: #F59E0B;">⚠️ Safety / Modification:</b> {ex.beginner_tip}
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                # Rest Day visual card
                st.markdown(
                    """
                    <div style="background: rgba(148, 163, 184, 0.05); border: 1px dashed rgba(148, 163, 184, 0.3); border-radius: 8px; padding: 2rem; text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">☕</div>
                        <div style="font-weight: 700; color: #FFFFFF; font-size: 1.1rem; margin-bottom: 0.25rem;">Scheduled Recovery Protocol</div>
                        <div style="color: #94A3B8; font-size: 0.9rem; max-width: 500px; margin: 0 auto;">
                            Physical adaptations occur during rest. Focus on muscular repair, high-protein nutrition, and mental decompression.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Cool-down block
            if day.cooldown and day.cooldown.activities:
                cooldown_drills = " • ".join(day.cooldown.activities)
                st.markdown(
                    f"""
                    <div style="background: rgba(16, 185, 129, 0.06); border-left: 3px solid #10B981; padding: 10px 14px; border-radius: 6px; margin-top: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; color: #10B981; font-size: 0.85rem; margin-bottom: 2px;">
                            🧘 Parasympathetic Cool-Down ({day.cooldown.duration_minutes} Minutes)
                        </div>
                        <div style="font-size: 0.85rem; color: #E2E8F0; margin-bottom: 4px;"><b>Stretches:</b> {cooldown_drills}</div>
                        <div style="font-size: 0.8rem; color: #94A3B8;"><i>{day.cooldown.instructions}</i></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Daily recovery advice
            if day.recovery_recommendation:
                st.markdown(
                    f"""
                    <div style="font-size: 0.8rem; color: #94A3B8; padding: 6px 10px; background: rgba(255, 255, 255, 0.03); border-radius: 4px; margin-top: 6px;">
                        <b style="color: #F8FAFC;">💧 Daily Recovery Action:</b> {day.recovery_recommendation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # General Recommendations Collapsible
    with st.expander("🥗 Holistic Nutrition, Hydration & Progressive Overload Guidelines", expanded=False):
        recs = plan.general_recommendations
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🥦 Nutrition & Hydration")
            for n_tip in recs.nutrition_guidelines:
                st.markdown(f"- {n_tip}")
            st.markdown(f"**Hydration Rule:** {recs.hydration_tip}")
        with c2:
            st.markdown("#### 📈 Overload & Neuro-Recovery")
            st.markdown(f"**Progressive Overload:** {recs.progressive_overload_advice}")
            st.markdown(f"**Sleep & Recovery:** {recs.sleep_and_recovery}")
            st.markdown(f"**Safety Disclaimer:** <span style='color: #F87171;'>{recs.safety_warning}</span>", unsafe_allow_html=True)
