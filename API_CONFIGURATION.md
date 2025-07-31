# 🌐 API Configuration Guide

This guide explains how to configure the ML API server for different environments.

## 🔧 Configuration Options

### Environment Variables

The API can be configured using these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `localhost` | Host address to bind to |
| `PORT` | `5000` | Port number to run on |
| `DEBUG` | `False` | Enable debug mode |

## 🏠 Local Development

### Default Configuration (Recommended)
```bash
# Run with default settings (localhost:5000)
python api/app.py
```

### Custom Configuration
```bash
# Run on different port
PORT=8080 python api/app.py

# Run with debug mode
DEBUG=true python api/app.py

# Run on different host and port
HOST=127.0.0.1 PORT=3000 python api/app.py
```

## ☁️ Oracle Cloud Deployment

### Current Configuration (localhost)
The API is configured to run on `localhost:5000` on the Oracle server.

**Access from Oracle server:**
- Web UI: http://localhost:5000
- Health: http://localhost:5000/health
- Model Info: http://localhost:5000/model/info

**Access from your computer:**
- Web UI: http://139.185.33.139:5000
- Health: http://139.185.33.139:5000/health
- Model Info: http://139.185.33.139:5000/model/info

### Alternative Configurations

#### Option 1: Localhost Only (Most Secure)
```bash
# Only accessible from the Oracle server itself
HOST=localhost PORT=5000
```

#### Option 2: All Interfaces (Current)
```bash
# Accessible from anywhere (requires firewall rules)
HOST=0.0.0.0 PORT=5000
```

#### Option 3: Custom Port
```bash
# Run on different port
HOST=localhost PORT=8080
```

## 🔒 Security Considerations

### Localhost Configuration (Recommended)
- ✅ **Most Secure**: Only accessible from the server itself
- ✅ **No External Access**: Prevents unauthorized access
- ❌ **Limited Access**: You need SSH to access the API

### All Interfaces Configuration
- ✅ **Easy Access**: Accessible from anywhere
- ❌ **Security Risk**: Exposed to the internet
- ⚠️ **Requires Firewall**: Need to configure security groups

## 🚀 How to Change Configuration

### 1. Update Service Configuration
```bash
# SSH into Oracle server
ssh ubuntu@139.185.33.139

# Edit the service file
sudo nano /etc/systemd/system/mlapi.service
```

### 2. Change Environment Variables
```ini
[Service]
Environment=HOST=localhost
Environment=PORT=5000
Environment=DEBUG=False
```

### 3. Restart Service
```bash
sudo systemctl daemon-reload
sudo systemctl restart mlapi.service
```

## 📋 Configuration Examples

### Example 1: Localhost with Custom Port
```bash
# Service configuration
Environment=HOST=localhost
Environment=PORT=8080
Environment=DEBUG=False

# Access URLs
http://localhost:8080          # From Oracle server
http://139.185.33.139:8080     # From your computer
```

### Example 2: All Interfaces (Public Access)
```bash
# Service configuration
Environment=HOST=0.0.0.0
Environment=PORT=5000
Environment=DEBUG=False

# Access URLs
http://139.185.33.139:5000     # From anywhere
```

### Example 3: Development Mode
```bash
# Service configuration
Environment=HOST=localhost
Environment=PORT=5000
Environment=DEBUG=True

# Access URLs
http://localhost:5000          # From Oracle server
```

## 🔧 Quick Configuration Changes

### Change to Localhost Only
```bash
# SSH into Oracle server
ssh ubuntu@139.185.33.139

# Update service configuration
sudo sed -i 's/Environment=HOST=0.0.0.0/Environment=HOST=localhost/' /etc/systemd/system/mlapi.service

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart mlapi.service
```

### Change Port
```bash
# Update service configuration
sudo sed -i 's/Environment=PORT=5000/Environment=PORT=8080/' /etc/systemd/system/mlapi.service

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart mlapi.service
```

## 🌐 Access Methods

### From Oracle Server (SSH)
```bash
# SSH into server
ssh ubuntu@139.185.33.139

# Access API locally
curl http://localhost:5000/health
curl http://localhost:5000/model/info

# Open web interface
# (You'll need to use a text-based browser or port forwarding)
```

### From Your Computer (Port Forwarding)
```bash
# Create SSH tunnel
ssh -L 5000:localhost:5000 ubuntu@139.185.33.139

# Now access from your computer
http://localhost:5000
```

### From Your Computer (Direct Access)
```bash
# If using 0.0.0.0 configuration
http://139.185.33.139:5000
```

## 📊 Current Configuration

Your API is currently configured as:
- **Host**: localhost
- **Port**: 5000
- **Debug**: False
- **Access**: From Oracle server only

## 🎯 Recommended Setup

For production use, we recommend:
- **Host**: localhost (for security)
- **Port**: 5000 (standard)
- **Access**: Use SSH port forwarding for secure access

This provides the best balance of security and usability! 🔒✨ 