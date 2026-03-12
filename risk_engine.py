def calculate_risk_score(in_hazard_zone, near_vehicle, helmet_missing):
    """
    Calculate risk score based on business rules.
    - Person inside hazard zone → +40
    - Person near moving vehicle → +30
    - Helmet missing → +20
    """
    score = 0
    if in_hazard_zone:
        score += 40
    if near_vehicle:
        score += 30
    if helmet_missing:
        score += 20
        
    return score

def classify_incident(risk_score):
    """
    Risk Levels:
    0–30 → Low
    31–60 → Medium
    61–80 → High
    81+ → Critical
    
    Incident Classification:
    Medium → Warning
    High → Alert
    Critical → Emergency
    """
    if risk_score <= 30:
        level = "Low"
        classification = "Normal"
        alert_msg = "Safe operation"
    elif risk_score <= 60:
        level = "Medium"
        classification = "Warning"
        alert_msg = "Warning: Moderate risk detected."
    elif risk_score <= 80:
        level = "High"
        classification = "Alert"
        alert_msg = "ALERT: High safety risk!"
    else:
        level = "Critical"
        classification = "Emergency"
        alert_msg = "EMERGENCY: Immediate action required! Triggering Protocol."
        
    return level, classification, alert_msg
