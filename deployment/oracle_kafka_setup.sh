#!/bin/bash

# Oracle Server Kafka Setup Script
# This script installs and configures Kafka on Oracle Cloud Infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Configuration
KAFKA_VERSION="3.6.1"
SCALA_VERSION="2.13"
JAVA_VERSION="11"
KAFKA_HOME="/opt/kafka"
KAFKA_USER="kafka"
KAFKA_GROUP="kafka"
KAFKA_DATA_DIR="/var/lib/kafka/data"
KAFKA_LOG_DIR="/var/log/kafka"
ZOOKEEPER_DATA_DIR="/var/lib/zookeeper/data"
ZOOKEEPER_LOG_DIR="/var/log/zookeeper"

log "Starting Kafka installation on Oracle server..."

# Update system
log "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install required packages
log "Installing required packages..."
sudo apt-get install -y \
    openjdk-${JAVA_VERSION}-jdk \
    curl \
    wget \
    unzip \
    systemd \
    systemd-sysv \
    net-tools \
    htop \
    vim \
    git

# Create kafka user and group
log "Creating Kafka user and group..."
sudo groupadd -r $KAFKA_GROUP 2>/dev/null || true
sudo useradd -r -g $KAFKA_GROUP -d $KAFKA_HOME -s /bin/bash $KAFKA_USER 2>/dev/null || true

# Create directories
log "Creating Kafka directories..."
sudo mkdir -p $KAFKA_HOME
sudo mkdir -p $KAFKA_DATA_DIR
sudo mkdir -p $KAFKA_LOG_DIR
sudo mkdir -p $ZOOKEEPER_DATA_DIR
sudo mkdir -p $ZOOKEEPER_LOG_DIR

# Download and install Kafka
log "Downloading Kafka ${KAFKA_VERSION}..."
cd /tmp
wget https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz
sudo tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -C /opt/
sudo ln -sf /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} $KAFKA_HOME

# Set ownership
log "Setting directory ownership..."
sudo chown -R $KAFKA_USER:$KAFKA_GROUP $KAFKA_HOME
sudo chown -R $KAFKA_USER:$KAFKA_GROUP $KAFKA_DATA_DIR
sudo chown -R $KAFKA_USER:$KAFKA_GROUP $KAFKA_LOG_DIR
sudo chown -R $KAFKA_USER:$KAFKA_GROUP $ZOOKEEPER_DATA_DIR
sudo chown -R $KAFKA_USER:$KAFKA_GROUP $ZOOKEEPER_LOG_DIR

# Configure environment variables
log "Configuring environment variables..."
sudo tee /etc/profile.d/kafka.sh > /dev/null <<EOF
export KAFKA_HOME=$KAFKA_HOME
export PATH=\$PATH:\$KAFKA_HOME/bin
export JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64
EOF

# Configure Zookeeper
log "Configuring Zookeeper..."
sudo tee $KAFKA_HOME/config/zookeeper.properties > /dev/null <<EOF
# Zookeeper configuration
dataDir=$ZOOKEEPER_DATA_DIR
dataLogDir=$ZOOKEEPER_LOG_DIR
clientPort=2181
maxClientCnxns=60
autopurge.snapRetainCount=3
autopurge.purgeInterval=1
tickTime=2000
initLimit=10
syncLimit=5
EOF

# Configure Kafka
log "Configuring Kafka..."
sudo tee $KAFKA_HOME/config/server.properties > /dev/null <<EOF
# Kafka configuration
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:29092
advertised.listeners=PLAINTEXT://$(hostname -I | awk '{print $1}'):9092,PLAINTEXT_HOST://$(hostname -I | awk '{print $1}'):29092
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
inter.broker.listener.name=PLAINTEXT
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs=$KAFKA_DATA_DIR
num.partitions=1
num.recovery.threads.per.data.dir=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
zookeeper.connect=localhost:2181
zookeeper.connection.timeout.ms=18000
group.initial.rebalance.delay.ms=0
EOF

# Create systemd service files
log "Creating systemd services..."

# Zookeeper service
sudo tee /etc/systemd/system/zookeeper.service > /dev/null <<EOF
[Unit]
Description=Apache Zookeeper
After=network.target

[Service]
Type=forking
User=$KAFKA_USER
Group=$KAFKA_GROUP
Environment="JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
ExecStart=$KAFKA_HOME/bin/zookeeper-server-start.sh -daemon $KAFKA_HOME/config/zookeeper.properties
ExecStop=$KAFKA_HOME/bin/zookeeper-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Kafka service
sudo tee /etc/systemd/system/kafka.service > /dev/null <<EOF
[Unit]
Description=Apache Kafka
After=network.target zookeeper.service

[Service]
Type=simple
User=$KAFKA_USER
Group=$KAFKA_GROUP
Environment="JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
ExecStart=$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties
ExecStop=$KAFKA_HOME/bin/kafka-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
log "Reloading systemd..."
sudo systemctl daemon-reload

# Enable services
log "Enabling services..."
sudo systemctl enable zookeeper.service
sudo systemctl enable kafka.service

# Start Zookeeper
log "Starting Zookeeper..."
sudo systemctl start zookeeper.service
sleep 10

