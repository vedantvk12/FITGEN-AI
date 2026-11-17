# FITGEN AI — Intelligent Fitness Routine Planner
### Elite-Level AI Physical Conditioning & Periodized Routine Planner
**Academic Final-Year Project — Problem Statement 55**

---

## 🎓 Academic Credentials

- **Project Title:** FITGEN AI – Intelligent Fitness Routine Planner
- **Problem Statement Number:** 55
- **Student Name:** Vedant Kirange
- **Roll Number:** 55
- **Class / Branch:** B.Tech Computer Science & Engineering – AI & Analytics
- **Domain:** Generative AI / Large Language Model Application
- **Frontend Framework:** Streamlit
- **LLM Engine:** Ollama Local Runtime (`llama3.2` default, fully configurable)

---

## 💡 Product Vision & Brand Identity

**Tagline:** *Train Smarter. Move Better. Live Stronger.*

FITGEN AI is a commercial-grade, privacy-first personal fitness routine synthesis application. Unlike basic prompt wrappers, FITGEN AI employs local large language model inference (Llama 3.2 via Ollama) paired with Pydantic schema validation, evidence-based periodization logic, SQLite database persistence, and ReportLab executive PDF generation.

Designed with an electric cyberpunk / modern SaaS visual design language:
- Premium dark interface (`#0B0E14` charcoal & `#121824` dark card slate)
- High-contrast electric lime (`#00FF87`) and sky cyan (`#38BDF8`) accents
- Clean typography, subtle gradients, and reactive cards
- Periodized 7-day schedule with distinct active training, active recovery, and rest days

---

## 🌟 Key Features

1. **Intelligent Constraint Capture:**
   - 🎯 **Fitness Goal:** Weight Management, Muscle Building, Strength Development, General Fitness, Endurance, Flexibility & Mobility.
   - 📊 **Fitness Level:** Beginner, Intermediate, Advanced.
   - ⏱️ **Workout Duration:** 15, 20, 30, 45, 60 minutes/day.
   - 🏋️ **Equipment Profiles:** Bodyweight (No Equipment), Dumbbells, Resistance Bands, Yoga Mat, Full Home Gym, or Custom.
   - ⚙️ **Biomechanical Preferences:** Training frequency (3-6 days/week), target muscle focus, and physical limitations to avoid.

2. **Defensive AI Engine & Pydantic Validation:**
   - Zero hallucinations or unformatted outputs.
   - Strict JSON mode schema enforcement with fallback regex cleaning for code fences and trailing commas.
   - Responsible AI safety directives: Rejects dangerous exercises, never diagnoses injuries, flags severe medical limitations for physician clearance.

3. **Interactive 7-Day Routine Dashboard:**
   - Day-by-day tabs with session type tags (Training, Active Recovery, Rest).
   - Dynamic warm-up drills, structured exercise sets, reps/duration, rest intervals, beginner form cues, and parasympathetic cool-downs.

4. **Biomechanical & Volume Analytics:**
   - Real-time weekly training time distribution chart.
   - Target muscle group volume frequency chart.
   - Key physiological adaptation summary.

5. **Executive PDF Export:**
   - Generates professional multi-page vector PDF routines via ReportLab.
   - Includes student academic headers/footers, metadata tables, exercise breakdown, and clinical safety warnings.

6. **SQLite Local Workout History:**
   - Fully persistent storage for all generated routines.
   - Reload past routines into the planner with one click, or export to PDF anytime.

7. **Dual-Mode Architecture (Ollama + Evaluation Mode):**
   - Seamlessly uses local Ollama daemon when running.
   - Features an "Offline / Demonstration Mode" toggle enabling full UI, charts, and PDF evaluation even if Ollama is paused during an examiner viva.

---

## 🏗️ System Architecture

