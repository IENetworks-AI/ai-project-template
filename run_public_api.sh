#!/bin/bash

echo "🛑 Stopping systemd service..."
sudo systemctl stop mlapi.service

echo "🔍 Checking if port 5000 is free..."
sleep 2

# Check if port is still in use
if sudo netstat -tlnp | grep :5000; then
    echo "⚠️ Port 5000 is still in use. Killing any remaining processes..."
    sudo pkill -f "python.*app.py" || true
    sudo pkill -f "flask" || true
    sleep 2
fi

echo "🚀 Starting API with public access..."
echo "🌐 API will be accessible at: http://139.185.33.139:5000"
echo "📱 Press Ctrl+C to stop the API"

# Run the API with public access
HOST=0.0.0.0 python api/app.py 