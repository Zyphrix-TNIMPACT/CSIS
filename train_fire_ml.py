import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

def create_synthetic_fire_dataset(num_samples=5000):
    """
    Generate synthetic dataset of HSV pixel values to train our ML model.
    Fire pixels: High Value (brightness), High Saturation, Hue in the Orange/Yellow/Red range (0-35).
    """
    X = []
    y = []
    
    # 1. Generate Fire pixel samples (Class 1)
    for _ in range(num_samples // 2):
        h = np.random.randint(0, 35)      # Red to Yellow Hue
        s = np.random.randint(150, 255)   # High saturation
        v = np.random.randint(200, 255)   # High brightness
        X.append([h, s, v])
        y.append(1)
        
    # 2. Generate Non-Fire background pixel samples (Class 0)
    samples_generated = 0
    while samples_generated < (num_samples // 2):
        h = np.random.randint(0, 180) # Open CV HSV hue is 0-179
        s = np.random.randint(0, 255)
        v = np.random.randint(0, 255)
        
        # Ensure non-fire doesn't accidentally perfectly match fire rules
        if not (h <= 35 and s >= 150 and v >= 200):
            X.append([h, s, v])
            y.append(0)
            samples_generated += 1
            
    return np.array(X), np.array(y)

if __name__ == "__main__":
    print("Initializing Machine Learning Pipeline for Fire Detection...")
    print("-> Generating synthetic fire and background pixel dataset...")
    X, y = create_synthetic_fire_dataset()
    
    print("-> Training Decision Tree Classifier...")
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X, y)
    
    accuracy = model.score(X, y) * 100
    print(f"-> Model Trained! Accuracy on synthetic data: {accuracy:.2f}%")
    
    save_path = 'fire_model.pkl'
    joblib.dump(model, save_path)
    print(f"ML Model successfully saved as '{save_path}'!")
    print("The CSIS Dashboard will now automatically use this trained model to detect fire instead of random simulation.")
