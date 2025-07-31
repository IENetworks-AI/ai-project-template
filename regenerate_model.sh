#!/bin/bash
set -e

echo "🔄 Regenerating ML Model Files on Oracle Server"
echo "================================================"

# Navigate to project directory
cd ~/ai-project-template

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if pipeline script exists
if [ ! -f "pipelines/ai_pipeline.py" ]; then
    echo "❌ Pipeline script not found!"
    exit 1
fi

echo "📋 Current model files:"
ls -la models/ 2>/dev/null || echo "models/ directory is empty or doesn't exist"

echo ""
echo "🚀 Running ML pipeline to regenerate model files..."
python pipelines/ai_pipeline.py

echo ""
echo "📋 New model files:"
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
echo "🎉 Model regeneration completed!"
echo "📋 Next steps:"
echo "   1. Test the web interface: http://139.185.33.139:5000"
echo "   2. Test API predictions"
echo "   3. Check service logs if needed: sudo journalctl -u mlapi.service -f" 