# Kafka GitHub Actions Integration Guide

This guide explains how Kafka functionality has been integrated into GitHub Actions and how to work with it both on Oracle and locally using virtual environments.

## 🎯 Overview

The Kafka integration includes:
- **GitHub Actions Workflow** for automated Kafka deployment on Oracle
- **Local Development Scripts** with virtual environment activation
- **Configuration Switching** between local and Oracle deployments
- **Virtual Environment Management** for consistent development

## 📋 GitHub Actions Integration

### 1. Kafka Deployment Workflow (`kafka_deployment.yml`)

**Triggers:**
- Push to `main` branch with Kafka-related file changes
- Manual workflow dispatch with force deploy option

**Jobs:**
- `kafka-deploy`: Deploys Kafka to Oracle server
- `kafka-local-test`: Tests Kafka integration locally with venv

**Key Features:**
- Automatic SSH connection to Oracle server (139.185.33.139)
- File deployment using `scp`
- Service verification and health checks
- Virtual environment testing

### 2. Updated ML Pipeline Workflow

The existing `ml_pipeline.yml` has been enhanced with:
- Kafka Python dependencies installation
- Oracle deployment integration
- Virtual environment support

## 🚀 Local Development Setup

### Quick Start

1. **Activate Virtual Environment:**
   ```bash
   source scripts/activate_venv.sh
   ```

2. **Setup Local Kafka:**
   ```bash
   ./scripts/setup_local_kafka.sh
   ```

3. **Switch Configurations:**
   ```bash
   # Switch to Oracle
   ./scripts/switch_to_oracle.sh
   
   # Switch back to local
   ./scripts/switch_to_local.sh
   ```

### Available Scripts

#### `scripts/activate_venv.sh`
- Creates and activates virtual environment
- Installs all Python dependencies including Kafka
- Sets up environment variables
- Provides development commands

#### `scripts/setup_local_kafka.sh`
- Checks Docker and Docker Compose installation
- Creates virtual environment if needed
- Starts Kafka using Docker Compose
- Tests Kafka connectivity
- Provides management commands

#### `scripts/switch_to_oracle.sh`
- Switches configuration to Oracle deployment
- Backs up local configuration
- Sets Oracle-specific environment variables
- Enables Oracle Kafka connectivity

#### `scripts/switch_to_local.sh`
- Switches configuration back to local deployment
- Restores local configuration or creates default
- Sets local-specific environment variables
- Enables local Kafka connectivity

## 🔧 Environment Variables

### Local Development
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export KAFKA_CONFIG_PATH="$(pwd)/config/kafka_config.yaml"
export KAFKA_DEPLOYMENT="local"
```

### Oracle Deployment
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export KAFKA_CONFIG_PATH="$(pwd)/config/kafka_config.yaml"
export KAFKA_DEPLOYMENT="oracle"
```

## 📊 GitHub Actions Workflow Details

### Kafka Deployment Workflow

**File Paths Monitored:**
- `deployment/oracle_kafka_*.sh`
- `config/oracle_kafka_config.yaml`
- `src/oracle_kafka_integration.py`
- `test_oracle_kafka.py`

**Deployment Process:**
1. **SSH Setup**: Configures SSH connection to Oracle server
2. **File Deployment**: Uses `scp` to deploy Kafka files
3. **Script Execution**: Runs Kafka deployment scripts on Oracle
4. **Verification**: Tests Kafka services and connectivity
5. **Local Testing**: Tests Kafka integration with virtual environment

### Integration with Existing ML Pipeline

The ML pipeline workflow now includes:
- Kafka dependency installation
- Oracle deployment with Kafka support
- Virtual environment management
- Service verification

## 🧪 Testing and Verification

### Local Testing
```bash
# Activate virtual environment
source scripts/activate_venv.sh

# Test local Kafka
python3 test_kafka_integration.py

# Test Oracle Kafka (when switched)
python3 test_oracle_kafka.py
```

### GitHub Actions Testing
- **Local Test Job**: Tests Kafka integration with venv
- **Oracle Test Job**: Verifies Kafka deployment on Oracle
- **Service Health Checks**: Validates running services
- **Connectivity Tests**: Tests Kafka connectivity

## 🔄 Configuration Management

### Local Configuration (`config/kafka_config.yaml`)
```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  security_protocol: "PLAINTEXT"
  # ... local settings
```

