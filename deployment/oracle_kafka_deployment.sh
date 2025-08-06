#!/bin/bash

# Oracle Kafka Deployment Script
# This script deploys Kafka on Oracle server and integrates it with the ML pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Configuration
ORACLE_IP="139.185.33.139"
ORACLE_USER="ubuntu"
KAFKA_VERSION="3.6.1"
SCALA_VERSION="2.13"
JAVA_VERSION="11"

log "Starting Oracle Kafka deployment..."

# Check if we're on the Oracle server
if [[ "$(hostname -I | awk '{print $1}')" == "$ORACLE_IP" ]]; then
    log "Running on Oracle server, proceeding with Kafka installation..."
    
    # Run the Kafka setup script
    if [[ -f "deployment/oracle_kafka_setup.sh" ]]; then
        log "Running Kafka setup script..."
        chmod +x deployment/oracle_kafka_setup.sh
        ./deployment/oracle_kafka_setup.sh
    else
        error "Kafka setup script not found: deployment/oracle_kafka_setup.sh"
    fi
    
    # Install Python Kafka dependencies
    log "Installing Python Kafka dependencies..."
    pip install kafka-python confluent-kafka pyyaml
    
    # Create Oracle-specific configuration
    log "Creating Oracle-specific Kafka configuration..."
    mkdir -p config
    cat > config/oracle_kafka_config.yaml << 'EOF'
# Oracle Server Kafka Configuration for ML Pipeline System

kafka:
  # Bootstrap servers for Oracle deployment
  bootstrap_servers: "139.185.33.139:9092"
  
  # External listeners for remote connections
  external_bootstrap_servers: "139.185.33.139:29092"
  
  # Security settings
  security_protocol: "PLAINTEXT"
  sasl_mechanism: "PLAIN"

# Topics configuration for Oracle deployment
topics:
  raw_data_topic: "ml-pipeline-raw-data"
  processed_data_topic: "ml-pipeline-processed-data"
  model_training_topic: "ml-pipeline-model-training"
  model_evaluation_topic: "ml-pipeline-model-evaluation"
  prediction_requests_topic: "ml-pipeline-prediction-requests"
  prediction_results_topic: "ml-pipeline-prediction-results"
  pipeline_monitoring_topic: "ml-pipeline-monitoring"
  model_monitoring_topic: "ml-pipeline-model-monitoring"
  alerts_topic: "ml-pipeline-alerts"
  dead_letter_topic: "ml-pipeline-dead-letter"

# Producer settings optimized for Oracle deployment
producer:
  acks: "all"
  retries: 3
  batch_size: 16384
  linger_ms: 5
  buffer_memory: 33554432
  compression_type: "snappy"
  max_request_size: 1048576
  request_timeout_ms: 30000
  max_block_ms: 60000
  delivery_timeout_ms: 120000

# Consumer settings optimized for Oracle deployment
consumer:
  group_id: "ml-pipeline-consumer-group"
  auto_offset_reset: "earliest"
  enable_auto_commit: true
  auto_commit_interval_ms: 5000
  session_timeout_ms: 30000
  heartbeat_interval_ms: 3000
  max_poll_records: 500
  fetch_max_wait_ms: 500
  fetch_min_bytes: 1
  fetch_max_bytes: 52428800
  max_poll_interval_ms: 300000
  request_timeout_ms: 30000

# Oracle deployment specific settings
oracle_deployment:
  server_ip: "139.185.33.139"
  server_hostname: "oracle-ml-server"
  kafka_service_name: "kafka.service"
  zookeeper_service_name: "zookeeper.service"
  kafka_home: "/opt/kafka"
  kafka_data_dir: "/var/lib/kafka/data"
  kafka_log_dir: "/var/log/kafka"
  zookeeper_data_dir: "/var/lib/zookeeper/data"
  zookeeper_log_dir: "/var/log/zookeeper"
  kafka_user: "kafka"
  kafka_group: "kafka"
  internal_port: 9092
  external_port: 29092
  zookeeper_port: 2181
  firewall_enabled: true
  backup_enabled: true
  backup_retention_days: 7
  log_retention_days: 7
  health_check_enabled: true
  health_check_interval: 300
  alert_on_failure: true
EOF

    # Test Kafka integration
    log "Testing Kafka integration..."
    python3 -c "
