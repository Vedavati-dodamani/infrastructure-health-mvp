from typing import List, Dict, Tuple


def compute_health(detections: List[Dict], image_shape: Tuple[int,int]) -> Dict:
    """
    Compute an overall health score (0-100), a status, and recommendations.

    Heuristic approach (MVP):
    - Start from 100
    - For each detection subtract an impact based on severity, area_percentage, and confidence
    - Use decay to ensure multiple small detections accumulate
    """
    score = 100.0
    total_impact = 0.0
    for d in detections:
        sev = d.get('severity', 'Low')
        conf = float(d.get('confidence', 0.0))
        area_pct = float(d.get('area_percentage', 0.0))

        sev_weight = {'Low': 2.0, 'Medium': 6.0, 'High': 15.0, 'Critical': 30.0}.get(sev, 5.0)
        # impact scales with area and confidence
        impact = sev_weight * (0.5 + conf) * (1.0 + area_pct/10.0)
        total_impact += impact
    # diminish returns scaling for many items
    score -= min(95.0, total_impact)
    score = max(0.0, min(100.0, score))
    score_int = int(round(score))
    if score_int > 70:
        status = 'Healthy'
    elif score_int > 40:
        status = 'Needs Attention'
    else:
        status = 'Critical'

    recommendations = []
    if status == 'Critical':
        recommendations.append('Immediate engineering inspection recommended. Consider closing or restricting access if structural risk is suspected.')
    elif status == 'Needs Attention':
        recommendations.append('Schedule a detailed inspection and monitor the location. Plan for repairs as needed.')
    else:
        recommendations.append('No immediate action; continue regular monitoring and periodic inspection.')

    return {"health_score": score_int, "status": status, "recommendations": recommendations}
