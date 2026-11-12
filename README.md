# RainCast AI — Annual Rainfall Prediction & Climate Analytics

**Predict Rainfall. Understand Climate. Prepare for Tomorrow.**

RainCast AI is a web-based climate analytics project that explores annual rainfall patterns across India using historical rainfall data, machine-learning regression models, interactive visualizations, and a generative-AI climate assistant. It is designed as an academic and experimental decision-support tool for understanding rainfall trends—not as a replacement for official weather forecasts or warnings.

## Features

- Annual rainfall prediction with selectable regression models.
- Historical rainfall exploration and interactive charts.
- Model comparison and evaluation views.
- An AI climate assistant powered by Google Gemini, when an API key is configured.
- English, Hindi, and Punjabi interface/assistant language support.
- PDF report generation and CSV data export.
- FastAPI endpoints and automatically generated API documentation.

## Technology Stack

- **Backend:** Python, FastAPI, Uvicorn, Jinja2
- **Machine learning:** scikit-learn, XGBoost
- **Data processing:** Pandas, NumPy, SciPy
- **Visualization:** Plotly, HTML, CSS, JavaScript, Tailwind CSS
- **AI assistant:** Google Gemini API (google-genai)
- **Reports and storage:** ReportLab, SQLite

## Project Structure

```text
.
├── app.py
├── backend/
│   ├── api.py
│   ├── config.py
│   ├── data/
│   ├── models/
│   ├── database/
│   ├── src/
│   └── tests/
├── frontend/
│   ├── static/
│   └── templates/
├── requirements.txt
├── Procfile
└── runtime.txt
```

## Run Locally

1. Install Python 3.11.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your own Gemini API key. The key is optional for the core web application but required for Gemini-powered assistant responses.
5. Start the application:

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

6. Open `http://localhost:8000`. API documentation is available at `/docs`.

## Environment Variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for the AI assistant |
| `HOST` | Host interface for the local server (default: `0.0.0.0`) |
| `PORT` | Server port (default: `8000`) |

Never commit `.env` or publish API keys. Use `.env.example` as a template and configure secrets through your hosting provider's environment settings.

## Data and Forecast Disclaimer

RainCast AI predictions are experimental, model-based estimates for learning, analysis, and demonstration. Data sources, coverage periods, preprocessing assumptions, and model evaluation results should be checked in the accompanying project documentation before using outputs in research or operational decisions. For official forecasts, warnings, and advisories, consult the India Meteorological Department (IMD).
