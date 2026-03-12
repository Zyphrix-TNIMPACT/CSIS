import os
import subprocess
import sys

def main():
    print("Initializing CSIS - Cognitive Safety Intelligence System...")
    
    # Check if necessary files exist
    required_files = ["dashboard.py", "detection_module.py", "risk_engine.py", "zone_module.py", "near_miss.py", "utils.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: Missing required file {file}. Ensure you are running this from the CSIS directory.")
            sys.exit(1)
            
    print("All core modules found. Starting Dashboard...")
    
    # Run Streamlit dashboard
    try:
        subprocess.run(["streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\nCSIS stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
