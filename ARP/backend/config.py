"""
RainCast AI - Central Configuration & Constants
Defines design tokens, paths, IMD meteorological standards, and machine learning configurations.
"""

from pathlib import Path
import os
import sys

# Base directory paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Ensure all primary roots are in sys.path
for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

BASE_DIR = PROJECT_ROOT

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env")
except Exception:
    pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Backend data and model paths
DATA_DIR = BACKEND_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ANNUAL_RAINFALL_PATH = DATA_DIR / "annual_rainfall.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "india_rainfall_cleaned.csv"

MODELS_DIR = BACKEND_DIR / "models"
DATABASE_DIR = BACKEND_DIR / "database"
DB_PATH = DATABASE_DIR / "raincast.db"

# Frontend template & static paths
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATES_DIR = FRONTEND_DIR / "templates"

# Application Metadata
APP_NAME = "RainCast AI"
APP_SUBTITLE = "Intelligent Annual Rainfall Prediction & Climate Analytics Platform"
APP_TAGLINE = "Predict Rainfall. Understand Climate. Prepare for Tomorrow."
APP_VERSION = "2.4.0-Enterprise"
APP_AUTHORS = "Jasmeet Singh Mann • RainCast AI Climate Intelligence Laboratory"

# Design System Color Tokens (Dark Navy & Cyan Theme)
THEME = {
    "bg_primary": "#071525",
    "bg_secondary": "#0D2035",
    "bg_card": "#122A40",
    "border": "#1A3A5A",
    "accent_primary": "#16B8D4",      # Cyan
    "accent_secondary": "#4F9DDA",    # Sky Blue
    "success": "#27C58A",             # Emerald Green
    "warning": "#F4B942",             # Amber Yellow
    "danger": "#E66A72",              # Coral Red
    "text_primary": "#F4F8FC",        # Ice White
    "text_secondary": "#9DB1C5",      # Muted Slate
    "text_muted": "#5C768D",
}

# IMD (India Meteorological Department) Rainfall Categorization Standards
# Deviation from normal (Long Period Average - LPA):
IMD_CATEGORIES = {
    "Large Deficient": {"min": -100.0, "max": -59.5, "color": "#B91C1C", "label": "Large Deficient (< -59%)"},
    "Deficient": {"min": -59.5, "max": -19.5, "color": "#E66A72", "label": "Deficient (-20% to -59%)"},
    "Normal": {"min": -19.5, "max": 19.5, "color": "#27C58A", "label": "Normal (-19% to +19%)"},
    "Excess": {"min": 19.5, "max": 59.5, "color": "#4F9DDA", "label": "Excess (+20% to +59%)"},
    "Large Excess": {"min": 59.5, "max": 999.0, "color": "#16B8D4", "label": "Large Excess (>= +60%)"},
}

# Machine Learning Settings
HISTORICAL_START_YEAR = 1901
HISTORICAL_END_YEAR = 2026
DEFAULT_FORECAST_HORIZON = 5 # 1-5 years ahead (2027 to 2031+)
RANDOM_STATE = 42

FEATURE_COLS = [
    "rainfall_lag_1",
    "rainfall_lag_2",
    "rainfall_lag_3",
    "rolling_mean_5",
    "rolling_mean_10",
    "rolling_std_5",
    "anomaly_lag_1",
    "latitude",
    "longitude",
    "monsoon_share_lag_1"
]

TARGET_COL = "annual_rainfall"

# Chronological Train-Val-Test Splits (Up to 2026 ending)
SPLIT_TRAIN_END = 2006
SPLIT_VAL_END = 2016
SPLIT_TEST_START = 2017

# Available Model Types
MODEL_NAMES = [
    "Random Forest Regressor",
    "Extra Trees Regressor",
    "XGBoost Regressor",
    "HistGradientBoosting Regressor"
]

# Official IMD Disclaimer
SCIENTIFIC_DISCLAIMER = (
    "RainCast AI delivers experimental empirical and machine-learning based annual rainfall projections "
    "developed for research, climate risk analysis, and academic demonstration. These projections are NOT "
    "official operational meteorological forecasts. For statutory weather warnings and official seasonal "
    "monsoon outlooks, please consult the India Meteorological Department (IMD), Ministry of Earth Sciences, "
    "Government of India (https://mausam.imd.gov.in)."
)

