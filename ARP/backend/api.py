"""
RainCast AI - FastAPI Application Engine
Serves high-performance REST APIs and renders modern HTML5 + Tailwind CSS web interfaces.
"""

import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import io
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, Request, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_NAME, APP_TAGLINE, APP_VERSION, APP_SUBTITLE,
    MODEL_NAMES, PROCESSED_DATA_PATH, MODELS_DIR
)
from src.prediction import (
    predict_annual_rainfall, get_cached_dataset, load_model_metadata, get_model
)
from src.genai_assistant import (
    generate_prediction_explanation, chat_with_climate_assistant
)
from src.model_evaluation import (
    get_model_comparison_dataframe, get_test_predictions_and_residuals, get_feature_importances
)
from src.report_generator import generate_pdf_report
from database.db import (
    save_prediction, get_recent_predictions, save_chat_message, log_report_generation
)

app = FastAPI(
    title=f"{APP_NAME} Enterprise API",
    description="High-performance climate analytics and annual rainfall prediction platform for India.",
    version=APP_VERSION
)

# Enable CORS for external API clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static and Templates
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))


# Pydantic Request Models
class PredictRequest(BaseModel):
    state: str
    district: str
    forecast_year: int = 2027
    model_name: str = "Random Forest Regressor"
    language: str = "English"

class ChatRequest(BaseModel):
    message: str
    language: str = "English"
    history: List[Dict[str, str]] = []


# =====================================================================
# HTML Web Page Routes
# =====================================================================

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    df = get_cached_dataset()
    meta = load_model_metadata()
    return templates.TemplateResponse(request=request, name="index.html", context={
        "active_page": "home",
        "total_records": len(df),
        "total_entities": df["location"].nunique(),
        "best_model": meta.get("best_model", "HistGradientBoosting Regressor")
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    df = get_cached_dataset()
    states = sorted(df["state"].unique())
    default_state = "Punjab" if "Punjab" in states else states[0]
    default_districts = sorted(df[df["state"] == default_state]["district"].unique())
    default_district = "Ludhiana" if "Ludhiana" in default_districts else default_districts[0]

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "active_page": "dashboard",
        "states": states,
        "default_state": default_state,
        "default_districts": default_districts,
        "default_district": default_district
    })


