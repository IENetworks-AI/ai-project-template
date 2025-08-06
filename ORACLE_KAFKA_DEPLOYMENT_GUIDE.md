# Oracle Kafka Deployment Guide

This guide provides comprehensive instructions for deploying Kafka on Oracle Cloud Infrastructure with full functionality for your ML pipeline system.

## 🎯 Overview

This deployment sets up a complete Kafka ecosystem on your Oracle server (139.185.33.139) with:

- **Apache Kafka 3.6.1** with Zookeeper
- **ML Pipeline Integration** with dedicated topics
- **Monitoring Dashboard** with real-time status
- **Automated Backups** and health checks
- **Systemd Services** for production deployment
- **Firewall Configuration** for security

## 🚀 Quick Start

### Step 1: Deploy to Oracle Server

Run the deployment script on your Oracle server:

```bash
# SSH to Oracle server
ssh ubuntu@139.185.33.139

# Clone or upload your project
cd /home/ubuntu
git clone <your-repo-url> ai-project-template
cd ai-project-template

# Run the Kafka deployment
chmod +x deployment/oracle_kafka_deployment.sh
./deployment/oracle_kafka_deployment.sh
```

### Step 2: Verify Installation

Check that all services are running:

```bash
# Check Kafka services
sudo systemctl status kafka zookeeper

# Check ML pipeline service
sudo systemctl status ml-pipeline

# Check monitoring service
sudo systemctl status kafka-monitoring
```

### Step 3: Access Monitoring Dashboard

Open your browser and navigate to:
- **Dashboard**: http://139.185.33.139:8080
- **API Status**: http://139.185.33.139:8080/api/kafka/status

## 📋 Detailed Installation

### Prerequisites

- Oracle Cloud Infrastructure instance (139.185.33.139)
- Ubuntu 20.04 or later
- SSH access with sudo privileges
- At least 4GB RAM and 20GB storage

### Manual Installation Steps

If you prefer manual installation:

#### 1. Install Java and Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Java 11
sudo apt-get install -y openjdk-11-jdk

# Install other dependencies
sudo apt-get install -y curl wget unzip net-tools htop vim git
```

#### 2. Install Kafka

```bash
# Download Kafka
cd /tmp
wget https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz

# Extract to /opt
sudo tar -xzf kafka_2.13-3.6.1.tgz -C /opt/
sudo ln -sf /opt/kafka_2.13-3.6.1 /opt/kafka

# Create kafka user
sudo groupadd -r kafka
sudo useradd -r -g kafka -d /opt/kafka -s /bin/bash kafka

# Set ownership
sudo chown -R kafka:kafka /opt/kafka
```

#### 3. Configure Kafka

```bash
# Configure Zookeeper
sudo tee /opt/kafka/config/zookeeper.properties > /dev/null << 'EOF'
dataDir=/var/lib/zookeeper/data
dataLogDir=/var/log/zookeeper
clientPort=2181
maxClientCnxns=60
autopurge.snapRetainCount=3
autopurge.purgeInterval=1
tickTime=2000
initLimit=10
syncLimit=5
EOF

# Configure Kafka
sudo tee /opt/kafka/config/server.properties > /dev/null << 'EOF'
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:29092
advertised.listeners=PLAINTEXT://139.185.33.139:9092,PLAINTEXT_HOST://139.185.33.139:29092
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
inter.broker.listener.name=PLAINTEXT
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs=/var/lib/kafka/data
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
```

#### 4. Create Systemd Services

```bash
# Create directories
sudo mkdir -p /var/lib/kafka/data /var/lib/zookeeper/data
sudo mkdir -p /var/log/kafka /var/log/zookeeper
sudo chown -R kafka:kafka /var/lib/kafka /var/lib/zookeeper /var/log/kafka /var/log/zookeeper

# Zookeeper service
sudo tee /etc/systemd/system/zookeeper.service > /dev/null << 'EOF'
[Unit]
Description=Apache Zookeeper
After=network.target

[Service]
Type=forking
User=kafka
Group=kafka
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
ExecStart=/opt/kafka/bin/zookeeper-server-start.sh -daemon /opt/kafka/config/zookeeper.properties
ExecStop=/opt/kafka/bin/zookeeper-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Kafka service
sudo tee /etc/systemd/system/kafka.service > /dev/null << 'EOF'
[Unit]
Description=Apache Kafka
After=network.target zookeeper.service

