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
Restart=on-failure
RestartSec=5
Environment=PATH=/home/ubuntu/ai-project-template/venv/bin
Environment=PORT=5000

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
sleep 5

echo "✅ API server deployed and started successfully."

# Check service status
echo "📊 Checking service status..."
sudo systemctl status mlapi.service --no-pager -l

# Wait a moment for the service to start
sleep 5

# Test the API
echo "🧪 Testing API endpoints..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ API health check passed"
else
    echo "⚠️ API health check failed - checking service logs..."
    sudo journalctl -u mlapi.service -n 20 --no-pager
    echo "🔧 Attempting to restart service..."
    sudo systemctl restart mlapi.service
    sleep 5
    if curl -f http://localhost:5000/health 2>/dev/null; then
        echo "✅ API health check passed after restart"
    else
        echo "❌ API health check still failing"
        echo "📋 Service logs:"
        sudo journalctl -u mlapi.service -n 30 --no-pager
    fi
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