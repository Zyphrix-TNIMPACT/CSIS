import cv2
import numpy as np
from ultralytics import YOLO
import torch
from datetime import datetime
import os

class SafetyDetectionEngine:
    def __init__(self):
        print("🔧 Initializing Safety Detection Engine...")
        
        # Check for GPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"📊 Using device: {self.device}")
        
        # Load YOLOv8 model
        try:
            self.model = YOLO('yolov8n.pt')  # nano model for speed
            self.model.to(self.device)
            print("✅ YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
        
        # Detection classes mapping
        self.class_names = {
            0: 'person',
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck',
            # Add custom classes if trained
        }
        
        # Risk thresholds
        self.thresholds = {
            'near_miss_distance': 100,  # pixels
            'hazard_zone_distance': 50,  # pixels
            'confidence': 0.5
        }
        
        # Risk scoring
        self.risk_points = {
            'worker_near_vehicle': 30,
            'worker_in_hazard_zone': 40,
            'no_helmet': 20,
            'fire_detected': 100,
            'worker_fall': 80,
            'vehicle_collision': 70,
            'theft': 60
        }
    
    def detect_objects(self, frame):
        """Detect objects in frame using YOLOv8"""
        results = self.model(frame, conf=self.thresholds['confidence'], verbose=False)
        
        detections = {
            'persons': [],
            'vehicles': [],
            'all_boxes': []
        }
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy()
                
                x1, y1, x2, y2 = map(int, xyxy)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                detection = {
                    'class': cls,
                    'class_name': self.class_names.get(cls, 'unknown'),
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2],
                    'center': [center_x, center_y]
                }
                
                # Categorize detections
                if cls == 0:  # person
                    detections['persons'].append(detection)
                elif cls in [2, 3, 5, 7]:  # vehicles
                    detections['vehicles'].append(detection)
                
                detections['all_boxes'].append(detection)
        
        return detections
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def check_near_miss(self, persons, vehicles):
        """Check for near miss between workers and vehicles"""
        near_misses = []
        
        for person in persons:
            for vehicle in vehicles:
                distance = self.calculate_distance(person['center'], vehicle['center'])
                if distance < self.thresholds['near_miss_distance']:
                    near_misses.append({
                        'person': person,
                        'vehicle': vehicle,
                        'distance': distance
                    })
        
        return near_misses
    
    def check_hazard_zone(self, persons, hazard_zones):
        """Check if workers are in hazard zones"""
        violations = []
        
        for person in persons:
            px, py = person['center']
            
            for zone in hazard_zones:
                coords = zone['coordinates']
                x1, y1, x2, y2 = coords
                
                # Check if person center is inside zone
                if x1 <= px <= x2 and y1 <= py <= y2:
                    violations.append({
                        'person': person,
                        'zone': zone
                    })
        
        return violations
    
    def detect_fall(self, persons, prev_persons=None):
        """Detect worker fall (simplified - based on aspect ratio)"""
        falls = []
        
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            width = x2 - x1
            height = y2 - y1
            
            # If person is wider than tall, might be fallen
            aspect_ratio = width / height if height > 0 else 0
            if aspect_ratio > 1.5:  # Horizontal orientation
                falls.append(person)
        
        return falls
    
    def calculate_risk_score(self, detections, hazard_zones=[]):
        """Calculate overall risk score"""
        risk_score = 0
        incidents = []
        
        persons = detections['persons']
        vehicles = detections['vehicles']
        
        # Check near misses
        near_misses = self.check_near_miss(persons, vehicles)
        if near_misses:
            risk_score += self.risk_points['worker_near_vehicle'] * len(near_misses)
            incidents.append({
                'type': 'near_miss',
                'count': len(near_misses),
                'severity': 'medium'
            })
        
        # Check hazard zones
        if hazard_zones:
            zone_violations = self.check_hazard_zone(persons, hazard_zones)
            if zone_violations:
                risk_score += self.risk_points['worker_in_hazard_zone'] * len(zone_violations)
                incidents.append({
                    'type': 'zone_violation',
                    'count': len(zone_violations),
                    'severity': 'high'
                })
        
        # Check for falls
        falls = self.detect_fall(persons)
        if falls:
            risk_score += self.risk_points['worker_fall'] * len(falls)
            incidents.append({
                'type': 'worker_fall',
                'count': len(falls),
                'severity': 'critical'
            })
        
        # Determine overall severity
        if risk_score >= 81:
            severity = 'critical'
        elif risk_score >= 61:
            severity = 'high'
        elif risk_score >= 31:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'risk_score': min(risk_score, 100),
            'severity': severity,
            'incidents': incidents,
            'workers_count': len(persons),
            'vehicles_count': len(vehicles)
        }
    
    def draw_detections(self, frame, detections, risk_info, hazard_zones=[]):
        """Draw bounding boxes and labels on frame"""
        annotated_frame = frame.copy()
        
        # Draw hazard zones
        for zone in hazard_zones:
            coords = zone['coordinates']
            x1, y1, x2, y2 = coords
            color = (0, 0, 255)  # Red for hazard
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            cv2.putText(annotated_frame, zone['name'], (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw person detections
        for person in detections['persons']:
            x1, y1, x2, y2 = person['bbox']
            color = (52, 152, 219)  # Blue
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            label = f"Worker {person['confidence']:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw vehicle detections
        for vehicle in detections['vehicles']:
            x1, y1, x2, y2 = vehicle['bbox']
            color = (243, 156, 18)  # Orange
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            label = f"Vehicle {vehicle['confidence']:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw risk score
        risk_score = risk_info['risk_score']
        severity = risk_info['severity']
        
        # Color based on severity
        severity_colors = {
            'low': (46, 204, 113),      # Green
            'medium': (243, 156, 18),   # Orange
            'high': (231, 76, 60),      # Red
            'critical': (192, 57, 43)   # Dark Red
        }
        color = severity_colors.get(severity, (255, 255, 255))
        
        # Draw risk info box
        cv2.rectangle(annotated_frame, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.rectangle(annotated_frame, (10, 10), (300, 100), color, 2)
        
        cv2.putText(annotated_frame, f"Risk Score: {risk_score}", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(annotated_frame, f"Severity: {severity.upper()}", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(annotated_frame, f"Workers: {risk_info['workers_count']} | Vehicles: {risk_info['vehicles_count']}", 
                   (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame

# Global instance
detection_engine = SafetyDetectionEngine()
