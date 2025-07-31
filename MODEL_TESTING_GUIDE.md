# 🎯 Model Testing Guide - Oracle Server

This guide explains how to test your deployed ML model on the Oracle Cloud server with a beautiful web UI.

## 🚀 Quick Start

### 1. Access the Web UI
Once deployed, access your model at:
```
http://139.185.33.139:5000
```

### 2. Test the API
Health check endpoint:
```
http://139.185.33.139:5000/health
```

## 🌐 Web Interface Features

### 📊 Main Dashboard
- **Beautiful UI**: Modern, responsive design with gradient backgrounds
- **Real-time Predictions**: Instant sales predictions with form validation
- **Model Information**: Live status of model loading and feature count
- **API Documentation**: Built-in endpoint documentation

### 🧪 Testing Interface
- **Single Prediction Form**: Input sales data and get predictions
- **Batch Testing**: Test multiple predictions at once
- **Sample Test Cases**: Pre-built test scenarios
- **Real-time Results**: Immediate feedback with detailed output

## 📡 API Endpoints

### 1. Health Check
```bash
GET http://139.185.33.139:5000/health
```
**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Model Information
```bash
GET http://139.185.33.139:5000/model/info
```
**Response:**
```json
{
  "model_type": "RandomForestRegressor",
  "features_count": 65,
  "feature_names": ["feature_0", "feature_1", ...],
  "model_loaded_at": "2024-01-15T10:30:00"
}
```

### 3. Single Prediction
```bash
POST http://139.185.33.139:5000/api/predict
Content-Type: application/json

{
  "Date": "2024-01-15",
  "Gender": "Female",
  "Age": 25,
  "Product Category": "Beauty",
  "Quantity": 2,
  "Price per Unit": 50.0
}
```
**Response:**
```json
{
  "prediction": 100.0,
  "input_data": {
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### 4. Batch Predictions
```bash
POST http://139.185.33.139:5000/api/batch_predict
Content-Type: application/json

[
  {
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
  },
  {
    "Date": "2024-01-15",
    "Gender": "Male",
    "Age": 35,
    "Product Category": "Electronics",
    "Quantity": 1,
    "Price per Unit": 500.0
  }
]
```

## 🧪 Testing Scenarios

### Test Case 1: Beauty Product
```json
{
  "Date": "2024-01-15",
  "Gender": "Female",
  "Age": 25,
  "Product Category": "Beauty",
  "Quantity": 2,
  "Price per Unit": 50.0
}
```
**Expected**: Prediction around $100.0 (2 × $50.0)

### Test Case 2: Electronics Product
```json
{
  "Date": "2024-01-15",
  "Gender": "Male",
  "Age": 35,
  "Product Category": "Electronics",
  "Quantity": 1,
  "Price per Unit": 500.0
}
```
**Expected**: Prediction around $500.0 (1 × $500.0)

### Test Case 3: Clothing Product
```json
{
  "Date": "2024-01-15",
  "Gender": "Female",
  "Age": 28,
  "Product Category": "Clothing",
  "Quantity": 3,
  "Price per Unit": 100.0
}
```
**Expected**: Prediction around $300.0 (3 × $100.0)

## 🔧 Testing with cURL

### Health Check
```bash
curl http://139.185.33.139:5000/health
```

### Single Prediction
```bash
curl -X POST http://139.185.33.139:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
  }'
```

### Batch Prediction
```bash
curl -X POST http://139.185.33.139:5000/api/batch_predict \
  -H "Content-Type: application/json" \
  -d '[
    {
      "Date": "2024-01-15",
      "Gender": "Female",
      "Age": 25,
      "Product Category": "Beauty",
      "Quantity": 2,
      "Price per Unit": 50.0
    },
    {
      "Date": "2024-01-15",
      "Gender": "Male",
      "Age": 35,
      "Product Category": "Electronics",
      "Quantity": 1,
      "Price per Unit": 500.0
    }
  ]'
```

## 🐍 Testing with Python

### Install requests
```bash
pip install requests
```

### Test Script
```python
import requests
import json

# API base URL
base_url = "http://139.185.33.139:5000"

# Test data
test_data = {
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
}

# Health check
print("🔍 Health Check:")
response = requests.get(f"{base_url}/health")
print(json.dumps(response.json(), indent=2))

