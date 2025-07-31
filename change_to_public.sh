#!/bin/bash

echo "🔧 Changing API to public access..."

# Stop the current service
sudo systemctl stop mlapi.service

# Update service configuration to use 0.0.0.0
sudo sed -i 's/Environment=HOST=localhost/Environment=HOST=0.0.0.0/' /etc/systemd/system/mlapi.service

# Reload and restart service
sudo systemctl daemon-reload
sudo systemctl start mlapi.service

echo "✅ API now accessible from anywhere!"
echo "🌐 Access URLs:"
echo "   - From Oracle server: http://localhost:5000"
echo "   - From your computer: http://139.185.33.139:5000"
echo "   - Health check: http://139.185.33.139:5000/health"

# Test the API
echo ""
echo "🧪 Testing API..."
sleep 3
curl -s http://localhost:5000/health | python3 -m json.tool 