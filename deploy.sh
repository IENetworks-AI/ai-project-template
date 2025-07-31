#!/bin/bash
set -e  # Exit on any error

echo "🔄 Starting ML Pipeline deployment..."

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

# Stop existing ML pipeline service if running
if sudo systemctl is-active --quiet mlpipeline.service; then
    echo "🛑 Stopping existing ML pipeline service..."
    sudo systemctl stop mlpipeline.service
    sleep 2
fi

# Set up systemd service for the ML pipeline
echo "🔧 Setting up ML pipeline systemd service..."
sudo tee /etc/systemd/system/mlpipeline.service > /dev/null << 'EOF'
[Unit]
Description=ML Pipeline Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-project-template
ExecStart=/home/ubuntu/ai-project-template/venv/bin/python pipelines/ai_pipeline.py
Restart=on-failure
RestartSec=5
Environment=PATH=/home/ubuntu/ai-project-template/venv/bin

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable + start the service
sudo systemctl daemon-reload
sudo systemctl enable mlpipeline.service
sudo systemctl restart mlpipeline.service

echo "✅ ML Pipeline service deployed and started successfully."

# Check service status
echo "📊 Checking service status..."
sudo systemctl status mlpipeline.service --no-pager -l

echo "🎉 ML Pipeline deployment completed successfully!" 