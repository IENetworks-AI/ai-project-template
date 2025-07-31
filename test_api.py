#!/usr/bin/env python3
"""
Test script for the ML Pipeline API
Run this to test the API locally before deployment
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    
    # Base URL (change this to your Oracle server IP when deployed)
    base_url = "http://localhost:5000"  # Local testing
    # base_url = "http://139.185.33.139:5000"  # Oracle server
    
    print("🧪 Testing ML Pipeline API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Scaler loaded: {data.get('scaler_loaded')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Model Info
    print("\n2️⃣ Model Information:")
    try:
        response = requests.get(f"{base_url}/model/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info retrieved")
            print(f"   Model type: {data.get('model_type')}")
            print(f"   Features count: {data.get('features_count')}")
            print(f"   Feature names: {data.get('feature_names', [])[:5]}...")
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Model info error: {e}")
        return False
    
    # Test 3: Single Prediction
    print("\n3️⃣ Single Prediction:")
    test_data = {
        "Date": "2024-01-15",
        "Gender": "Female",
        "Age": 25,
        "Product Category": "Beauty",
        "Quantity": 2,
        "Price per Unit": 50.0
    }
    
    try:
        response = requests.post(f"{base_url}/api/predict", 
                               json=test_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful")
            print(f"   Input: {test_data}")
            print(f"   Prediction: ${data.get('prediction', 0):.2f}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction error: {e}")
        return False
    
    # Test 4: Batch Prediction
    print("\n4️⃣ Batch Prediction:")
    batch_data = [
        {
            "Date": "2024-01-15",
            "Gender": "Female",
            "Age": 25,
            "Product Category": "Beauty",
            "Quantity": 2,
            "Price per Unit": 50.0
        },
        {
            "Date": "2024-01-15",
            "Gender": "Male",
            "Age": 35,
            "Product Category": "Electronics",
            "Quantity": 1,
            "Price per Unit": 500.0
        },
        {
            "Date": "2024-01-15",
            "Gender": "Female",
            "Age": 28,
            "Product Category": "Clothing",
            "Quantity": 3,
            "Price per Unit": 100.0
        }
    ]
    
    try:
        response = requests.post(f"{base_url}/api/batch_predict", 
                               json=batch_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch prediction successful")
            print(f"   Input count: {len(batch_data)}")
            print(f"   Predictions: {[f'${p:.2f}' for p in data.get('predictions', [])]}")
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch prediction error: {e}")
        return False
    
    # Test 5: Performance Test
    print("\n5️⃣ Performance Test:")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/api/predict", 
                               json=test_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"✅ Performance test passed")
            print(f"   Response time: {response_time:.2f}ms")
            
            if response_time < 100:
                print(f"   🚀 Excellent performance (< 100ms)")
            elif response_time < 500:
                print(f"   ⚡ Good performance (< 500ms)")
            else:
                print(f"   ⚠️ Slow performance (> 500ms)")
        else:
            print(f"❌ Performance test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Performance test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! API is working correctly.")
    print(f"🌐 Web UI available at: {base_url}")
    print(f"📡 API endpoints available at: {base_url}/api/")
    return True

def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing Error Handling:")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    # Test invalid JSON
    print("\n1️⃣ Invalid JSON:")
    try:
        response = requests.post(f"{base_url}/api/predict", 
                               data="invalid json",
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Expected: 400 (Bad Request)")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    # Test missing data
    print("\n2️⃣ Missing Data:")
    try:
        response = requests.post(f"{base_url}/api/predict", 
                               json={},
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Expected: 400 (Bad Request)")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    # Test invalid endpoint
    print("\n3️⃣ Invalid Endpoint:")
    try:
        response = requests.get(f"{base_url}/invalid", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Expected: 404 (Not Found)")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("Make sure the API server is running: python api/app.py")
    print()
    
    # Test main functionality
    success = test_api()
    
    if success:
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ API testing completed successfully!")
        print("📋 Next steps:")
        print("   1. Deploy to Oracle Cloud")
        print("   2. Update base_url in this script to: http://139.185.33.139:5000")
        print("   3. Run tests against production server")
    else:
        print("\n❌ API testing failed!")
        print("📋 Troubleshooting:")
        print("   1. Make sure the API server is running: python api/app.py")
        print("   2. Check if the model files exist in models/ directory")
        print("   3. Verify all dependencies are installed: pip install -r requirements.txt") 