@app.get("/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    df = get_cached_dataset()
    states = sorted(df["state"].unique())
    default_state = "Punjab" if "Punjab" in states else states[0]
    default_districts = sorted(df[df["state"] == default_state]["district"].unique())
    default_district = "Ludhiana" if "Ludhiana" in default_districts else default_districts[0]

    return templates.TemplateResponse(request=request, name="predict.html", context={
        "active_page": "predict",
        "states": states,
        "default_state": default_state,
        "default_districts": default_districts,
        "default_district": default_district,
        "models": MODEL_NAMES
    })


@app.get("/assistant", response_class=HTMLResponse)
async def assistant_page(request: Request):
    return templates.TemplateResponse(request=request, name="assistant.html", context={
        "active_page": "assistant"
    })


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    comp_df = get_model_comparison_dataframe()
    meta = load_model_metadata()
    best_name = meta.get("best_model", "")

    rows = []
    for _, r in comp_df.iterrows():
        rows.append({
            "name": r.get("Model", ""),
            "val_mae": r.get("Val MAE (mm)", 0),
            "val_r2": r.get("Val R²", 0),
            "test_mae": r.get("Test MAE (mm)", 0),
            "test_r2": r.get("Test R²", 0),
            "improvement": r.get("Improvement vs Mean (%)", 0),
            "is_best": (r.get("Model", "") == best_name)
        })

    return templates.TemplateResponse(request=request, name="models.html", context={
        "active_page": "models",
        "comparison_rows": rows
    })


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    df = get_cached_dataset()
    states = sorted(df["state"].unique())
    default_state = "Punjab" if "Punjab" in states else states[0]
    default_districts = sorted(df[df["state"] == default_state]["district"].unique())
    default_district = "Ludhiana" if "Ludhiana" in default_districts else default_districts[0]
    recent_logs = get_recent_predictions(limit=15)

    return templates.TemplateResponse(request=request, name="reports.html", context={
        "active_page": "reports",
        "states": states,
        "default_state": default_state,
        "default_districts": default_districts,
        "default_district": default_district,
        "models": MODEL_NAMES,
        "audit_logs": recent_logs
    })


# =====================================================================
# REST API Endpoints
# =====================================================================

@app.get("/api/districts/{state}")
async def get_districts(state: str):
    df = get_cached_dataset()
    districts = sorted(df[df["state"] == state]["district"].unique())
    return districts


@app.get("/api/dashboard-data")
async def get_dashboard_data(state: str = Query(...), district: str = Query(...)):
    df = get_cached_dataset()
    dist_df = df[(df["state"] == state) & (df["district"] == district)].sort_values(by="year")
    if dist_df.empty:
        dist_df = df[df["state"] == state].sort_values(by="year")
    
    if dist_df.empty:
        raise HTTPException(status_code=404, detail=f"No observations found for {state} - {district}")

    years = dist_df["year"].tolist()
    annual_series = dist_df["annual_rainfall"].tolist()
    ma5_series = dist_df["annual_rainfall"].rolling(5, min_periods=1).mean().round(1).tolist()
    lpa_normal = float(dist_df["lpa_normal"].iloc[-1])
    latest_annual = float(dist_df["annual_rainfall"].iloc[-1])
    latest_anomaly_pct = float(dist_df["anomaly_pct"].iloc[-1])
    latest_category = str(dist_df["imd_category"].iloc[-1])
    rainy_days = int(dist_df["rainy_days"].iloc[-1])

    # 12-month climatological normal profile
    m_cols = [
        "jan_rainfall", "feb_rainfall", "mar_rainfall", "apr_rainfall",
        "may_rainfall", "jun_rainfall", "jul_rainfall", "aug_rainfall",
        "sep_rainfall", "oct_rainfall", "nov_rainfall", "dec_rainfall"
    ]
    monthly_means = dist_df[m_cols].mean().round(1).tolist()
    anomalies_pct = dist_df["anomaly_pct"].tolist()

    return {
        "years": years,
        "annual_series": annual_series,
        "ma5_series": ma5_series,
        "lpa_normal": lpa_normal,
        "latest_annual": latest_annual,
        "latest_anomaly_pct": latest_anomaly_pct,
        "latest_category": latest_category,
        "rainy_days": rainy_days,
        "monthly_means": monthly_means,
        "anomalies_pct": anomalies_pct
    }


@app.post("/api/predict")
async def api_predict(req: PredictRequest):
    try:
        pred_res = predict_annual_rainfall(
            state=req.state,
            district=req.district,
            forecast_year=req.forecast_year,
            model_name=req.model_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate AI explanation
    ai_text = generate_prediction_explanation(pred_res, language=req.language)
    pred_res["ai_explanation"] = ai_text

    # Log to SQLite
    try:
        save_prediction({
            "state": req.state,
            "district": req.district,
            "forecast_year": req.forecast_year,
            "predicted_rainfall": pred_res.get("predicted_rainfall_mm", 0.0),
            "model_name": req.model_name,
            "historical_avg": pred_res.get("normal_lpa_mm", 0.0),
            "anomaly_pct": pred_res.get("anomaly_pct", 0.0),
            "classification": pred_res.get("classification", "Normal"),
            "confidence_lower": pred_res.get("confidence_lower", 0.0),
            "confidence_upper": pred_res.get("confidence_upper", 0.0),
            "ai_explanation": ai_text
        })
    except Exception as log_err:
        print(f"Notice: Failed to log prediction: {log_err}")

    # Add historical trajectory for chart
    df = get_cached_dataset()
    dist_df = df[(df["state"] == req.state) & (df["district"] == req.district)].sort_values(by="year")
    if dist_df.empty:
        dist_df = df[df["state"] == req.state].sort_values(by="year")
    recent_df = dist_df.tail(12) # last 12 years (2014-2025)
    pred_res["history_years"] = recent_df["year"].tolist()
    pred_res["history_rainfalls"] = recent_df["annual_rainfall"].tolist()

    return pred_res


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    # Format history tuples
    hist_list = []
    for h in req.history:
        role = h.get("role", "")
        content = h.get("content", "")
        if role and content:
            hist_list.append({"role": role, "message": content})

    response_text = chat_with_climate_assistant(
        user_message=req.message,
        session_history=hist_list,
        language=req.language
    )

    try:
        save_chat_message("user", req.message)
        save_chat_message("assistant", response_text)
    except Exception:
        pass

    return {"response": response_text}


@app.get("/api/model-diagnostics")
async def api_diagnostics(model_name: str = Query("Random Forest Regressor")):
    eval_df, _ = get_test_predictions_and_residuals(model_name)
    actuals = [round(float(v), 1) for v in eval_df["actual"].tolist()]
    predictions = [round(float(v), 1) for v in eval_df["predicted"].tolist()]
    residuals = [round(float(v), 1) for v in eval_df["residual"].tolist()]

    imp_df = get_feature_importances(model_name)
    feature_names = imp_df["Feature"].tolist()
    importance_scores = [round(float(v), 4) for v in imp_df["Importance"].tolist()]

    return {
        "actuals": actuals,
        "predictions": predictions,
        "residuals": residuals,
        "feature_names": feature_names,
        "importance_scores": importance_scores
    }


@app.get("/api/export/pdf")
async def export_pdf(
    state: str = Query(...),
    district: str = Query(...),
    forecast_year: int = Query(2027),
    model_name: str = Query("Random Forest Regressor")
):
    try:
        pdf_bytes = generate_pdf_report(
            state=state,
            district=district,
            forecast_year=forecast_year,
            model_name=model_name
        )
        try:
            log_report_generation(
                title="Executive Climate Report",
                state=state,
                district=district,
                year=forecast_year,
                file_format="PDF"
            )
        except Exception:
            pass

        filename = f"RainCast_Executive_Report_{district}_{forecast_year}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {e}")


@app.get("/api/export/csv")
async def export_csv():
    if not PROCESSED_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Processed dataset file not found.")
    return FileResponse(
        path=PROCESSED_DATA_PATH,
        media_type="text/csv",
        filename="india_rainfall_cleaned_1901_2026.csv"
    )

