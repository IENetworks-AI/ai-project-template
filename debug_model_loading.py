#!/usr/bin/env python3
"""
Debug script to check model loading issues on Oracle server
Run this on the Oracle server to diagnose model loading problems
"""

import os
import sys
import joblib
import pandas as pd
from pathlib import Path

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 Checking file structure...")
    print("=" * 50)
    
    base_dir = Path("/home/ubuntu/ai-project-template")
    
    # Check directories
    dirs_to_check = [
        "models",
        "data/processed",
        "api"
    ]
    
    for dir_path in dirs_to_check:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/ exists")
            # List contents
            try:
                files = list(full_path.iterdir())
                for file in files[:5]:  # Show first 5 files
                    print(f"   📄 {file.name}")
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
            except Exception as e:
                print(f"   ❌ Error listing contents: {e}")
        else:
            print(f"❌ {dir_path}/ does not exist")
    
    # Check specific model files
    model_files = [
        "models/sales_prediction_model.joblib",
        "models/feature_scaler.joblib",
        "data/processed/features.csv"
    ]
    
    print("\n📋 Checking model files:")
    for file_path in model_files:
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} exists ({size} bytes)")
        else:
            print(f"❌ {file_path} does not exist")

def check_python_environment():
    """Check Python environment and dependencies"""
    print("\n🐍 Checking Python environment...")
    print("=" * 50)
    
    try:
        import joblib
        print(f"✅ joblib version: {joblib.__version__}")
    except ImportError as e:
        print(f"❌ joblib not available: {e}")
    
    try:
        import pandas
        print(f"✅ pandas version: {pandas.__version__}")
    except ImportError as e:
        print(f"❌ pandas not available: {e}")
    
    try:
        import flask
        print(f"✅ flask version: {flask.__version__}")
    except ImportError as e:
        print(f"❌ flask not available: {e}")
    
    try:
        import sklearn
        print(f"✅ scikit-learn version: {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ scikit-learn not available: {e}")

def test_model_loading():
    """Test loading the model files"""
    print("\n🎯 Testing model loading...")
    print("=" * 50)
    
    base_dir = Path("/home/ubuntu/ai-project-template")
    
    # Test model loading
    model_path = base_dir / "models" / "sales_prediction_model.joblib"
    if model_path.exists():
        try:
            model = joblib.load(model_path)
            print(f"✅ Model loaded successfully: {type(model).__name__}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    else:
        print("❌ Model file not found")
    
    # Test scaler loading
    scaler_path = base_dir / "models" / "feature_scaler.joblib"
    if scaler_path.exists():
        try:
            scaler = joblib.load(scaler_path)
            print(f"✅ Scaler loaded successfully: {type(scaler).__name__}")
        except Exception as e:
            print(f"❌ Error loading scaler: {e}")
    else:
        print("❌ Scaler file not found")
    
    # Test features loading
    features_path = base_dir / "data" / "processed" / "features.csv"
    if features_path.exists():
        try:
            features_df = pd.read_csv(features_path)
            print(f"✅ Features loaded successfully: {features_df.shape}")
            print(f"   Columns: {list(features_df.columns)[:5]}...")
        except Exception as e:
            print(f"❌ Error loading features: {e}")
    else:
        print("❌ Features file not found")

def check_api_app():
    """Check the API app file"""
    print("\n🌐 Checking API app...")
    print("=" * 50)
    
    api_path = Path("/home/ubuntu/ai-project-template/api/app.py")
    if api_path.exists():
        print(f"✅ API app exists ({api_path.stat().st_size} bytes)")
        
        # Check if it's executable
        if os.access(api_path, os.X_OK):
            print("✅ API app is executable")
        else:
            print("⚠️ API app is not executable")
            
        # Check first few lines
        try:
            with open(api_path, 'r') as f:
                lines = f.readlines()[:10]
                print("📄 First 10 lines:")
                for i, line in enumerate(lines, 1):
                    print(f"   {i:2d}: {line.rstrip()}")
        except Exception as e:
            print(f"❌ Error reading API app: {e}")
    else:
        print("❌ API app not found")

def check_service_logs():
    """Check service logs"""
    print("\n📋 Checking service logs...")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(['sudo', 'journalctl', '-u', 'mlapi.service', '-n', '20', '--no-pager'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("📄 Recent service logs:")
            for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                if line.strip():
                    print(f"   {line}")
        else:
            print("📄 No recent logs found")
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def main():
    """Main debug function"""
    print("🔧 ML Pipeline Debug Script")
    print("=" * 60)
    print("This script will help diagnose model loading issues")
    print()
    
    check_file_structure()
    check_python_environment()
    test_model_loading()
    check_api_app()
    check_service_logs()
    
    print("\n" + "=" * 60)
    print("🎯 Debug Summary:")
    print("If model/scaler files are missing, the pipeline needs to be re-run")
    print("If files exist but loading fails, check Python dependencies")
    print("If API app has issues, check the file permissions and content")
    print()
    print("🔧 Next steps:")
    print("1. Run: python pipelines/ai_pipeline.py (to generate model files)")
    print("2. Restart service: sudo systemctl restart mlapi.service")
    print("3. Check logs: sudo journalctl -u mlapi.service -f")

if __name__ == "__main__":
    main() 