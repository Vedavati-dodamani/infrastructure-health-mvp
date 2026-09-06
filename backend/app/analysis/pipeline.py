import cv2
import numpy as np
from typing import Dict, Any
from . import heuristic_detector, model_detector
from .severity import calc_severity
from .health_score import compute_health


def run_analysis(image_bytes: bytes) -> Dict[str, Any]:
    """
    Central pipeline:
    - decode image
    - try model detector
    - fallback to heuristic detector
    - normalize detections
    - compute per-detection severity
    - compute overall health score and recommendations
    - return structured response
    """
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "invalid image"}
    h, w = img.shape[:2]

    # try model detector
    model_dets = model_detector.detect(img)
    if model_dets is not None:
        analysis_mode = 'model'
        detections = model_dets
    else:
        analysis_mode = 'heuristic_demo'
        detections = heuristic_detector.detect(img)

    # ensure normalized fields and calculate severity
    for d in detections:
        # make sure keys exist
        d.setdefault('confidence', 0.0)
        d.setdefault('label', 'surface_damage')
        if 'bounding_box' not in d and 'box' in d:
            x,y,ww,hh = d['box']
            d['bounding_box'] = {'x': x, 'y': y, 'width': ww, 'height': hh}
        d.setdefault('area_percentage', 0.0)
        d['severity'] = calc_severity(d)

    # compute health
    health = compute_health(detections, (h,w))

    return {
        'analysis_mode': analysis_mode,
        'detections': detections,
        'health_score': health['health_score'],
        'status': health['status'],
        'recommendations': health['recommendations'],
        'image_shape': [int(h), int(w)]
    }
