import cv2

class ZoneModule:
    def __init__(self, hazard_zone_rel, safe_zone_rel):
        """
        hazard_zone_rel: list of tuples or simply a bounding box [x1, y1, x2, y2] in relative coords (0.0 - 1.0)
        safe_zone_rel: [x1, y1, x2, y2] in relative coords
        """
        self.hazard_zone_rel = hazard_zone_rel
        self.safe_zone_rel = safe_zone_rel

    def _get_absolute_coords(self, rel_coords, frame_width, frame_height):
        x1, y1, x2, y2 = rel_coords
        return [
            int(x1 * frame_width),
            int(y1 * frame_height),
            int(x2 * frame_width),
            int(y2 * frame_height)
        ]

    def draw_zones(self, frame):
        """Draw Hazard and Safe zones on the frame."""
        h, w = frame.shape[:2]
        
        # Draw Hazard Zone (Red)
        hx1, hy1, hx2, hy2 = self._get_absolute_coords(self.hazard_zone_rel, w, h)
        
        # Create a transparent overlay for zones (XAI feature)
        overlay = frame.copy()
        cv2.rectangle(overlay, (hx1, hy1), (hx2, hy2), (0, 0, 255), -1)
        # Apply the overlay
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        
        cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), (0, 0, 255), 2)
        cv2.putText(frame, "Hazard Zone", (hx1, hy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Draw Safe Zone (Green) - simple border
        sx1, sy1, sx2, sy2 = self._get_absolute_coords(self.safe_zone_rel, w, h)
        cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), (0, 255, 0), 2)
        cv2.putText(frame, "Safe Zone", (sx1, sy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame

    def check_if_inside_zone(self, person_bbox, zone_rel, frame_width, frame_height):
        """
        Check if the center of a person's bounding box is inside a given relative zone.
        """
        px1, py1, px2, py2 = person_bbox
        zx1, zy1, zx2, zy2 = self._get_absolute_coords(zone_rel, frame_width, frame_height)
        
        # Calculate center of person (specifically lower center for feet placement better represents where they are)
        cx = (px1 + px2) / 2
        cy = py2  # Bottom edge of bounding box is closer to the ground
        
        if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
            return True
        return False
        
    def is_in_hazard_zone(self, person_bbox, frame_width, frame_height):
        return self.check_if_inside_zone(person_bbox, self.hazard_zone_rel, frame_width, frame_height)
