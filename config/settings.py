"""
FITGEN AI - Application Settings & Constants
Academic Project: Problem Statement 55
Author: Vedant Kirange | Roll No: 55 | B.Tech CSE (AI & Analytics)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if available
load_dotenv(BASE_DIR / ".env")


class Settings:
    # Academic and Brand Meta
    APP_NAME: str = "FITGEN AI"
    APP_SUBTITLE: str = "Intelligent Fitness Routine Planner"
    TAGLINE: str = "Train Smarter. Move Better. Live Stronger."
    VERSION: str = "1.0.0"
    ACADEMIC_STUDENT: str = "Vedant Kirange"
    ACADEMIC_ROLL: str = "55"
    ACADEMIC_CLASS: str = "B.Tech CSE – AI & Analytics"
    ACADEMIC_PROBLEM_STMT: str = "55"

    # Ollama LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "90"))
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))

    # Database Configuration
    DATABASE_PATH: Path = BASE_DIR / "database" / "fitgen_history.db"

    # Core Options (Problem Statement 55 Requirements)
    FITNESS_GOALS = [
        "Weight Management",
        "Muscle Building",
        "Strength Development",
        "General Fitness",
        "Endurance",
        "Flexibility and Mobility",
    ]

    FITNESS_LEVELS = [
        "Beginner",
        "Intermediate",
        "Advanced",
    ]

    TIME_OPTIONS = [
        15,
        20,
        30,
        45,
        60,
    ]

    EQUIPMENT_OPTIONS = [
        "No Equipment (Bodyweight)",
        "Dumbbells",
        "Resistance Bands",
        "Yoga Mat",
        "Full Home Gym",
        "Kettlebell",
        "Pull-up Bar",
    ]

    DAYS_OF_WEEK = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Theme & Visual Palette (Cyber Lime & Dark Slate)
    COLOR_PRIMARY = "#00FF87"       # Electric Lime
    COLOR_SECONDARY = "#60A5FA"     # Slate Cyan / Ice Blue
    COLOR_ACCENT = "#38BDF8"        # Sky Accent
    COLOR_BG_DARK = "#0B0E14"       # Deep Charcoal
    COLOR_CARD_BG = "#121824"       # Dark Card Slate
    COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
    COLOR_TEXT_PRIMARY = "#F8FAFC"  # Crisp White
    COLOR_TEXT_MUTED = "#94A3B8"    # Slate Gray
    COLOR_REST = "#94A3B8"          # Rest indicator
    COLOR_ACTIVE_REC = "#F59E0B"    # Amber Recovery
    COLOR_WORKOUT = "#00FF87"       # Neon Green Workout


settings = Settings()
