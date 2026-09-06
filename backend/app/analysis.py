import io
import cv2
import numpy as np
from typing import Any, Dict, List


def analyze_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Simulated damage detection using OpenCV contour heuristics.
    Returns a dict with detected boxes, confidence, severity, health_score, and recommendations.
    """
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "invalid image"}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    # dilate to close gaps
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    h, w = gray.shape
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 200:  # skip tiny
            continue
        x,y,ww,hh = cv2.boundingRect(cnt)
        # heuristics for confidence & severity
        size_ratio = (ww*hh) / (w*h)
        confidence = min(0.95, 0.2 + size_ratio*10)
        if area > 2000 or size_ratio > 0.02:
            severity = "high"
        elif area > 800:
            severity = "medium"
        else:
            severity = "low"
        detections.append({
            "box": [int(x), int(y), int(ww), int(hh)],
            "area": float(area),
            "confidence": round(float(confidence), 2),
            "severity": severity,
            "type": "crack_or_surface_damage"
        })

    # derive health score: 100 - weighted impact
    score = 100
    for d in detections:
        sev_weight = {"low": 5, "medium": 15, "high": 35}[d["severity"]]
        size_impact = min(1.0, d["area"]/ (w*h) * 1000)
        score -= sev_weight * size_impact
    score = max(0, int(score))
    status = "Healthy" if score > 70 else ("Needs Attention" if score > 40 else "Critical")
    recommendations = []
    if score <= 40:
        recommendations.append("Immediate inspection by a structural engineer recommended.")
    elif score <= 70:
        recommendations.append("Schedule inspection and monitoring. Consider localized repairs.")
    else:
        recommendations.append("No immediate action required; retain monitoring schedule.")

    return {
        "detections": detections,
        "health_score": score,
        "status": status,
        "recommendations": recommendations,
        "image_shape": [int(h), int(w)]
    }
