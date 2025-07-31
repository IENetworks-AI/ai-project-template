#!/bin/bash
set -e  # Exit on any error

echo "🔄 Starting ML Pipeline API deployment..."

# Function to handle apt locks
handle_apt_locks() {
    echo "🔧 Checking for apt locks..."
    sudo killall apt apt-get || true
    sudo rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock* || true
    echo "✅ Apt locks cleared"
}

# Function to install system dependencies
install_system_deps() {
    echo "📦 Installing system dependencies..."
    handle_apt_locks
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv rsync git
    echo "✅ System dependencies installed"
}

# Navigate to project directory
cd ~/ai-project-template

# Install system dependencies if needed
if ! command -v python3 &> /dev/null; then
    install_system_deps
fi

echo "📥 Code deployed via rsync from GitHub Actions..."

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Step 1: Fix file structure and generate model
echo "🔧 Step 1: Fixing file structure and generating model..."

# Create models directory
mkdir -p models

# Move any existing model files to correct location
if [ -f "sales_prediction_model.joblib" ]; then
    echo "📦 Moving sales_prediction_model.joblib to models/"
    mv sales_prediction_model.joblib models/
fi

if [ -f "feature_scaler.joblib" ]; then
    echo "📦 Moving feature_scaler.joblib to models/"
    mv feature_scaler.joblib models/
fi

# Generate model files if they don't exist
if [ ! -f "models/sales_prediction_model.joblib" ] || [ ! -f "models/feature_scaler.joblib" ]; then
    echo "🚀 Generating model files..."
    python pipelines/ai_pipeline.py
fi

# Verify model files
echo "📋 Verifying model files..."
if [ -f "models/sales_prediction_model.joblib" ] && [ -f "models/feature_scaler.joblib" ]; then
    model_size=$(stat -c%s "models/sales_prediction_model.joblib")
    scaler_size=$(stat -c%s "models/feature_scaler.joblib")
    echo "✅ Model files found:"
    echo "   Model: ${model_size} bytes"
    echo "   Scaler: ${scaler_size} bytes"
else
    echo "❌ Model files not found, attempting to regenerate..."
    python pipelines/ai_pipeline.py
fi

# Stop existing API service if running
if sudo systemctl is-active --quiet mlapi.service; then
    echo "🛑 Stopping existing API service..."
    sudo systemctl stop mlapi.service
    sleep 2
fi

# Set up systemd service for the API server
echo "🔧 Setting up API server systemd service..."
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
Environment=PORT=5000
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable + start the service
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "🔧 Enabling API server service..."
sudo systemctl enable mlapi.service

echo "🚀 Starting API server service..."
sudo systemctl start mlapi.service

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

echo "✅ API server deployed and started successfully."

# Check service status
echo "📊 Checking service status..."
sudo systemctl status mlapi.service --no-pager -l

# Wait a moment for the service to start
sleep 5

# Test the API multiple times
echo "🧪 Testing API endpoints..."
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Testing API health..."
    
    if curl -f http://localhost:5000/health 2>/dev/null; then
        echo "✅ API health check passed on attempt $attempt"
        
        # Test model loading
        model_info=$(curl -s http://localhost:5000/model/info 2>/dev/null)
        if echo "$model_info" | grep -q "model_loaded.*true"; then
            echo "✅ Model loaded successfully"
            break
        else
            echo "⚠️ Model not loaded yet, retrying..."
        fi
    else
        echo "❌ API health check failed on attempt $attempt"
    fi
    
    if [ $attempt -lt $max_attempts ]; then
        echo "⏳ Waiting 10 seconds before retry..."
        sleep 10
    fi
    
    attempt=$((attempt + 1))
done

# Final test
echo "🧪 Final API test..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ API is working!"
    echo "🌐 Web UI available at: http://139.185.33.139:5000"
    
    # Test a prediction
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
    sudo journalctl -u mlapi.service -n 30 --no-pager
fi

echo "🎉 ML Pipeline API deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   🌐 Web UI: http://139.185.33.139:5000"
echo "   🔧 Health Check: http://139.185.33.139:5000/health"
echo "   📊 Model Info: http://139.185.33.139:5000/model/info"
echo "   🧪 Test Page: http://139.185.33.139:5000/test"
echo ""
echo "📡 API Endpoints:"
echo "   POST http://139.185.33.139:5000/api/predict - Single prediction"
echo "   POST http://139.185.33.139:5000/api/batch_predict - Batch predictions"
echo ""
echo "🔧 Service Management:"
echo "   sudo systemctl status mlapi.service - Check status"
echo "   sudo systemctl restart mlapi.service - Restart service"
echo "   sudo journalctl -u mlapi.service -f - View logs"
echo ""
echo "🔄 The API will automatically:"
echo "   ✅ Start on server boot"
echo "   ✅ Restart if it crashes"
echo "   ✅ Run continuously in the background" 