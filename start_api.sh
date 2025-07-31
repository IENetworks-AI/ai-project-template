#!/bin/bash
set -e

echo "🚀 Starting ML API Server on Oracle Cloud"
echo "=========================================="

# Navigate to project directory
cd ~/ai-project-template

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Fix file structure first
echo "🔧 Fixing file structure..."
mkdir -p models

# Move model files if they exist in root
if [ -f "sales_prediction_model.joblib" ]; then
    echo "📦 Moving model to models/ directory..."
    mv sales_prediction_model.joblib models/
fi

if [ -f "feature_scaler.joblib" ]; then
    echo "📦 Moving scaler to models/ directory..."
    mv feature_scaler.joblib models/
fi

# Generate model if it doesn't exist
if [ ! -f "models/sales_prediction_model.joblib" ]; then
    echo "🚀 Generating model files..."
    python pipelines/ai_pipeline.py
fi

# Stop existing service
echo "🛑 Stopping existing service..."
sudo systemctl stop mlapi.service 2>/dev/null || true

# Update service configuration
echo "🔧 Updating service configuration..."
sudo tee /etc/systemd/system/mlapi.service > /dev/null << 'EOF'
[Unit]
Description=ML Pipeline API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-project-template
ExecStart=/home/ubuntu/ai-project-template/venv/bin/python api/app.py
Restart=always
RestartSec=10
Environment=PATH=/home/ubuntu/ai-project-template/venv/bin
Environment=HOST=localhost
Environment=PORT=5000
Environment=DEBUG=False
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload and start service
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "🔧 Enabling service..."
sudo systemctl enable mlapi.service

echo "🚀 Starting service..."
sudo systemctl start mlapi.service

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 15

# Check service status
echo "📊 Service status:"
sudo systemctl status mlapi.service --no-pager -l

# Test the API
echo "🧪 Testing API..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Testing API..."
    
    if curl -f http://localhost:5000/health 2>/dev/null; then
        echo "✅ API is responding!"
        
        # Test model loading
        model_info=$(curl -s http://localhost:5000/model/info 2>/dev/null)
        if echo "$model_info" | grep -q "model_loaded.*true"; then
            echo "✅ Model is loaded!"
            break
        else
            echo "⚠️ Model not loaded yet..."
        fi
    else
        echo "❌ API not responding yet..."
    fi
    
    if [ $attempt -lt $max_attempts ]; then
        echo "⏳ Waiting 5 seconds..."
        sleep 5
    fi
    
    attempt=$((attempt + 1))
done

# Final test
echo "🎯 Final test..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo ""
    echo "🎉 SUCCESS! Your ML API is now running!"
    echo ""
    echo "🌐 Access your model:"
    echo "   Web UI: http://139.185.33.139:5000"
    echo "   Health: http://139.185.33.139:5000/health"
    echo "   Model Info: http://139.185.33.139:5000/model/info"
    echo ""
    echo "📡 API Endpoints:"
    echo "   POST http://139.185.33.139:5000/api/predict"
    echo "   POST http://139.185.33.139:5000/api/batch_predict"
    echo ""
    echo "🔧 Service Management:"
    echo "   sudo systemctl status mlapi.service"
    echo "   sudo systemctl restart mlapi.service"
    echo "   sudo journalctl -u mlapi.service -f"
    echo ""
    echo "🔄 The API will:"
    echo "   ✅ Start automatically on server boot"
    echo "   ✅ Restart automatically if it crashes"
    echo "   ✅ Run continuously in the background"
else
    echo "❌ API failed to start properly"
    echo "📋 Checking logs..."
    sudo journalctl -u mlapi.service -n 20 --no-pager
fi 