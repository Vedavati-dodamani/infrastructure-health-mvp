from pydantic import BaseModel
from typing import List, Any

class Detection(BaseModel):
    box: List[int]
    area: float
    confidence: float
    severity: str
    type: str

class AnalyzeResponse(BaseModel):
    detections: List[Detection]
    health_score: int
    status: str
    recommendations: List[str]

class UploadResponse(BaseModel):
    id: str
    filename: str
    analysis: Any
