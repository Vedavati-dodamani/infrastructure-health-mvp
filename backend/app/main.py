from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .analysis import analyze_image_bytes
from .models import AnalyzeResponse, UploadResponse
from .db import get_session, init_db, Report
import shutil
import uuid
import os
from sqlalchemy.orm import Session

app = FastAPI(title="Infrastructure Health MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ensure uploads dir
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static frontend if present
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../..", "frontend")
if os.path.isdir(STATIC_DIR):
    app.mount("/frontend", StaticFiles(directory=STATIC_DIR), name="frontend")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/upload/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_session)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(400, "Only JPG/PNG images are supported")
    uid = str(uuid.uuid4())
    out_path = os.path.join(UPLOAD_DIR, uid + os.path.splitext(file.filename)[1])
    with open(out_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # analyze
    result = analyze_image_bytes(open(out_path, "rb").read())
    # save minimal report
    report = Report(id=uid, filename=os.path.basename(out_path), result_json=result)
    db.add(report)
    db.commit()
    return {"id": uid, "filename": report.filename, "analysis": result}

@app.get("/assets")
def get_assets():
    # serve seeded assets
    here = os.path.dirname(__file__)
    path = os.path.join(here, "../..", "data", "seeded_india_assets.geojson")
    if os.path.exists(path):
        return open(path, "r").read()
    return {"type":"FeatureCollection", "features": []}

@app.get("/history")
def history(db: Session = Depends(get_session)):
    rows = db.query(Report).order_by(Report.created_at.desc()).limit(200).all()
    out = []
    for r in rows:
        out.append({"id": r.id, "filename": r.filename, "created_at": r.created_at.isoformat(), "result": r.result_json})
    return out