import sys
sys.path.append('src')
from oracle_kafka_integration import check_oracle_kafka_health, get_oracle_kafka_status, create_oracle_ml_topics

print('Testing Oracle Kafka integration...')

# Check health
health = check_oracle_kafka_health()
print(f'Health status: {health}')

# Get status
status = get_oracle_kafka_status()
print(f'Kafka status: {status}')

# Create topics
if create_oracle_ml_topics():
    print('ML pipeline topics created successfully')
else:
    print('Some topics may already exist')

print('Kafka integration test completed')
"

    # Create systemd service for ML pipeline with Kafka
    log "Creating ML pipeline service with Kafka integration..."
    sudo tee /etc/systemd/system/ml-pipeline.service > /dev/null << 'EOF'
[Unit]
Description=ML Pipeline with Kafka Integration
After=network.target kafka.service zookeeper.service
Wants=kafka.service zookeeper.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-project-template
Environment=PATH=/home/ubuntu/ai-project-template/venv/bin
ExecStart=/home/ubuntu/ai-project-template/venv/bin/python /home/ubuntu/ai-project-template/src/kafka_ml_pipeline.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start ML pipeline service
    log "Enabling ML pipeline service..."
    sudo systemctl daemon-reload
    sudo systemctl enable ml-pipeline.service
    
    # Create Kafka monitoring dashboard
    log "Creating Kafka monitoring dashboard..."
    mkdir -p /home/ubuntu/kafka-monitoring
    cat > /home/ubuntu/kafka-monitoring/dashboard.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Kafka Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .healthy { background-color: #d4edda; color: #155724; }
        .unhealthy { background-color: #f8d7da; color: #721c24; }
        .warning { background-color: #fff3cd; color: #856404; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Kafka Monitoring Dashboard</h1>
    <div id="status"></div>
    <div id="metrics"></div>
    <script>
        function updateStatus() {
            fetch('/api/kafka/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    const metricsDiv = document.getElementById('metrics');
                    
                    // Status
                    let statusHtml = '<h2>Service Status</h2>';
                    if (data.health.overall_healthy) {
                        statusHtml += '<div class="status healthy">✓ All services healthy</div>';
                    } else {
                        statusHtml += '<div class="status unhealthy">✗ Some services unhealthy</div>';
                    }
                    
                    statusHtml += `
                        <div class="metric">
                            <strong>Zookeeper:</strong> ${data.health.zookeeper_service ? '✓ Running' : '✗ Stopped'}
                        </div>
                        <div class="metric">
                            <strong>Kafka:</strong> ${data.health.kafka_service ? '✓ Running' : '✗ Stopped'}
                        </div>
                        <div class="metric">
                            <strong>Topics:</strong> ${data.topics.length} topics
                        </div>
                    `;
                    
                    statusDiv.innerHTML = statusHtml;
                    
                    // Metrics
                    let metricsHtml = '<h2>Topics</h2><ul>';
                    data.topics.forEach(topic => {
                        metricsHtml += `<li>${topic}</li>`;
                    });
                    metricsHtml += '</ul>';
                    
                    metricsDiv.innerHTML = metricsHtml;
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        '<div class="status unhealthy">Error fetching status: ' + error.message + '</div>';
                });
        }
        
        // Update every 30 seconds
        updateStatus();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
EOF

    # Create API endpoint for Kafka status
    log "Creating Kafka status API endpoint..."
    cat > /home/ubuntu/kafka-api.py << 'EOF'
#!/usr/bin/env python3

from flask import Flask, jsonify
import sys
import os
sys.path.append('/home/ubuntu/ai-project-template/src')
from oracle_kafka_integration import get_oracle_kafka_status

app = Flask(__name__)

@app.route('/api/kafka/status')
def kafka_status():
    try:
        status = get_oracle_kafka_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def dashboard():
    with open('/home/ubuntu/kafka-monitoring/dashboard.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

    # Create systemd service for Kafka monitoring
    log "Creating Kafka monitoring service..."
    sudo tee /etc/systemd/system/kafka-monitoring.service > /dev/null << 'EOF'
[Unit]
Description=Kafka Monitoring Dashboard
After=network.target kafka.service
Wants=kafka.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/ai-project-template/venv/bin/python /home/ubuntu/kafka-api.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable Kafka monitoring service
    sudo systemctl daemon-reload
    sudo systemctl enable kafka-monitoring.service
    sudo systemctl start kafka-monitoring.service

    # Create backup script
    log "Creating backup script..."
    cat > /home/ubuntu/backup-kafka.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups/kafka"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating Kafka backup at $DATE..."

# Backup Kafka configuration and data
sudo tar -czf $BACKUP_DIR/kafka-config-$DATE.tar.gz \
    /opt/kafka/config \
    /etc/systemd/system/kafka.service \
    /etc/systemd/system/zookeeper.service \
    /etc/systemd/system/ml-pipeline.service \
    /etc/systemd/system/kafka-monitoring.service

# Backup Kafka data (optional - can be large)
# sudo tar -czf $BACKUP_DIR/kafka-data-$DATE.tar.gz /var/lib/kafka/data

# Backup logs
sudo tar -czf $BACKUP_DIR/kafka-logs-$DATE.tar.gz \
    /var/log/kafka \
    /var/log/zookeeper

echo "Backup completed: $BACKUP_DIR/kafka-config-$DATE.tar.gz"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

    chmod +x /home/ubuntu/backup-kafka.sh

    # Set up cron job for backups
    log "Setting up backup cron job..."
    (crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-kafka.sh >> /var/log/kafka-backup.log 2>&1") | crontab -

    # Final verification
    log "Performing final verification..."
    
    # Check services
    if sudo systemctl is-active --quiet kafka.service; then
        log "✓ Kafka service is running"
    else
        error "✗ Kafka service is not running"
    fi
    
    if sudo systemctl is-active --quiet zookeeper.service; then
        log "✓ Zookeeper service is running"
    else
        error "✗ Zookeeper service is not running"
    fi
    
    if sudo systemctl is-active --quiet ml-pipeline.service; then
        log "✓ ML Pipeline service is running"
    else
        warning "ML Pipeline service is not running (will start automatically)"
    fi
    
    if sudo systemctl is-active --quiet kafka-monitoring.service; then
        log "✓ Kafka monitoring service is running"
    else
        warning "Kafka monitoring service is not running"
    fi

    # Test Kafka connectivity
    log "Testing Kafka connectivity..."
    python3 -c "
import sys
sys.path.append('src')
from oracle_kafka_integration import OracleKafkaProducer, get_oracle_kafka_config

config = get_oracle_kafka_config()
producer = OracleKafkaProducer(config)

# Test message
test_message = {
    'message_id': 'test-$(date +%s)',
    'message_type': 'test',
    'timestamp': '$(date -Iseconds)',
    'source': 'deployment-test',
    'data': {'test': True}
}

if producer.send_message('ml-pipeline-raw-data', test_message):
    print('✓ Kafka producer test successful')
else:
    print('✗ Kafka producer test failed')

producer.close()
"

    log "=== Oracle Kafka Deployment Complete ==="
    log ""
    log "Kafka is now running on Oracle server:"
    log "  • Bootstrap servers: 139.185.33.139:9092"
    log "  • External listeners: 139.185.33.139:29092"
    log "  • Zookeeper: 139.185.33.139:2181"
    log ""
    log "Services:"
    log "  • Kafka: sudo systemctl status kafka"
    log "  • Zookeeper: sudo systemctl status zookeeper"
    log "  • ML Pipeline: sudo systemctl status ml-pipeline"
    log "  • Monitoring: sudo systemctl status kafka-monitoring"
    log ""
    log "Monitoring:"
    log "  • Dashboard: http://139.185.33.139:8080"
    log "  • API: http://139.185.33.139:8080/api/kafka/status"
    log ""
    log "Management:"
    log "  • Monitor: /usr/local/bin/kafka-monitor.sh"
    log "  • Health check: /usr/local/bin/kafka-health-check.sh"
    log "  • Backup: /home/ubuntu/backup-kafka.sh"
    log ""
    log "Topics created:"
    log "  • ml-pipeline-raw-data"
    log "  • ml-pipeline-processed-data"
    log "  • ml-pipeline-model-training"
    log "  • ml-pipeline-model-evaluation"
    log "  • ml-pipeline-prediction-requests"
    log "  • ml-pipeline-prediction-results"
    log "  • ml-pipeline-monitoring"
    log "  • ml-pipeline-alerts"
    log "  • ml-pipeline-dead-letter"

else
    log "Not running on Oracle server, skipping Kafka installation"
    log "This script should be run on the Oracle server (139.185.33.139)"
fi 