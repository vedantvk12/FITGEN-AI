"""
Sidebar component for FITGEN AI.
Handles navigation, Ollama connectivity status, model settings, and academic meta.
"""

import streamlit as st
from config.settings import settings
from core.ollama_client import OllamaClient


def render_sidebar(ollama_client: OllamaClient) -> dict:
    """Render sidebar and return active configuration dictionary."""
    with st.sidebar:
        # Academic & Brand Header
        st.markdown(
            f"""
            <div style="padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.5rem; font-weight: 900; color: #FFFFFF; letter-spacing: 1.5px;">FITGEN</span>
                    <span style="background: #00FF87; color: #0B0E14; font-size: 0.75rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">AI</span>
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px; font-weight: 600;">
                    Problem Statement 55 | Roll No: 55
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown(
            "<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.5rem;'>Navigation</div>",
            unsafe_allow_html=True,
        )
        views = [
            "🏋️ Routine Planner",
            "📊 Weekly Analytics",
            "💡 AI Fitness Tips",
            "📂 Saved Routines",
            "🎓 Academic Info & Viva",
        ]
        current_view = st.radio(
            "Select View",
            options=views,
            label_visibility="collapsed",
            key="active_nav_view",
        )

        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 1rem 0;'>", unsafe_allow_html=True)

        # Ollama Health & Model Configuration
        st.markdown(
            "<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.5rem;'>LLM Engine (Ollama)</div>",
            unsafe_allow_html=True,
        )

        # Check or cache Ollama health
        if "ollama_status" not in st.session_state or st.button("🔄 Test Ollama Connection", use_container_width=True):
            with st.spinner("Probing Ollama daemon..."):
                is_online, msg, models = ollama_client.check_health()
                st.session_state["ollama_status"] = is_online
                st.session_state["ollama_msg"] = msg
                st.session_state["ollama_models"] = models

        is_online = st.session_state.get("ollama_status", False)
        status_msg = st.session_state.get("ollama_msg", "Not probed yet")
        installed_models = st.session_state.get("ollama_models", [])

        if is_online:
            st.markdown(
                f"""
                <div class="ollama-pill-online" style="margin-bottom: 0.75rem; display: flex; align-items: center;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00FF87;"></span>
                    <span>Ollama Online</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="ollama-pill-offline" style="margin-bottom: 0.75rem; display: flex; align-items: center;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #EF4444;"></span>
                    <span>Ollama Disconnected</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("🛠️ Ollama Setup Instructions", expanded=False):
                st.markdown(
                    """
                    **To run Ollama locally:**
                    1. Open a terminal and start the server:
                    ```bash
                    ollama serve
                    ```
                    2. Pull the configured model:
                    ```bash
                    ollama pull llama3.2
                    ```
                    3. Refresh connection with the button above.
                    """
                )

        # Model Selection
        model_options = installed_models if installed_models else [settings.OLLAMA_MODEL, "llama3.2", "llama3", "mistral", "custom"]
        if settings.OLLAMA_MODEL not in model_options:
            model_options.insert(0, settings.OLLAMA_MODEL)

        selected_model = st.selectbox(
            "Selected LLM Model",
            options=model_options,
            index=0,
            help="Default model is Llama 3.2. Configurable via OLLAMA_MODEL in .env",
        )

        # Demo Mode Toggle (Crucial for offline evaluation or grading when Ollama daemon is paused)
        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 1rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.5rem;'>Evaluation Mode</div>",
            unsafe_allow_html=True,
        )

        # If Ollama is offline, default demo mode to True to allow testing without crash, but give clear label
        demo_mode_default = not is_online
        is_demo_mode = st.toggle(
            "Offline / Demonstration Mode",
            value=st.session_state.get("demo_mode", demo_mode_default),
            help="Generates deterministic evidence-based routines for testing when Ollama is offline or uninstalled.",
            key="demo_mode_toggle",
        )
        st.session_state["demo_mode"] = is_demo_mode

        if is_demo_mode:
            st.info("⚡ Demo Mode Active: Generates evidence-based routines without requiring a live Ollama server.")

        # Academic Credits Footer
        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 1rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background: rgba(18, 24, 36, 0.8); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px; font-size: 0.75rem; color: #94A3B8;">
                <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 2px;">{settings.ACADEMIC_STUDENT}</div>
                <div>Roll No: <span style="color: #00FF87; font-weight: 600;">{settings.ACADEMIC_ROLL}</span></div>
                <div>{settings.ACADEMIC_CLASS}</div>
                <div style="margin-top: 4px; color: #38BDF8; font-weight: 600;">Problem Statement {settings.ACADEMIC_PROBLEM_STMT}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return {
            "view": current_view,
            "model": selected_model,
            "is_online": is_online,
            "is_demo_mode": is_demo_mode,
        }
