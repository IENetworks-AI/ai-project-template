# Server Deployment Guide

## Server Environment
- **Server**: ubuntu@ai-test-lab
- **Project Directory**: `/home/ubuntu/ai-project-template`
- **SSH Directory**: `ubuntu@ai-test-lab:~/ai-project-template$`

## Quick Start

### 1. Connect to Server
```bash
ssh ubuntu@ai-test-lab
cd ~/ai-project-template
```

### 2. Make Scripts Executable (First Time Only)
```bash
chmod +x start.sh
chmod +x deploy.sh
```

### 3. Start Application

#### Option A: Direct Start
```bash
./start.sh
```

#### Option B: Deploy as Service
```bash
./deploy.sh
```

## File Structure Compliance

The project has been updated to comply with the server's directory structure:

- **Working Directory**: `/home/ubuntu/ai-project-template`
- **Virtual Environment**: `/home/ubuntu/ai-project-template/venv/`
- **Service Configuration**: Updated `aiapp.service` with correct paths
- **Deployment Script**: Updated `deploy.sh` with correct paths

## Configuration Files

### `config/config.yaml`
- Updated `target_dir` to `/home/ubuntu/ai-project-template`
- All data paths are relative to the project root

### `aiapp.service`
- WorkingDirectory: `/home/ubuntu/ai-project-template`
- ExecStart: Uses `python3` for compatibility
- User: `ubuntu`

### `deploy.sh`
- Navigates to correct directory: `cd ~/ai-project-template`
- Creates virtual environment if needed
- Installs dependencies
- Deploys systemd service

## Available Endpoints

Once running, the application provides:

- **Main App**: `http://server-ip:80/`
- **API**: `http://server-ip:5000/`
  - `/health` - Health check
  - `/model/info` - Model information
  - `/model/predict` - Make predictions
  - `/data/features` - Get features data

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status aiapp
```

### View Logs
```bash
sudo journalctl -u aiapp -f
```

### Restart Service
```bash
sudo systemctl restart aiapp
```

### Manual Start (for debugging)
```bash
cd ~/ai-project-template
source venv/bin/activate
python3 app.py
```

## Testing

### Run Tests
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Or Run Tests Manually
```bash
cd ~/ai-project-template
source venv/bin/activate
pip install pytest pandas pyyaml
python -m pytest tests/ -v
``` 