# Model info
print("\n📊 Model Info:")
response = requests.get(f"{base_url}/model/info")
print(json.dumps(response.json(), indent=2))

# Single prediction
print("\n🎯 Single Prediction:")
response = requests.post(f"{base_url}/api/predict", json=test_data)
print(json.dumps(response.json(), indent=2))

# Batch prediction
print("\n📦 Batch Prediction:")
batch_data = [test_data, {
    "Date": "2024-01-15",
    "Gender": "Male",
    "Age": 35,
    "Product Category": "Electronics",
    "Quantity": 1,
    "Price per Unit": 500.0
}]
response = requests.post(f"{base_url}/api/batch_predict", json=batch_data)
print(json.dumps(response.json(), indent=2))
```

## 🔍 Server Monitoring

### Check Service Status
```bash
# SSH into the server
ssh ubuntu@139.185.33.139

# Check service status
sudo systemctl status mlapi.service

# View logs
sudo journalctl -u mlapi.service -f
```

### Check API Health
```bash
# Test from server
curl http://localhost:5000/health

# Check if port is open
netstat -tlnp | grep :5000
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check service status
sudo systemctl status mlapi.service

# View detailed logs
sudo journalctl -u mlapi.service -n 50

# Restart service
sudo systemctl restart mlapi.service
```

#### 2. Model Not Loading
```bash
# Check if model files exist
ls -la /home/ubuntu/ai-project-template/models/

# Check Python environment
cd /home/ubuntu/ai-project-template
source venv/bin/activate
python -c "import joblib; print('joblib available')"
```

#### 3. Port Not Accessible
```bash
# Check firewall
sudo ufw status

# Check if service is listening
sudo netstat -tlnp | grep :5000

# Test local access
curl http://localhost:5000/health
```

### Debug Commands
```bash
# SSH into server
ssh ubuntu@139.185.33.139

# Navigate to project
cd /home/ubuntu/ai-project-template

# Activate environment
source venv/bin/activate

# Test API manually
python api/app.py

# Check logs
tail -f /var/log/syslog | grep mlapi
```

## 📊 Performance Testing

### Load Testing with Apache Bench
```bash
# Install ab
sudo apt-get install apache2-utils

# Test single endpoint
ab -n 100 -c 10 -T application/json -p test_data.json http://139.185.33.139:5000/api/predict
```

### Create test_data.json
```json
{
  "Date": "2024-01-15",
  "Gender": "Female",
  "Age": 25,
  "Product Category": "Beauty",
  "Quantity": 2,
  "Price per Unit": 50.0
}
```

## 🎯 Expected Results

### Model Performance
- **Response Time**: < 100ms for single predictions
- **Accuracy**: High accuracy for sales predictions
- **Availability**: 99.9% uptime
- **Concurrent Users**: Support for multiple simultaneous requests

### API Response Format
- **Consistent JSON**: All responses in JSON format
- **Error Handling**: Proper HTTP status codes
- **Validation**: Input validation with clear error messages
- **Documentation**: Self-documenting API endpoints

## 🔐 Security Considerations

### Production Deployment
- **HTTPS**: Use SSL/TLS certificates
- **Authentication**: Implement API key authentication
- **Rate Limiting**: Add request rate limiting
- **Input Validation**: Validate all input data
- **Logging**: Monitor and log all requests

### Current Setup (Development)
- **HTTP Only**: For development/testing
- **No Authentication**: Open access for testing
- **Basic Validation**: Input format validation
- **Basic Logging**: Application logs only

## 📞 Support

### Getting Help
1. **Check Logs**: `sudo journalctl -u mlapi.service -f`
2. **Test Health**: `curl http://139.185.33.139:5000/health`
3. **Restart Service**: `sudo systemctl restart mlapi.service`
4. **Check Files**: Verify model files exist in `/models/` directory

### Useful Commands
```bash
# Service management
sudo systemctl start mlapi.service
sudo systemctl stop mlapi.service
sudo systemctl restart mlapi.service
sudo systemctl status mlapi.service

# Log viewing
sudo journalctl -u mlapi.service -f
sudo journalctl -u mlapi.service --since "1 hour ago"

# File checking
ls -la /home/ubuntu/ai-project-template/models/
ls -la /home/ubuntu/ai-project-template/api/
```

---

**🎉 Your ML model is now ready for testing on Oracle Cloud!**

Access the web interface at: **http://139.185.33.139:5000** 