# Verify Zookeeper is running
if sudo systemctl is-active --quiet zookeeper.service; then
    log "Zookeeper started successfully"
else
    error "Failed to start Zookeeper"
fi

# Start Kafka
log "Starting Kafka..."
sudo systemctl start kafka.service
sleep 15

# Verify Kafka is running
if sudo systemctl is-active --quiet kafka.service; then
    log "Kafka started successfully"
else
    error "Failed to start Kafka"
fi

# Create topics for ML pipeline
log "Creating ML pipeline topics..."
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-raw-data
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-processed-data
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-model-training
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-model-evaluation
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-prediction-requests
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-prediction-results
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-monitoring
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-alerts
$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-dead-letter

# List topics
log "Created topics:"
$KAFKA_HOME/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Configure firewall (if ufw is active)
if command -v ufw &> /dev/null && sudo ufw status | grep -q "Status: active"; then
    log "Configuring firewall..."
    sudo ufw allow 2181/tcp  # Zookeeper
    sudo ufw allow 9092/tcp  # Kafka
    sudo ufw allow 29092/tcp # Kafka external
fi

# Create monitoring script
log "Creating monitoring script..."
sudo tee /usr/local/bin/kafka-monitor.sh > /dev/null <<'EOF'
#!/bin/bash

echo "=== Kafka Status ==="
sudo systemctl status kafka.service --no-pager -l

echo -e "\n=== Zookeeper Status ==="
sudo systemctl status zookeeper.service --no-pager -l

echo -e "\n=== Kafka Topics ==="
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

echo -e "\n=== Kafka Consumer Groups ==="
/opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

echo -e "\n=== System Resources ==="
free -h
df -h
EOF

sudo chmod +x /usr/local/bin/kafka-monitor.sh

# Create health check script
log "Creating health check script..."
sudo tee /usr/local/bin/kafka-health-check.sh > /dev/null <<'EOF'
#!/bin/bash

# Health check for Kafka services
check_service() {
    local service=$1
    if sudo systemctl is-active --quiet $service; then
        echo "✓ $service is running"
        return 0
    else
        echo "✗ $service is not running"
        return 1
    fi
}

check_port() {
    local port=$1
    local service=$2
    if netstat -tlnp | grep -q ":$port "; then
        echo "✓ $service is listening on port $port"
        return 0
    else
        echo "✗ $service is not listening on port $port"
        return 1
    fi
}

echo "=== Kafka Health Check ==="
echo "$(date)"

echo -e "\n--- Service Status ---"
check_service zookeeper.service
check_service kafka.service

echo -e "\n--- Port Status ---"
check_port 2181 "Zookeeper"
check_port 9092 "Kafka"
check_port 29092 "Kafka External"

echo -e "\n--- Topic Status ---"
if /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "ml-pipeline"; then
    echo "✓ ML pipeline topics exist"
else
    echo "✗ ML pipeline topics missing"
fi
EOF

sudo chmod +x /usr/local/bin/kafka-health-check.sh

# Create log rotation
log "Setting up log rotation..."
sudo tee /etc/logrotate.d/kafka > /dev/null <<EOF
$KAFKA_LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $KAFKA_USER $KAFKA_GROUP
    postrotate
        systemctl reload kafka.service
    endscript
}

$ZOOKEEPER_LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $KAFKA_USER $KAFKA_GROUP
    postrotate
        systemctl reload zookeeper.service
    endscript
}
EOF

# Set up cron job for health checks
log "Setting up health check cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/kafka-health-check.sh >> /var/log/kafka-health.log 2>&1") | crontab -

# Create backup script
log "Creating backup script..."
sudo tee /usr/local/bin/kafka-backup.sh > /dev/null <<'EOF'
#!/bin/bash

BACKUP_DIR="/var/backups/kafka"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating Kafka backup at $DATE..."

# Backup configuration
tar -czf $BACKUP_DIR/kafka-config-$DATE.tar.gz \
    /opt/kafka/config \
    /etc/systemd/system/kafka.service \
    /etc/systemd/system/zookeeper.service

# Backup data (if needed)
# tar -czf $BACKUP_DIR/kafka-data-$DATE.tar.gz /var/lib/kafka/data

echo "Backup completed: $BACKUP_DIR/kafka-config-$DATE.tar.gz"
EOF

sudo chmod +x /usr/local/bin/kafka-backup.sh

# Final status check
log "Performing final status check..."
/usr/local/bin/kafka-health-check.sh

log "=== Kafka Installation Complete ==="
log "Kafka is now running on Oracle server"
log "Bootstrap servers: $(hostname -I | awk '{print $1}'):9092"
log "External listeners: $(hostname -I | awk '{print $1}'):29092"
log "Zookeeper: $(hostname -I | awk '{print $1}'):2181"
log ""
log "Useful commands:"
log "  Check status: sudo systemctl status kafka zookeeper"
log "  Monitor: /usr/local/bin/kafka-monitor.sh"
log "  Health check: /usr/local/bin/kafka-health-check.sh"
log "  Backup: /usr/local/bin/kafka-backup.sh"
log "  Stop: sudo systemctl stop kafka zookeeper"
log "  Start: sudo systemctl start zookeeper kafka"
log "  Restart: sudo systemctl restart kafka zookeeper" 