```
fitgen-ai/
│
├── app.py                      # Main Streamlit application entrypoint & routing
├── requirements.txt            # Production dependencies
├── README.md                   # Comprehensive project documentation
├── ACADEMIC_REPORT.md          # 2-Page university submission procedure report
├── .env.example                # Environment variable configuration template
├── .gitignore                  # Git repository exclusion rules
│
├── .streamlit/
│   └── config.toml             # Custom dark fitness-tech theme configuration
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Global application constants and settings
│
├── core/
│   ├── __init__.py
│   ├── ollama_client.py        # Ollama local REST client with retry and error handling
│   ├── prompt_engine.py        # System prompt, safety directives, and schema formatting
│   ├── workout_generator.py    # Orchestration of AI generation, fallback, and demo logic
│   └── validators.py           # Pydantic schema validation & LLM JSON cleaning
│
├── models/
│   ├── __init__.py
│   └── workout_schema.py       # Pydantic models (WeeklyWorkoutPlan, DayWorkout, ExerciseItem)
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite connection manager and DDL schemas
│   └── history.py              # Parameterized CRUD operations and history analytics
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py              # Navigation, Ollama status monitor, and model picker
│   ├── dashboard.py            # Hero section, workflow cards, and configuration form
│   ├── workout_cards.py        # 7-day schedule tabs, exercise cards, and action toolbar
│   ├── charts.py               # Training volume and muscle split charts (pandas/Streamlit)
│   └── extra_views.py          # AI tips, SQLite history browser, and Viva Q&A
│
├── utils/
│   ├── __init__.py
│   ├── export_pdf.py           # ReportLab PDF generator with academic header/footer
│   └── helpers.py              # Badge renderers, formatting, and metric calculators
│
├── assets/
│   ├── logo.svg                # Vector brand identity mark
│   └── custom.css              # Custom dark cyberpunk fitness styling rules
│
└── tests/
    ├── __init__.py
    ├── test_validators.py       # JSON extraction, schema checks, and constraint validation
    ├── test_prompts.py          # Prompt engineering and safety directive tests
    ├── test_ollama_client.py    # Mocked connection, timeout, and 404 tests
    ├── test_workout_generator.py# 5 Mandatory academic test configurations + mocked LLM
    ├── test_db_history.py       # SQLite CRUD lifecycle tests
    └── test_pdf_export.py       # ReportLab PDF byte integrity tests
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Ollama:** Installed locally ([ollama.com](https://ollama.com))

### 2. Clone or Enter Project Directory
```bash
cd "d:\FITGEN AI"
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Default parameters in `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=90
OLLAMA_TEMPERATURE=0.2
```

### 5. Pull Ollama Model
Ensure Ollama is running and download the configured Llama 3.2 model:
```bash
ollama serve
ollama pull llama3.2
```

### 6. Launch FITGEN AI
```bash
streamlit run app.py
```
The application will launch automatically at: `http://localhost:8501`.

---

## 🧪 Automated Testing

The project includes a comprehensive Pytest suite containing 29 automated tests covering input validation, schema enforcement, mocked Ollama network handling, SQLite CRUD, PDF generation, and all 5 mandatory university test configurations.

Run all tests:
```bash
python -m pytest -v
```

### Mandatory Academic Test Configurations Verified:
| Test ID | Experience Tier | Target Goal | Daily Duration | Equipment Available | Status |
|:---:|:---|:---|:---:|:---|:---:|
| **Test 1** | Beginner | General Fitness | 20 mins | No Equipment (Bodyweight) | ✅ PASSED |
| **Test 2** | Beginner | Weight Management | 30 mins | Yoga Mat | ✅ PASSED |
| **Test 3** | Intermediate | Strength Development | 45 mins | Dumbbells | ✅ PASSED |
| **Test 4** | Intermediate | Flexibility and Mobility | 20 mins | No Equipment (Bodyweight) | ✅ PASSED |
| **Test 5** | Advanced | Endurance | 60 mins | Full Home Gym | ✅ PASSED |

---

## 🛡️ Security & Reliability Standards

- **Zero Hardcoded Secrets:** Configuration driven entirely by environment variables and `.env`.
- **SQL Injection Defense:** All SQLite interactions use parameterized queries (`?`).
- **Data Privacy:** Runs 100% locally on device. No biometric or user data is ever transmitted to third-party clouds.
- **Defensive Error Handling:** Friendly, actionable error banners guide users through Ollama installation, model pulls, and network timeouts without raw tracebacks.

---

## 🔮 Limitations & Future Enhancements

### Current Limitations:
- Local LLM generation latency is dependent on host machine CPU/GPU capabilities.
- Complex anatomical modifications require explicit text prompts.

### Future Enhancements:
- Computer Vision real-time exercise form tracking via webcam (MediaPipe Pose).
- Wearable integration (Apple HealthKit / Google Health Connect) for live heart rate load syncing.
- Multi-week macrocycle periodization (auto-deload weeks).

---

## 👨‍💻 Author & Academic Submission

**Vedant Kirange**  
Roll Number: **55**  
B.Tech Computer Science & Engineering – AI & Analytics  
Problem Statement 55: **FITGEN AI – Intelligent Fitness Routine Planner**