### Oracle Configuration (`config/oracle_kafka_config.yaml`)
```yaml
kafka:
  bootstrap_servers: "139.185.33.139:9092"
  external_bootstrap_servers: "139.185.33.139:29092"
  # ... Oracle settings
```

## 📋 Available Commands

### Local Development
```bash
# Setup and activation
source scripts/activate_venv.sh
./scripts/setup_local_kafka.sh

# Configuration switching
./scripts/switch_to_local.sh
./scripts/switch_to_oracle.sh

# Testing
python3 test_kafka_integration.py
python3 test_oracle_kafka.py

# Kafka management
docker-compose -f docker-compose.kafka.yml up -d
docker-compose -f docker-compose.kafka.yml down
```

### Oracle Deployment
```bash
# Manual deployment (if needed)
ssh ubuntu@139.185.33.139
cd ~/ai-project-template
./deployment/oracle_kafka_deployment.sh

# Service management
sudo systemctl status kafka
sudo systemctl status zookeeper
sudo systemctl status ml-pipeline
```

## 🔍 Monitoring and Health Checks

### Local Monitoring
- **Kafka UI**: http://localhost:8080
- **Health Check**: `python3 test_kafka_integration.py`
- **Logs**: `docker-compose -f docker-compose.kafka.yml logs -f`

### Oracle Monitoring
- **Kafka Dashboard**: http://139.185.33.139:8080
- **Health Check**: `python3 test_oracle_kafka.py`
- **Service Logs**: `sudo journalctl -u kafka -f`

## 🚨 Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**
   ```bash
   source scripts/activate_venv.sh
   ```

2. **Docker Not Running**
   ```bash
   sudo systemctl start docker
   ```

3. **Oracle SSH Connection Failed**
   - Check `ORACLE_SSH_KEY` secret in GitHub
   - Verify Oracle server is accessible

4. **Kafka Services Not Starting**
   ```bash
   # Local
   docker-compose -f docker-compose.kafka.yml restart
   
   # Oracle
   sudo systemctl restart kafka
   sudo systemctl restart zookeeper
   ```

### Debug Commands

```bash
# Check virtual environment
echo $VIRTUAL_ENV

# Check Kafka configuration
cat config/kafka_config.yaml

# Test Kafka connectivity
python3 -c "from kafka_utils import KafkaConfig; print(KafkaConfig().bootstrap_servers)"

# Check Oracle services
ssh ubuntu@139.185.33.139 "sudo systemctl status kafka zookeeper ml-pipeline"
```

## 📈 Benefits

### GitHub Actions Integration
- **Automated Deployment**: Kafka deploys automatically on code changes
- **Environment Consistency**: Same setup across all deployments
- **Health Monitoring**: Automated verification of Kafka services
- **Rollback Capability**: Easy to revert to previous versions

### Local Development
- **Virtual Environment**: Isolated Python environment
- **Easy Switching**: Quick configuration changes
- **Docker Integration**: Local Kafka with Docker Compose
- **Development Tools**: Full development environment setup

### Oracle Deployment
- **Production Ready**: Native Kafka installation on Oracle
- **Service Management**: Systemd services for reliability
- **Monitoring**: Built-in health checks and monitoring
- **Backup**: Automated backup and recovery

## 🎯 Next Steps

1. **Configure GitHub Secrets**: Add `ORACLE_SSH_KEY` to your repository
2. **Test Local Setup**: Run `source scripts/activate_venv.sh`
3. **Deploy to Oracle**: Push changes to trigger GitHub Actions
4. **Monitor Deployment**: Check GitHub Actions logs for deployment status
5. **Verify Services**: Test both local and Oracle Kafka connectivity

## 📚 Additional Resources

- [Kafka Oracle Deployment Guide](ORACLE_KAFKA_DEPLOYMENT_GUIDE.md)
- [Kafka Oracle Summary](KAFKA_ORACLE_SUMMARY.md)
- [Oracle Deployment Setup](ORACLE_DEPLOYMENT_SETUP.md)
- [Kafka Integration Guide](KAFKA_INTEGRATION_GUIDE.md)

---

**🎉 Your Kafka functionality is now fully integrated with GitHub Actions and supports both Oracle and local development with virtual environment activation!** 