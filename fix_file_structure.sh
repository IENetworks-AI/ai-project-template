#!/bin/bash
set -e

echo "🔧 Fixing File Structure on Oracle Server"
echo "=========================================="

# Navigate to project directory
cd ~/ai-project-template

echo "📋 Current file structure:"
echo "Root directory files:"
ls -la *.joblib 2>/dev/null || echo "No .joblib files in root"

echo ""
echo "Models directory:"
ls -la models/ 2>/dev/null || echo "models/ directory is empty"

echo ""
echo "🔧 Moving model files to correct location..."

# Create models directory if it doesn't exist
mkdir -p models

# Move model files from root to models directory
if [ -f "sales_prediction_model.joblib" ]; then
    echo "📦 Moving sales_prediction_model.joblib to models/"
    mv sales_prediction_model.joblib models/
fi

if [ -f "feature_scaler.joblib" ]; then
    echo "📦 Moving feature_scaler.joblib to models/"
    mv feature_scaler.joblib models/
fi

echo ""
echo "📋 File structure after fix:"
echo "Root directory:"
ls -la *.joblib 2>/dev/null || echo "No .joblib files in root (good!)"

echo ""
echo "Models directory:"
ls -la models/

echo ""
echo "🔧 Restarting API service..."
sudo systemctl restart mlapi.service

echo "⏳ Waiting for service to restart..."
sleep 5

echo ""
echo "🧪 Testing API health..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ API is working!"
    echo "🌐 Web UI available at: http://139.185.33.139:5000"
    
    # Test model info
    echo ""
    echo "📊 Model information:"
    curl -s http://localhost:5000/model/info | python -m json.tool
else
    echo "❌ API health check failed"
    echo "📋 Service logs:"
    sudo journalctl -u mlapi.service -n 20 --no-pager
fi

echo ""
echo "🎉 File structure fix completed!"
echo "📋 Next steps:"
echo "   1. Test the web interface: http://139.185.33.139:5000"
echo "   2. Test API predictions"
echo "   3. Check service logs if needed: sudo journalctl -u mlapi.service -f" 