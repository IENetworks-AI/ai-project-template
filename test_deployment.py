#!/usr/bin/env python3
"""
Test script to debug deployment issues
"""
import os
import sys
import subprocess
import time

def test_app_startup():
    """Test if the app can start without errors"""
    print("🔍 Testing app startup...")
    
    # Test if we can import the app
    try:
        sys.path.append(os.path.join(os.getcwd(), 'api'))
        from api.app import app
        print("✅ App imports successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    # Test if we can start the app in a subprocess
    try:
        # Change to api directory
        api_dir = os.path.join(os.getcwd(), 'api')
        os.chdir(api_dir)
        
        # Start app in background
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ App started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ App failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'flask',
        'pandas', 
        'yaml',
        'joblib',
        'sklearn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {missing}")
        return False
    else:
        print("✅ All dependencies available")
        return True

def test_config():
    """Test if configuration files exist"""
    print("🔍 Testing configuration...")
    
    config_files = [
        'config/config.yaml',
        'api/app.py',
        'api/routes.py'
    ]
    
    missing = []
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All config files present")
        return True

def main():
    print("🚀 Starting deployment test...")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    # Test configuration
    config_ok = test_config()
    
    # Test app startup
    app_ok = test_app_startup()
    
    print("\n📊 Test Results:")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"App Startup: {'✅' if app_ok else '❌'}")
    
    if all([deps_ok, config_ok, app_ok]):
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main()) 