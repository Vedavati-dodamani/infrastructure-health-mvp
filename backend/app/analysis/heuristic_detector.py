import cv2
import numpy as np
from typing import List, Dict


def detect(img: np.ndarray) -> List[Dict]:
    """
    Heuristic/OpenCV-based detector.
    Input: BGR image as numpy ndarray (H, W, 3)
    Output: list of normalized detections:
      {"label": "surface_damage", "confidence": 0.8, "bounding_box": {x,y,width,height}, "area_percentage": 1.2}
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray.shape
    detections = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 200:
            continue
        x,y,ww,hh = cv2.boundingRect(cnt)
        size_ratio = (ww*hh) / (w*h)
        confidence = min(0.95, 0.2 + size_ratio*10)
        # classify generically as surface damage
        if area > 2000 or size_ratio > 0.02:
            label = "surface_damage"
        elif area > 1000:
            label = "concrete_damage"
        else:
            label = "crack"
        det = {
            "label": label,
            "confidence": float(round(float(confidence), 2)),
            "bounding_box": {"x": int(x), "y": int(y), "width": int(ww), "height": int(hh)},
            "area_percentage": float(round((ww*hh)/(w*h)*100.0, 3))
        }
        detections.append(det)
    return detections
