# Analysis package wrapper
from .analysis.pipeline import run_analysis


def analyze_image_bytes(image_bytes: bytes):
    """Compatibility wrapper preserved for existing imports.
    Calls the new analysis pipeline and returns a serializable dict.
    """
    return run_analysis(image_bytes)
