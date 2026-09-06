# Infrastructure Health MVP

This repository contains an MVP for an AI-powered infrastructure health monitoring platform.

Analysis modes
- heuristic_demo: OpenCV-based heuristics (default, always available) — useful for demo and environments without a trained model.
- model: Load a trained model placed at backend/app/analysis/models/model.pt (TorchScript) or model.pth (PyTorch). The pipeline will attempt to load the model if PyTorch is installed.

How to add a trained model
1. Install PyTorch in your backend environment (optional):
   pip install torch torchvision
2. Place your model file at backend/app/analysis/models/model.pt or model.pth
3. Restart the backend. API responses will include "analysis_mode": "model" if inference succeeded.

Fallback behavior
- If no model is available or loading fails, the API falls back to the heuristic_demo detector. Heuristic results are explicitly served with analysis_mode: "heuristic_demo".

MVP notes
- This health score and severity classification are visual heuristics for early detection and not a structural engineering certification.

