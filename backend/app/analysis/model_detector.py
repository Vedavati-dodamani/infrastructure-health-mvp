import os
from typing import List, Dict, Optional
import numpy as np

MODEL_PATH_POSSIBILITIES = [
    os.path.join(os.path.dirname(__file__), "models", "model.pt"),
    os.path.join(os.path.dirname(__file__), "models", "model.pth"),
]

_model = None
_model_available = None


def _model_file_path() -> Optional[str]:
    for p in MODEL_PATH_POSSIBILITIES:
        if os.path.exists(p):
            return p
    return None


def _try_load_model():
    global _model, _model_available
    if _model_available is not None:
        return _model_available
    path = _model_file_path()
    if path is None:
        _model_available = False
        return False
    try:
        import torch
        # attempt to load TorchScript first
        try:
            _model = torch.jit.load(path, map_location='cpu')
        except Exception:
            # fallback to torch.load
            _model = torch.load(path, map_location='cpu')
        _model.eval()
        _model_available = True
        return True
    except Exception:
        _model_available = False
        return False


def detect(img: np.ndarray) -> Optional[List[Dict]]:
    """
    Attempts to run a trained model. If no model is present or loading fails, returns None.
    The function expects the model (if provided) to return detections in one of the common forms:
      - a list of dicts with keys: boxes (N,4), labels (N,), scores (N,)
      - a torchvision-style dict with 'boxes','labels','scores'
    The function will normalize those outputs into the standard detection dict format.
    """
    if not _try_load_model():
        return None
    try:
        import torch
        # Convert BGR numpy image to RGB and to tensor
        img_rgb = img[:, :, ::-1]
        tensor = torch.from_numpy(img_rgb).permute(2,0,1).float() / 255.0
        tensor = tensor.unsqueeze(0)  # batch
        with torch.no_grad():
            out = _model(tensor)
        # normalize different model output shapes
        detections = []
        # handle torchvision/faster-rcnn style (list of dicts)
        if isinstance(out, (list, tuple)):
            out0 = out[0]
            boxes = out0.get('boxes') if isinstance(out0, dict) else None
            scores = out0.get('scores') if isinstance(out0, dict) else None
            labels = out0.get('labels') if isinstance(out0, dict) else None
            if boxes is not None:
                boxes = boxes.cpu().numpy()
                scores = scores.cpu().numpy() if scores is not None else [0.0]*len(boxes)
                labels = labels.cpu().numpy() if labels is not None else [0]*len(boxes)
                h, w, _ = img.shape
                for i, b in enumerate(boxes):
                    x1, y1, x2, y2 = b
                    bx = int(x1); by = int(y1); bw = int(x2-x1); bh = int(y2-y1)
                    area_pct = (bw*bh)/(w*h)*100.0
                    detections.append({
                        'label': str(int(labels[i])),
                        'confidence': float(float(scores[i])),
                        'bounding_box': {'x': bx, 'y': by, 'width': bw, 'height': bh},
                        'area_percentage': float(round(area_pct,3))
                    })
                return detections
        # else: try dict with tensors
        if isinstance(out, dict):
            boxes = out.get('boxes')
            scores = out.get('scores')
            labels = out.get('labels')
            if boxes is not None:
                boxes = boxes.cpu().numpy()
                scores = scores.cpu().numpy() if scores is not None else [0.0]*len(boxes)
                labels = labels.cpu().numpy() if labels is not None else [0]*len(boxes)
                h, w, _ = img.shape
                for i, b in enumerate(boxes):
                    x1, y1, x2, y2 = b
                    bx = int(x1); by = int(y1); bw = int(x2-x1); bh = int(y2-y1)
                    area_pct = (bw*bh)/(w*h)*100.0
                    detections.append({
                        'label': str(int(labels[i])),
                        'confidence': float(float(scores[i])),
                        'bounding_box': {'x': bx, 'y': by, 'width': bw, 'height': bh},
                        'area_percentage': float(round(area_pct,3))
                    })
                return detections
        # If we get here, model returned an unexpected type — return None to trigger fallback
        return None
    except Exception:
        return None
