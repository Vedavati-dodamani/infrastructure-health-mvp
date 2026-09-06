# Infrastructure Health MVP

This repository contains an MVP for an AI-powered infrastructure health monitoring platform.

Stack
- Backend: FastAPI, Python, OpenCV (simulated detection)
- Frontend: Simple Vite-style static HTML/CSS/JS (no build step for MVP)
- Database: SQLite (SQLAlchemy)

What’s included
- backend/: FastAPI app with upload, analyze, assets and history endpoints
- frontend/: Static frontend with camera capture, upload, simulated live warnings, and map (Leaflet fallback)
- data/: Seeded India asset GeoJSON

Quick start (development)

1. Backend

- Create a virtualenv and install requirements

  python -m venv .venv
  source .venv/bin/activate
  pip install -r backend/requirements.txt

- Copy backend/.env.example to backend/.env and edit if needed
- Run the backend

  uvicorn backend.app.main:app --reload --port 8000

2. Frontend

- Open frontend/index.html in a browser (or serve with a static server)

Notes
- This MVP uses simulated detection (OpenCV contour heuristics) to produce bounding boxes and severity scores. It’s structured so ML models or external APIs can be dropped in later.
- No external keys were provided; the map uses Leaflet + OpenStreetMap by default. To use Google Maps, add VITE_GOOGLE_MAPS_API_KEY to frontend/.env and update the map code.

License: MIT