[Service]
Type=simple
User=kafka
Group=kafka
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable zookeeper.service kafka.service
sudo systemctl start zookeeper.service
sleep 10
sudo systemctl start kafka.service
```

#### 5. Create ML Pipeline Topics

```bash
# Create topics for ML pipeline
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-raw-data
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-processed-data
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-model-training
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-model-evaluation
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-prediction-requests
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-prediction-results
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-monitoring
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-alerts
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-dead-letter
```

## 🔧 Configuration

### Kafka Configuration Files

The deployment creates several configuration files:

1. **`config/oracle_kafka_config.yaml`** - Oracle-specific Kafka settings
2. **`/opt/kafka/config/server.properties`** - Kafka server configuration
3. **`/opt/kafka/config/zookeeper.properties`** - Zookeeper configuration

### Network Configuration

- **Internal Kafka**: `139.185.33.139:9092`
- **External Kafka**: `139.185.33.139:29092`
- **Zookeeper**: `139.185.33.139:2181`
- **Monitoring Dashboard**: `139.185.33.139:8080`

### Firewall Configuration

The deployment automatically configures UFW firewall:

```bash
# Check firewall status
sudo ufw status

# Manual firewall configuration (if needed)
sudo ufw allow 2181/tcp  # Zookeeper
sudo ufw allow 9092/tcp  # Kafka internal
sudo ufw allow 29092/tcp # Kafka external
sudo ufw allow 8080/tcp  # Monitoring dashboard
```

## 📊 Monitoring and Management

### Built-in Monitoring Tools

1. **Health Check Script**: `/usr/local/bin/kafka-health-check.sh`
2. **Monitoring Script**: `/usr/local/bin/kafka-monitor.sh`
3. **Web Dashboard**: http://139.185.33.139:8080
4. **API Endpoint**: http://139.185.33.139:8080/api/kafka/status

### Manual Monitoring Commands

```bash
# Check service status
sudo systemctl status kafka zookeeper

# Check Kafka topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Check consumer groups
/opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Monitor Kafka logs
sudo journalctl -u kafka.service -f

# Monitor Zookeeper logs
sudo journalctl -u zookeeper.service -f
```

### Automated Health Checks

The deployment sets up automated health checks:

```bash
# Check cron jobs
crontab -l

# View health check logs
tail -f /var/log/kafka-health.log
```

## 🔄 Backup and Recovery

### Automated Backups

The deployment creates automated backups:

```bash
# Manual backup
/home/ubuntu/backup-kafka.sh

# View backup directory
ls -la /home/ubuntu/backups/kafka/

# Restore from backup (example)
sudo tar -xzf /home/ubuntu/backups/kafka/kafka-config-20231201_120000.tar.gz -C /
```

### Backup Schedule

- **Daily backups** at 2:00 AM
- **7-day retention** for configuration backups
- **Log rotation** for Kafka and Zookeeper logs

## 🛠️ Troubleshooting

### Common Issues

#### 1. Kafka Service Won't Start

```bash
# Check logs
sudo journalctl -u kafka.service -n 50

# Check Zookeeper is running
sudo systemctl status zookeeper.service

# Check Java installation
java -version

# Check disk space
df -h
```

#### 2. Connection Issues

```bash
# Test local connectivity
telnet localhost 9092
telnet localhost 2181

# Test external connectivity
telnet 139.185.33.139 29092

# Check firewall
sudo ufw status
```

#### 3. Topic Creation Issues

```bash
# Check if topics exist
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Delete and recreate topic (if needed)
/opt/kafka/bin/kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic ml-pipeline-raw-data
/opt/kafka/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ml-pipeline-raw-data
```

### Performance Tuning

#### Memory Configuration

For production environments, adjust JVM settings:

```bash
# Edit Kafka startup script
sudo vim /opt/kafka/bin/kafka-server-start.sh

# Add these lines before the exec command:
export KAFKA_HEAP_OPTS="-Xmx2G -Xms2G"
export KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:+ExplicitGCInvokesConcurrent -XX:MaxInlineLevel=15"
```

#### Disk I/O Optimization

```bash
# Check disk I/O
iostat -x 1

# Optimize for SSD (if using SSD)
echo 'vm.swappiness=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔌 Integration with ML Pipeline

