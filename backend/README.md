# Backend README (extended)

This backend implements the analysis pipeline for the Infrastructure Health MVP.

Analysis modes
- heuristic_demo: OpenCV-based contour heuristics used as a fallback and for demo purposes. It detects contours likely to be cracks or surface damage and returns normalized detections.
- model: When a trained model file is present in backend/app/analysis/models/ and PyTorch is available, the model detector will load it and attempt inference. The system expects the model to either be a TorchScript model or a PyTorch model that returns detection outputs in a familiar format (dict with 'boxes','scores','labels' or a list with such dicts).

Model placement & configuration
- Place your trained model in: backend/app/analysis/models/
  Supported filenames: model.pt, model.pth
- The model_detector will attempt to load a TorchScript model via torch.jit.load first, then fall back to torch.load.
- The model is loaded on CPU by default. For large models or GPU usage adapt the code accordingly.

Fallback behavior
- If no model file exists or loading fails (e.g., PyTorch not installed), the pipeline uses the heuristic_demo (OpenCV) detector and returns analysis_mode: "heuristic_demo".
- Heuristic detections are explicitly labeled as heuristic and not presented as AI model predictions.

How model inference works (MVP)
- The pipeline decodes the uploaded image into a numpy BGR image.
- model_detector.detect(img) will attempt to load the model and run inference. It normalizes outputs into the standard detection format.
- If model detection fails or is not available, heuristic_detector.detect(img) is called.

Standardized detection format
Each detection is a JSON object with the following keys:
{
  "label": "crack",
  "confidence": 0.87,
  "bounding_box": {"x": 120, "y": 80, "width": 200, "height": 140},
  "area_percentage": 12.5,
  "severity": "High"
}

Health scoring & severity
- Per-detection severity is calculated using confidence, area percentage, and damage label.
- Overall health score (0-100) aggregates per-detection impacts with diminishing returns for many detections. Status is one of: Healthy, Needs Attention, Critical.
- The README and docs include the note: this is an MVP visual-risk heuristic and not an engineering structural certification.

Adding a trained model later
1. Install PyTorch in your backend environment (not added to default requirements to keep install lightweight):
   pip install torch torchvision
2. Place your model file at backend/app/analysis/models/model.pt (or model.pth).
3. Ensure the model returns outputs compatible with torchvision detection outputs (dict with 'boxes','scores','labels') or a list where the first element is such a dict.
4. Restart the backend. The pipeline will detect the model and use analysis_mode: "model".

Limitations
- The model integration code makes reasonable effort to support common PyTorch detection models, but model input/output shapes vary. You may need to adapt model_detector.py for your exact model signature.
- No authentication or quota management is implemented.

