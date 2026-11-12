"""
RainCast AI - Backend Service Launcher
Allows running the FastAPI application directly from the backend package.
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

for p in [str(PROJECT_ROOT), str(BACKEND_DIR), str(FRONTEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import uvicorn
from api import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print("🌦️  RainCast AI - Climate Intelligence Platform")
    print("    Backend Service Launcher (FastAPI)")
    print("=" * 65)
    print(f" -> Local Server: http://localhost:{port}")
    print(f" -> Interactive API Docs: http://localhost:{port}/docs")
    print("=" * 65)
    uvicorn.run(app, host=host, port=port)