### Python Integration

The deployment includes Oracle-specific Kafka integration:

```python
# Example usage
from src.oracle_kafka_integration import OracleKafkaProducer, OracleKafkaConsumer, get_oracle_kafka_config

# Get configuration
config = get_oracle_kafka_config()

# Create producer
producer = OracleKafkaProducer(config)

# Send message
message = {
    'message_id': 'test-123',
    'message_type': 'raw_data',
    'timestamp': '2023-12-01T12:00:00Z',
    'source': 'ml-pipeline',
    'data': {'feature1': 1.0, 'feature2': 2.0}
}

producer.send_message('ml-pipeline-raw-data', message)
producer.close()

# Create consumer
consumer = OracleKafkaConsumer(config, 'test-consumer-group')

def message_handler(message_data):
    print(f"Received: {message_data}")

consumer.start_consuming(['ml-pipeline-raw-data'], message_handler)
```

### API Integration

The ML pipeline API can use Kafka for:

- **Data ingestion** from external sources
- **Model training** coordination
- **Prediction requests** and results
- **Monitoring** and alerting
- **Pipeline orchestration**

## 📈 Scaling Considerations

### For High Volume

1. **Increase partitions** for topics:
```bash
/opt/kafka/bin/kafka-topics.sh --alter --bootstrap-server localhost:9092 --topic ml-pipeline-raw-data --partitions 4
```

2. **Add more brokers** (requires cluster setup)
3. **Use multiple consumer groups** for parallel processing
4. **Implement partitioning** strategies

### For High Availability

1. **Set up Kafka cluster** with multiple brokers
2. **Configure replication factor** > 1
3. **Use external Zookeeper cluster**
4. **Implement monitoring** and alerting

## 🔒 Security Considerations

### Current Setup (Development)

- **PLAINTEXT** protocol (no encryption)
- **No authentication** (open access)
- **Firewall protection** via UFW

### Production Security

For production environments, consider:

1. **SSL/TLS encryption**:
```bash
# Generate certificates
keytool -keystore kafka.server.keystore.jks -alias localhost -validity 365 -genkey
```

2. **SASL authentication**:
```bash
# Configure SASL in server.properties
sasl.enabled.mechanisms=PLAIN
sasl.mechanism.inter.broker.protocol=PLAIN
```

3. **ACL (Access Control Lists)**:
```bash
# Create ACLs for topics
/opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:producer --operation Write --topic ml-pipeline-raw-data
```

## 📞 Support and Maintenance

### Regular Maintenance

1. **Daily**: Check health status
2. **Weekly**: Review logs and performance
3. **Monthly**: Update Kafka version
4. **Quarterly**: Review backup and recovery procedures

### Log Locations

- **Kafka logs**: `/var/log/kafka/`
- **Zookeeper logs**: `/var/log/zookeeper/`
- **System logs**: `sudo journalctl -u kafka.service`
- **Health check logs**: `/var/log/kafka-health.log`
- **Backup logs**: `/var/log/kafka-backup.log`

### Useful Commands

```bash
# Restart all services
sudo systemctl restart zookeeper kafka ml-pipeline kafka-monitoring

# Check disk usage
du -sh /var/lib/kafka/data /var/lib/zookeeper/data

# Monitor network connections
netstat -tlnp | grep -E ':(9092|2181|8080)'

# Check process status
ps aux | grep -E '(kafka|zookeeper)'
```

## 🎉 Success Indicators

Your Kafka deployment is successful when:

✅ **All services are running**:
```bash
sudo systemctl is-active kafka zookeeper ml-pipeline kafka-monitoring
```

✅ **Topics are created**:
```bash
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

✅ **Dashboard is accessible**: http://139.185.33.139:8080

✅ **API returns status**: http://139.185.33.139:8080/api/kafka/status

✅ **Health checks pass**:
```bash
/usr/local/bin/kafka-health-check.sh
```

## 🚀 Next Steps

1. **Test the ML pipeline** with Kafka integration
2. **Monitor performance** and adjust settings
3. **Set up alerts** for critical issues
4. **Plan for scaling** as your data volume grows
5. **Implement security** measures for production

---

**Congratulations!** You now have a fully functional Kafka deployment on Oracle Cloud Infrastructure with complete ML pipeline integration, monitoring, and management capabilities. 