import os
from ultralytics import YOLO

def train_custom_ppe_model():
    """
    This script is designed to train a REAL YOLOv8 model on a custom dataset, 
    replacing the simulated hardhat detections in the default implementation.
    
    Prerequisites:
    1. A dataset formatted in YOLO architecture containing images and labels.
    2. A 'data.yaml' file pointing to your train/val image folders and class names (e.g., [0: 'person', 1: 'hardhat', 2: 'no_hardhat']).
    
    You can get free PPE datasets via Kaggle or Roboflow: https://universe.roboflow.com/
    """
    
    dataset_path = "dataset/data.yaml"
    
    if not os.path.exists(dataset_path):
        print("❌ Dataset not found!")
        print(f"Please place your dataset containing {dataset_path} in the current directory.")
        print("Once the dataset is ready, run this script again to begin training.")
        return

    print("🚀 Loading pre-trained YOLOv8 Nano model as base...")
    model = YOLO("yolov8n.pt") 

    print("🔥 Starting ML Training Epochs...")
    # Train the model
    # Adjust epochs, batch size, and imgsz based on your hardware capabilities (GPU recommended)
    results = model.train(
        data=dataset_path, 
        epochs=50, 
        imgsz=640,
        batch=16,
        project="csis_models",
        name="ppe_detector"
    )
    
    print("✅ Training Complete!")
    print(f"Your model is saved at: {results.save_dir}/weights/best.pt")
    print("Rename this file to 'ppe_custom.pt' and place it in the root directory. CSIS will automatically load it!")

if __name__ == "__main__":
    train_custom_ppe_model()
