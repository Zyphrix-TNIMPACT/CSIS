from ultralytics import YOLO
import cv2
import random
import os
import joblib
import numpy as np

class DetectionModule:
    def __init__(self, model_path="yolov8n.pt"):
        # Check for trained custom models
        if os.path.exists("ppe_custom.pt"):
            self.model = YOLO("ppe_custom.pt")
            print("✅ Loaded Custom PPE AI Model.")
        else:
            self.model = YOLO(model_path)
            
        try:
            self.fire_model = joblib.load("fire_model.pkl")
            print("✅ Loaded Custom Fire ML Model.")
        except:
            self.fire_model = None

        # COCO Classes: 0: person, 2: car, 3: motorcycle, 5: bus, 7: truck
        self.vehicle_classes = [2, 3, 5, 7]
        self.person_class = 0
        
        # State to store simulated helmet detection so it doesn't flicker per frame
        self.helmet_state = {}

    def process_frame(self, frame):
        """
        Runs YOLOv8 tracking inference on a frame.
        Returns: annotated_frame, list_of_person_bboxes, list_of_vehicle_bboxes, list_of_helmet_status, incident_triggered
        """
        # Use ByteTrack for object tracking (default in ultralytics)
        results = self.model.track(frame, persist=True, verbose=False)[0]
        
        persons = []
        vehicles = []
        helmets_missing = []
        
        # Automatic IERRE Event Simulation Variables
        incident_triggered = None

        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy() # [x1, y1, x2, y2]
                
                # Get tracker ID if available
                track_id = int(box.id[0]) if box.id is not None else -1
                
                # Confidence threshold
                if conf > 0.4:
                    if cls_id == self.person_class:
                        persons.append(bbox)
                        
                        # Fix Helmet Flickering - persistent across frames
                        if track_id != -1 and track_id not in self.helmet_state:
                            # Assign a random helmet violation state when person first appears (20% missing rate)
                            self.helmet_state[track_id] = random.random() < 0.2
                            
                        is_missing = self.helmet_state.get(track_id, random.random() < 0.2)
                        helmets_missing.append(is_missing)
                        
                        # Physical Fall Detection (Logic: bounding box width is significantly > height)
                        w = bbox[2] - bbox[0]
                        h = bbox[3] - bbox[1]
                        if w > h * 1.5:
                            incident_triggered = "Fall"
                            
                    elif cls_id in self.vehicle_classes:
                        vehicles.append(bbox)

        # Draw boxes and labels
        # Assuming persons and vehicles are matched (can extract from results again or parallel lists)
        # We need to re-iterate through results to draw things with IDs easily
        
        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf <= 0.4: continue
                bbox = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, bbox)
                track_id = int(box.id[0]) if box.id is not None else -1
                
                if cls_id == self.person_class:
                    is_missing = self.helmet_state.get(track_id, False)
                    color = (0, 0, 255) if is_missing else (0, 255, 0)
                    label = f"Person ID:{track_id} (No PPE)" if is_missing else f"Person ID:{track_id}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                elif cls_id in self.vehicle_classes:
                    # Vehicle -> Blue, relabeled as Forklift
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"Forklift ID:{track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # REAL ML inference for Fire Detection
        if self.fire_model is not None and incident_triggered is None:
            # Resize for fast inference
            small = cv2.resize(frame, (64, 48))
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            # Find warm/bright pixels
            warm_mask = hsv[:, :, 2] > 150
            pixels_to_check = hsv[warm_mask]
            
            if len(pixels_to_check) > 20:
                predictions = self.fire_model.predict(pixels_to_check)
                if np.sum(predictions) > 15: # If ML model classifies at least 15 pixels as fire
                    incident_triggered = "Fire"

        return frame, persons, vehicles, helmets_missing, incident_triggered
