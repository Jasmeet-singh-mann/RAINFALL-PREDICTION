"""
RainCast AI - Database Layer (SQLite)
Manages persistent records for rainfall predictions, climate chat history, and generated reports.
"""

import sqlite3
import datetime
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config import DB_PATH, DATABASE_DIR


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        forecast_year INTEGER NOT NULL,
        predicted_rainfall REAL NOT NULL,
        model_name TEXT NOT NULL,
        historical_avg REAL NOT NULL,
        anomaly_pct REAL NOT NULL,
        classification TEXT NOT NULL,
        confidence_lower REAL,
        confidence_upper REAL,
        ai_explanation TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        session_id TEXT,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        language TEXT DEFAULT 'English',
        state_context TEXT,
        district_context TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        report_title TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        forecast_year INTEGER NOT NULL,
        file_format TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def save_prediction(data: Dict[str, Any]) -> int:
    """Inserts a new prediction record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO predictions (
            timestamp, state, district, forecast_year, predicted_rainfall,
            model_name, historical_avg, anomaly_pct, classification,
            confidence_lower, confidence_upper, ai_explanation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        data.get("state", "Unknown"),
        data.get("district", "Unknown"),
        int(data.get("forecast_year", 2025)),
        float(data.get("predicted_rainfall", 0.0)),
        data.get("model_name", "Random Forest Regressor"),
        float(data.get("historical_avg", 0.0)),
        float(data.get("anomaly_pct", 0.0)),
        data.get("classification", "Normal"),
        float(data.get("confidence_lower", 0.0)),
        float(data.get("confidence_upper", 0.0)),
        data.get("ai_explanation", "")
    ))
    conn.commit()
    rec_id = cursor.lastrowid
    conn.close()
    return rec_id


def get_recent_predictions(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves the most recent predictions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_chat_message(role: str, message: str, language: str = "English", session_id: str = "default",
                      state_context: Optional[str] = None, district_context: Optional[str] = None):
    """Saves a single chat message turn."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_history (
            timestamp, session_id, role, message, language, state_context, district_context
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now_str, session_id, role, message, language, state_context, district_context))
    conn.commit()
    conn.close()


def get_session_chat_history(session_id: str = "default", limit: int = 30) -> List[Dict[str, Any]]:
    """Retrieves conversational turns for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message, timestamp, language FROM chat_history WHERE session_id = ? ORDER BY id ASC LIMIT ?",
        (session_id, limit)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def log_report_generation(title: str, state: str, district: str, year: int, file_format: str):
    """Logs report download actions."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO report_logs (timestamp, report_title, state, district, forecast_year, file_format)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (now_str, title, state, district, year, file_format))
    conn.commit()
    conn.close()


# Auto-initialize database on import
init_db()

