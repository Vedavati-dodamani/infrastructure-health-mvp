from typing import Dict


def calc_severity(detection: Dict) -> str:
    """
    Determine severity label for a single detection.
    Returns one of: Low, Medium, High, Critical
    Logic considers confidence, area_percentage, and label.
    """
    conf = detection.get('confidence', 0.0)
    area = detection.get('area_percentage', 0.0)
    label = detection.get('label', '').lower()

    # base score
    score = 0.0
    score += conf * 50.0
    score += min(area, 50.0)

    # label-specific modifiers (structural defects are considered more severe)
    if any(k in label for k in ['structural', 'collapse', 'critical']):
        score += 20
    if 'pothole' in label:
        score += 5
    if 'crack' in label and area > 3.0:
        score += 10

    if score >= 70:
        return 'Critical'
    if score >= 50:
        return 'High'
    if score >= 30:
        return 'Medium'
    return 'Low'
