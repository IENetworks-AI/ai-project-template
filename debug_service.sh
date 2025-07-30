#!/bin/bash
# Debug script for systemd service issues

echo "🔍 Debugging aiapp service..."

# Check service status
echo "📊 Service Status:"
sudo systemctl status aiapp --no-pager -l

# Check service logs
echo -e "\n📋 Service Logs:"
sudo journalctl -u aiapp --no-pager -l -n 20

# Check if port is in use
echo -e "\n🔌 Port Check:"
sudo netstat -tlnp | grep :5000 || echo "Port 5000 not in use"

# Check if app.py exists and is executable
echo -e "\n📁 File Check:"
ls -la /home/ubuntu/ai-project-template/api/app.py
ls -la /home/ubuntu/ai-project-template/venv/bin/python3

# Test app startup manually
echo -e "\n🧪 Manual App Test:"
cd /home/ubuntu/ai-project-template/api
source ../venv/bin/activate
python3 -c "import app; print('✅ App imports successfully')" || echo "❌ App import failed"

# Test app startup in background
echo -e "\n🚀 Testing app startup:"
cd /home/ubuntu/ai-project-template/api
source ../venv/bin/activate
timeout 10s python3 app.py &
sleep 3
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ App responds to health check"
    pkill -f "python3 app.py"
else
    echo "❌ App does not respond to health check"
    pkill -f "python3 app.py"
fi

echo -e "\n�� Debug complete!" 