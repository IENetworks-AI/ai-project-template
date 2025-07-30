
#!/bin/bash
set -e  # Exit on any error

echo "🔄 Starting deployment..."

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

# Stop existing app if running
if pgrep -f "python3.*app.py" > /dev/null; then
    echo "🛑 Stopping existing app..."
    pkill -f "python3.*app.py" || true
    sleep 2
fi

if [ -f "api/app.py" ]; then
    echo "🚀 Starting API app in background..."
    cd api
    nohup python3 app.py > ../output.log 2>&1 &
    cd ..
    echo "✅ API app is running."
else
    echo "⚠️ api/app.py not found."
fi

echo "✅ Application deployment finished."

# Deploy systemd service
echo "🔧 Deploying systemd service..."
sudo cp aiapp.service /etc/systemd/system/aiapp.service

# Reload systemd and enable + start the service
sudo systemctl daemon-reload
sudo systemctl enable aiapp
sudo systemctl restart aiapp

echo "✅ Service deployed and started successfully."

# Check service status
echo "📊 Checking service status..."
sudo systemctl status aiapp --no-pager -l

echo "🎉 Deployment completed successfully!"
