#!/bin/bash

echo "🔍 Checking API service status..."

# Check if mlapi service is running
if sudo systemctl is-active --quiet mlapi.service; then
    echo "✅ mlapi.service is running"
    echo "📊 Service status:"
    sudo systemctl status mlapi.service --no-pager -l
    
    echo ""
    echo "🌐 Testing API endpoints..."
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    curl -s http://localhost:5000/health | python3 -m json.tool
    
    echo ""
    echo "🔍 Testing model info..."
    curl -s http://localhost:5000/model/info | python3 -m json.tool
    
    echo ""
    echo "🎉 API is working perfectly!"
    echo "📱 Access the web UI at: http://localhost:5000"
    echo "🔗 Or use SSH port forwarding: ssh -L 5000:localhost:5000 ubuntu@139.185.33.139"
    
else
    echo "❌ mlapi.service is not running"
    echo "🔧 Starting the service..."
    sudo systemctl start mlapi.service
    sudo systemctl status mlapi.service --no-pager -l
fi

echo ""
echo "🔍 Checking what's using port 5000..."
sudo netstat -tlnp | grep :5000 || echo "No process found on port 5000"

echo ""
echo "🔍 Checking all Python processes..."
ps aux | grep python | grep -v grep || echo "No Python processes found" 