"""
RainCast AI - Modern Climate Intelligence Web Platform
Primary FastAPI + HTML5 + Tailwind CSS Web Application Server.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import uvicorn
from backend.api import app

# Export app object for ASGI servers (Uvicorn / Gunicorn / Render / Docker)
__all__ = ["app"]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print("🌦️  RainCast AI - Modern Climate Intelligence Web Platform")
    print("    FastAPI + HTML5 + Tailwind CSS Architecture")
    print("=" * 65)
    print(f" -> Local Web Application: http://localhost:{port}")
    print(f" -> Interactive API Docs:  http://localhost:{port}/docs")
    print("=" * 65)
    uvicorn.run(app, host=host, port=port)
