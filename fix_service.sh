#!/bin/bash
set -e

echo "🔧 Fixing ML API Service on Oracle Server"
echo "=========================================="

# Navigate to project directory
cd ~/ai-project-template

echo "📋 Current service status:"
sudo systemctl status mlapi.service --no-pager -l || echo "Service not found"

echo ""
echo "🔧 Enabling service..."
sudo systemctl enable mlapi.service

echo "🚀 Starting service..."
sudo systemctl start mlapi.service

echo "⏳ Waiting for service to start..."
sleep 5

echo ""
echo "📊 Service status after fix:"
sudo systemctl status mlapi.service --no-pager -l

echo ""
echo "🧪 Testing API health..."
if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ API is working!"
    echo "🌐 Web UI available at: http://139.185.33.139:5000"
else
    echo "❌ API health check failed"
    echo "📋 Recent service logs:"
    sudo journalctl -u mlapi.service -n 20 --no-pager
fi

echo ""
echo "🔧 Service management commands:"
echo "   sudo systemctl status mlapi.service - Check status"
echo "   sudo systemctl restart mlapi.service - Restart service"
echo "   sudo journalctl -u mlapi.service -f - View logs"
echo "   curl http://localhost:5000/health - Test API" 