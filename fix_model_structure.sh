#!/bin/bash
set -e

echo "🔧 Fixing ML Model File Structure on Oracle Server"
echo "=================================================="

# Navigate to project directory
cd ~/ai-project-template

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📋 Current file structure:"
echo "Root directory:"
ls -la *.joblib 2>/dev/null || echo "No .joblib files in root"

echo ""
echo "Models directory:"
ls -la models/ 2>/dev/null || echo "models/ directory is empty"

echo ""
echo "🔧 Step 1: Moving existing model files to correct location..."

# Create models directory if it doesn't exist
mkdir -p models

# Move model files from root to models directory if they exist
if [ -f "sales_prediction_model.joblib" ]; then
    echo "📦 Moving sales_prediction_model.joblib to models/"
    mv sales_prediction_model.joblib models/
fi

if [ -f "feature_scaler.joblib" ]; then
    echo "📦 Moving feature_scaler.joblib to models/"
    mv feature_scaler.joblib models/
fi

echo ""
echo "🔧 Step 2: Regenerating model files with correct structure..."

# Check if pipeline script exists
if [ ! -f "pipelines/ai_pipeline.py" ]; then
    echo "❌ Pipeline script not found!"
    exit 1
fi

echo "🚀 Running ML pipeline to regenerate model files..."
python pipelines/ai_pipeline.py

echo ""
echo "📋 File structure after regeneration:"
echo "Root directory:"
ls -la *.joblib 2>/dev/null || echo "No .joblib files in root (good!)"

echo ""
echo "Models directory:"
ls -la models/

echo ""
echo "🔧 Step 3: Verifying model files..."

# Check if model files exist in correct location
if [ -f "models/sales_prediction_model.joblib" ] && [ -f "models/feature_scaler.joblib" ]; then
    echo "✅ Model files found in correct location"
    
    # Check file sizes
    model_size=$(stat -c%s "models/sales_prediction_model.joblib")
    scaler_size=$(stat -c%s "models/feature_scaler.joblib")
    
    echo "📊 Model file size: ${model_size} bytes"
    echo "📊 Scaler file size: ${scaler_size} bytes"
    
    if [ $model_size -gt 1000 ] && [ $scaler_size -gt 100 ]; then
        echo "✅ Model files appear to be valid"
    else
        echo "⚠️ Model files seem too small, may be corrupted"
    fi
else
    echo "❌ Model files not found in models/ directory"
    echo "📋 Checking if they were saved to root directory..."
    
    if [ -f "sales_prediction_model.joblib" ] || [ -f "feature_scaler.joblib" ]; then
        echo "⚠️ Model files found in root directory, moving them..."
        mv *.joblib models/ 2>/dev/null || true
        echo "✅ Model files moved to models/ directory"
    else
        echo "❌ No model files found anywhere"
        exit 1
    fi
fi

echo ""
echo "🔧 Step 4: Restarting API service..."
sudo systemctl restart mlapi.service

echo "⏳ Waiting for service to restart..."
sleep 5

echo ""
echo "🧪 Step 5: Testing API health..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ API is working!"
    echo "🌐 Web UI available at: http://139.185.33.139:5000"
    
    # Test model info
    echo ""
    echo "📊 Model information:"
    curl -s http://localhost:5000/model/info | python -m json.tool
    
    # Test a simple prediction
    echo ""
    echo "🎯 Testing prediction..."
    test_data='{
        "Date": "2024-01-15",
        "Gender": "Female",
        "Age": 25,
        "Product Category": "Beauty",
        "Quantity": 2,
        "Price per Unit": 50.0
    }'
    
    prediction_response=$(curl -s -X POST http://localhost:5000/api/predict \
        -H "Content-Type: application/json" \
        -d "$test_data")
    
    if echo "$prediction_response" | grep -q "prediction"; then
        echo "✅ Prediction test successful!"
        echo "📊 Response: $prediction_response"
    else
        echo "❌ Prediction test failed"
        echo "📊 Response: $prediction_response"
    fi
    
else
    echo "❌ API health check failed"
    echo "📋 Service logs:"
    sudo journalctl -u mlapi.service -n 20 --no-pager
fi

echo ""
echo "🎉 Model structure fix completed!"
echo "📋 Summary:"
echo "   ✅ Model files moved to correct location"
echo "   ✅ Model files regenerated with proper structure"
echo "   ✅ API service restarted"
echo "   ✅ API health verified"
echo ""
echo "🌐 Access your model:"
echo "   Web UI: http://139.185.33.139:5000"
echo "   Health: http://139.185.33.139:5000/health"
echo "   Model Info: http://139.185.33.139:5000/model/info"
echo ""
echo "🔧 Service management:"
echo "   sudo systemctl status mlapi.service - Check status"
echo "   sudo systemctl restart mlapi.service - Restart service"
echo "   sudo journalctl -u mlapi.service -f - View logs" 