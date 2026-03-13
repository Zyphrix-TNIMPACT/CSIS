import numpy as np
import random

def calculate_center(bbox):
    """Calculate the center (x, y) of a bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def calculate_distance(bbox1, bbox2):
    """Calculate the Euclidean distance between the centers of two bounding boxes."""
    c1 = calculate_center(bbox1)
    c2 = calculate_center(bbox2)
    return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def check_overlap(bbox1, bbox2):
    """Check if two bounding boxes overlap."""
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # If one rectangle is on left side of other
    if x1_1 >= x2_2 or x1_2 >= x2_1:
        return False
    # If one rectangle is above other
    if y1_1 >= y2_2 or y1_2 >= y2_1:
        return False
    return True

def simulate_event(event_type):
    """
    Simulate an emergency event for the IERRE module.
    event_type can be 'Fall', 'Fire', 'Security Breach'
    """
    events = {
        "Fall": "🚨 Fall detected -> Medical Alert + Notify Supervisor",
        "Fire": "🔥 Fire detected -> Trigger Alarm + Evacuation",
        "Security Breach": "🥷 Theft/Security breach -> Silent Alert + Security Notification"
    }
    return events.get(event_type, "Unknown event")
