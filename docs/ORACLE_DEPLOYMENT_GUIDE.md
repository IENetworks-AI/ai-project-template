# Oracle Cloud Deployment Guide

## 🚀 Oracle Cloud Infrastructure Setup

### Server Configuration
- **CPU**: 1 Oracle CPU (OCPU)
- **RAM**: 16GB
- **Storage**: 100 GB
- **OS**: Ubuntu Server (AI/ML-optimized)
- **IP**: 139.185.33.139
- **Username**: ubuntu

## 🔑 Required GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

### 1. SSH_PRIVATE_KEY
Your SSH private key for server access:
```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copy the private key content to GitHub secret
cat ~/.ssh/id_rsa
```

### 2. SSH_USER
```
ubuntu
```

### 3. SSH_HOST
```
139.185.33.139
```

### 4. SSH_TARGET_DIR
```
/home/ubuntu/ai-project-template
```

## 🛠️ Server Preparation

### 1. Install Dependencies
```bash
# Connect to your Oracle server
ssh ubuntu@139.185.33.139

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install Oracle Instant Client (if using Oracle DB)
sudo apt install libaio1 -y
```

### 2. Setup Project Directory
```bash
# Create project directory
mkdir -p /home/ubuntu/ai-project-template
cd /home/ubuntu/ai-project-template

# Clone your repository
git clone https://github.com/your-username/your-repo.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Oracle Database (Optional)
If you're using Oracle Database:

```bash
# Install cx_Oracle dependencies
sudo apt install libaio1 -y

# Download Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip
unzip instantclient-basiclite-linuxx64.zip

# Set environment variables
echo 'export LD_LIBRARY_PATH=/home/ubuntu/instantclient_21_1:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 4. Setup Systemd Service
Create the service file:
```bash
sudo nano /etc/systemd/system/oracle-ai-api.service
```

Add this content:
```ini
[Unit]
Description=Oracle AI API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-project-template
Environment=PATH=/home/ubuntu/ai-project-template/venv/bin
ExecStart=/home/ubuntu/ai-project-template/venv/bin/python api/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable oracle-ai-api
sudo systemctl start oracle-ai-api
sudo systemctl status oracle-ai-api
```

## 🔄 CI/CD Pipeline

### Automatic Deployment
The GitHub Actions workflow will automatically:

1. **Test**: Run unit tests
2. **Preprocess**: Extract and transform data
3. **Train**: Train and evaluate models
4. **Deploy**: Sync files to Oracle server
5. **Restart**: Restart the API service

### Manual Deployment
If you prefer manual deployment:

```bash
# On your local machine
cd ai-project-template

# Run the pipeline
python pipelines/ai_pipeline.py

# Deploy to server
rsync -avz --delete ./ ubuntu@139.185.33.139:/home/ubuntu/ai-project-template/

# SSH to server and restart service
ssh ubuntu@139.185.33.139 "sudo systemctl restart oracle-ai-api"
```

## 🧪 Testing Deployment

### 1. Check Service Status
```bash
sudo systemctl status oracle-ai-api
```

### 2. Test API Endpoints
```bash
# Health check
curl http://139.185.33.139:5000/health

# API info
curl http://139.185.33.139:5000/

# Model info
curl http://139.185.33.139:5000/model/info
```

### 3. Check Logs
```bash
# Service logs
sudo journalctl -u oracle-ai-api -f

# Application logs
tail -f /home/ubuntu/ai-project-template/logs/*.log
```

## 🔧 Configuration

### Update config/config.yaml
Edit the configuration file with your Oracle Database settings:

```yaml
# Oracle Database Configuration
database:
  host: "your-oracle-db-host"
  port: 1521
  service_name: "ORCL"
  username: "your_username"
  password: "your_password"

# Oracle Cloud Server Settings
oracle_server:
  host: "139.185.33.139"
  user: "ubuntu"
  target_dir: "/home/ubuntu/ai-project-template"
```

## 🚨 Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Check SSH key permissions
   chmod 600 ~/.ssh/id_rsa
   
   # Test SSH connection
   ssh -i ~/.ssh/id_rsa ubuntu@139.185.33.139
   ```

2. **Port 5000 Blocked**
   ```bash
   # Configure firewall
   sudo ufw allow 5000
   sudo ufw enable
   ```

3. **Oracle Database Connection Issues**
   ```bash
   # Check Oracle Instant Client
   echo $LD_LIBRARY_PATH
   
   # Test connection
   python3 -c "import cx_Oracle; print('Oracle client OK')"
   ```

4. **Service Won't Start**
   ```bash
   # Check service logs
   sudo journalctl -u oracle-ai-api -n 50
   
   # Check file permissions
ls -la /home/ubuntu/ai-project-template/
   ```

### Debug Commands
```bash
# Check if API is running
ps aux | grep python

# Check port usage
netstat -tlnp | grep :5000

# Check disk space
df -h

# Check memory usage
free -h
```

## 📊 Monitoring

### Log Files
- **Service logs**: `/var/log/syslog`
- **Application logs**: `/home/ubuntu/ai-project/logs/`
- **GitHub Actions logs**: Available in your repository

### Health Checks
```bash
# Automated health check script
#!/bin/bash
curl -f http://localhost:5000/health || echo "API is down"
```

## 🔒 Security

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 5000
sudo ufw enable
```

### SSL/TLS (Optional)
For production, consider adding SSL:
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

**Note**: This guide assumes you have access to the Oracle Cloud server and the necessary permissions to configure services. 