# Backend README

Run the backend locally:

- Create virtualenv and install:
  python -m venv .venv
  source .venv/bin/activate
  pip install -r backend/requirements.txt

- Copy backend/.env.example to backend/.env
- Start server:
  uvicorn backend.app.main:app --reload --port 8000

API endpoints
- GET /health
- POST /upload/image (multipart form file)
- GET /assets
- GET /history
