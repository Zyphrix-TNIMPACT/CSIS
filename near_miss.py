from utils import calculate_distance, check_overlap

def detect_near_miss(person_bboxes, vehicle_bboxes, distance_threshold=150):
    """
    Check if any person is too close to any vehicle (distance < threshold)
    but they are not colliding (no overlap of bounding boxes).
    """
    near_misses = []
    
    for p_bbox in person_bboxes:
        for v_bbox in vehicle_bboxes:
            dist = calculate_distance(p_bbox, v_bbox)
            overlap = check_overlap(p_bbox, v_bbox)
            
            if dist < distance_threshold and not overlap:
                near_misses.append({
                    "person": p_bbox,
                    "vehicle": v_bbox,
                    "distance": dist
                })
                
    return len(near_misses) > 0, near_misses
