# Kafka Setup and Usage Guide

## Overview
This guide covers the setup and usage of Apache Kafka in the Real-time Football Match Prediction MLOps Pipeline.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Football      │    │   Kafka         │    │   Airflow       │
│   Producer      │───▶│   Broker        │───▶│   Consumer      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Streamlit     │
                       │   Dashboard     │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Start Kafka Services

```bash
# Start Kafka and Zookeeper
docker-compose up -d zookeeper kafka

# Check service status
docker-compose ps
```

### 2. Verify Kafka is Running

```bash
# Check if Kafka is accessible
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list
```

### 3. Create Required Topics

```bash
# Create the main football events topic
docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
  --create --topic live_football_events \
  --partitions 3 --replication-factor 1

# Create additional topics for the pipeline
docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
  --create --topic ml-pipeline-raw-data \
  --partitions 3 --replication-factor 1

docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
  --create --topic ml-pipeline-processed-data \
  --partitions 3 --replication-factor 1

docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
  --create --topic ml-pipeline-prediction-requests \
  --partitions 3 --replication-factor 1
```

## 📊 Topic Structure

### Main Topics

| Topic | Description | Partition Count | Replication Factor |
|-------|-------------|-----------------|-------------------|
| `live_football_events` | Real-time football match events | 3 | 1 |
| `ml-pipeline-raw-data` | Raw data from various sources | 3 | 1 |
| `ml-pipeline-processed-data` | Processed and cleaned data | 3 | 1 |
| `ml-pipeline-prediction-requests` | Model prediction requests | 3 | 1 |
| `ml-pipeline-prediction-results` | Model prediction results | 3 | 1 |
| `ml-pipeline-monitoring` | Pipeline monitoring events | 3 | 1 |

### Message Format

#### Football Events
```json
{
  "id": 1,
  "minute": 15,
  "second": 30,
  "type": {"name": "Shot"},
  "team": {"name": "Manchester United"},
  "player": {"name": "Marcus Rashford"},
  "shot": {"outcome": {"name": "Goal"}},
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### Prediction Requests
```json
{
  "home_goals": 1,
  "away_goals": 0,
  "current_minute": 45,
  "home_shots": 8,
  "away_shots": 3,
  "home_shots_on_target": 4,
  "away_shots_on_target": 1,
  "home_possession": 65.0,
  "away_possession": 35.0,
  "home_xg": 1.2,
  "away_xg": 0.4
}
```

## 🔧 Configuration

### Local Development
- **Broker**: `localhost:9092` (external), `kafka:29092` (internal)
- **Zookeeper**: `localhost:2181`
- **Security**: PLAINTEXT (no authentication)

### Oracle Server Deployment
- **Broker**: `139.185.33.139:9092` (external), `139.185.33.139:29092` (internal)
- **Zookeeper**: `139.185.33.139:2181`
- **Security**: PLAINTEXT (no authentication)

## 📝 Usage Examples

### 1. Start the Football Event Producer

```bash
# Start producer with default settings
python producer/producer.py

# Start with custom settings
python producer/producer.py --kafka-broker localhost:9092 --delay 1.0 --max-events 100
```

### 2. Monitor Topics

```bash
# Monitor live football events
docker exec kafka kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic live_football_events \
  --from-beginning

# Monitor prediction requests
docker exec kafka kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic ml-pipeline-prediction-requests \
  --from-beginning
```

### 3. Produce Test Messages

```bash
# Produce a test football event
docker exec kafka kafka-console-producer \
  --bootstrap-server kafka:29092 \
  --topic live_football_events \
  --property "parse.key=true" \
  --property "key.separator=:"

# Then enter: test:{"id": 999, "minute": 90, "type": {"name": "Goal"}, "team": {"name": "Test Team"}}
```

## 🔍 Monitoring and Debugging

### Check Topic Details
```bash
# List all topics
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list

# Describe specific topic
docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
  --describe --topic live_football_events
```

### Check Consumer Groups
```bash
# List consumer groups
docker exec kafka kafka-consumer-groups --bootstrap-server kafka:29092 --list

# Describe consumer group
docker exec kafka kafka-consumer-groups --bootstrap-server kafka:29092 \
  --describe --group streamlit_consumer
```

### Check Broker Status
```bash
# Check broker configuration
docker exec kafka kafka-configs --bootstrap-server kafka:29092 \
  --entity-type brokers --entity-name 1 --describe
```

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if Kafka is running
   docker-compose ps
   
   # Check Kafka logs
   docker-compose logs kafka
   ```

2. **Topic Not Found**
   ```bash
   # Create missing topic
   docker exec kafka kafka-topics --bootstrap-server kafka:29092 \
     --create --topic live_football_events \
     --partitions 3 --replication-factor 1
   ```

3. **Consumer Not Receiving Messages**
   ```bash
   # Check consumer group offsets
   docker exec kafka kafka-consumer-groups --bootstrap-server kafka:29092 \
     --describe --group streamlit_consumer
   ```

### Performance Tuning

#### Producer Settings
```python
producer_config = {
    'bootstrap_servers': ['localhost:9092'],
    'acks': 'all',
    'retries': 3,
    'batch_size': 16384,
    'linger_ms': 5,
    'buffer_memory': 33554432,
    'compression_type': 'snappy'
}
```

#### Consumer Settings
```python
consumer_config = {
    'bootstrap_servers': ['localhost:9092'],
    'group_id': 'streamlit_consumer',
    'auto_offset_reset': 'latest',
    'enable_auto_commit': True,
    'auto_commit_interval_ms': 1000
}
```

## 🔐 Security (Future Enhancement)

For production deployments, consider implementing:

1. **SASL Authentication**
2. **SSL/TLS Encryption**
3. **ACL Authorization**
4. **Kerberos Integration**

## 📚 Additional Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Platform](https://docs.confluent.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/overview.html) 