# Kafka Integration Guide for ML Pipeline

This guide explains how to set up and use Kafka with the ML pipeline system for real-time data processing, model training, and prediction serving.

## 🎯 Overview

The Kafka integration provides:
- **Real-time data streaming** for ML pipeline stages
- **Asynchronous processing** with message queues
- **Scalable architecture** for distributed ML workloads
- **Monitoring and observability** through Kafka topics
- **Fault tolerance** with message persistence

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

## 🚀 Quick Start

### 1. Setup Kafka Infrastructure

```bash
# Make the setup script executable
chmod +x scripts/setup_kafka.sh

# Run the Kafka setup
./scripts/setup_kafka.sh
```

This will:
- Start Kafka, Zookeeper, and related services
- Create all required topics
- Test connectivity
- Setup Python environment

### 2. Start the ML Pipeline

```bash
# Start the Kafka-integrated ML pipeline
python pipelines/kafka_ml_pipeline.py
```

### 3. Start the API Service

```bash
# Start the Kafka API service
python api/kafka_api.py
```

## 🏗️ Architecture

### Kafka Topics

| Topic | Purpose | Message Type |
|-------|---------|--------------|
| `ml-pipeline-raw-data` | Raw data ingestion | RAW_DATA |
| `ml-pipeline-processed-data` | Processed data | PROCESSED_DATA |
| `ml-pipeline-model-training` | Model training events | MODEL_TRAINING |
| `ml-pipeline-prediction-requests` | Prediction requests | PREDICTION_REQUEST |
| `ml-pipeline-prediction-results` | Prediction results | PREDICTION_RESULT |
| `ml-pipeline-monitoring` | Pipeline monitoring | MONITORING |
| `ml-pipeline-alerts` | System alerts | ALERT |

### Pipeline Stages

1. **Data Ingestion** → Raw data topic
2. **Data Processing** → Processed data topic
3. **Model Training** → Training results topic
4. **Prediction Serving** → Prediction results topic
5. **Monitoring** → All topics

## 🔧 Configuration

### Kafka Configuration

Edit `config/kafka_config.yaml` to customize:

```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  security_protocol: "PLAINTEXT"

topics:
  raw_data_topic: "ml-pipeline-raw-data"
  processed_data_topic: "ml-pipeline-processed-data"
  # ... more topics

producer:
  acks: "all"
  retries: 3
  batch_size: 16384

consumer:
  group_id: "ml-pipeline-consumer-group"
  auto_offset_reset: "earliest"
```

### Environment Variables

```bash
# Kafka connection
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# API settings
PORT=5000
FLASK_ENV=production
```

## 📊 Usage Examples

### 1. Data Ingestion

```python
from src.kafka_utils import KafkaMLPipeline

# Create pipeline
pipeline = KafkaMLPipeline()

# Ingest data
success = pipeline.ingest_data("data/Sales Dataset.csv")
```

### 2. Request Prediction

```python
# Request prediction
features = [100, 50, 25, 10]  # Example features
success = pipeline.request_prediction(features)
```

### 3. API Usage

```bash
# Ingest data via API
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/Sales Dataset.csv"}'

# Request prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [100, 50, 25, 10]}'

# Get prediction result
curl http://localhost:5000/api/prediction/{message_id}

# Check pipeline status
curl http://localhost:5000/api/status
```

## 🐳 Docker Services

The `docker-compose.kafka.yml` includes:

- **Kafka Broker** (port 9092)
- **Zookeeper** (port 2181)
- **Kafka UI** (port 8080) - Web interface
- **Schema Registry** (port 8081) - Avro schemas
- **Kafka Connect** (port 8083) - Data connectors
- **KSQL Server** (port 8088) - Stream processing
- **Control Center** (port 9021) - Management UI

### Service URLs

- **Kafka UI**: http://localhost:8080
- **Control Center**: http://localhost:9021
- **Schema Registry**: http://localhost:8081

## 🔍 Monitoring

### Health Checks

```bash
# Check Kafka health
curl http://localhost:5000/api/health/kafka

# Check overall pipeline status
curl http://localhost:5000/api/status
```

### Topic Monitoring

```bash
# List topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Monitor topic messages
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ml-pipeline-raw-data \
  --from-beginning
```

## 🛠️ Development

### Adding New Topics

1. Add topic to `config/kafka_config.yaml`:
```yaml
topics:
  new_topic: "ml-pipeline-new-topic"
```

2. Add to setup script:
```bash
# In scripts/setup_kafka.sh
declare -a topics=(
  # ... existing topics
  "ml-pipeline-new-topic"
)
```

3. Create consumer/producer in your code:
```python
from src.kafka_utils import KafkaProducerManager, KafkaConsumerManager

# Producer
producer = KafkaProducerManager(config)
producer.send_message("ml-pipeline-new-topic", message)

# Consumer
consumer = KafkaConsumerManager(config, "new-consumer-group")
consumer.start_consuming(["ml-pipeline-new-topic"], message_handler)
```

### Custom Message Types

1. Add to `MessageType` enum in `src/kafka_utils.py`:
```python
class MessageType(Enum):
    # ... existing types
    NEW_MESSAGE_TYPE = "new_message_type"
```

2. Create message:
```python
message = create_message(
    MessageType.NEW_MESSAGE_TYPE,
    {"data": "example"},
    "source-name"
)
```

## 🔧 Troubleshooting

### Common Issues

1. **Kafka not starting**
   ```bash
   # Check Docker logs
   docker-compose -f docker-compose.kafka.yml logs kafka
   
   # Restart services
   docker-compose -f docker-compose.kafka.yml restart
   ```

2. **Connection refused**
   ```bash
   # Check if Kafka is running
   docker ps | grep kafka
   
   # Test connectivity
   docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   ```

3. **Python import errors**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

```python
from src.kafka_utils import KafkaHealthChecker

health_checker = KafkaHealthChecker(config)
status = health_checker.check_overall_health()
print(f"Health status: {status}")
```

## 📈 Performance Tuning

### Producer Settings

```yaml
producer:
  batch_size: 32768  # Increase for better throughput
  linger_ms: 10      # Wait longer for batching
  compression_type: "snappy"  # Enable compression
```

### Consumer Settings

```yaml
consumer:
  max_poll_records: 1000  # Process more records per poll
  fetch_max_bytes: 52428800  # Larger fetch size
```

### Topic Configuration

```bash
# Create topic with custom settings
docker exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic high-throughput-topic \
  --partitions 6 \
  --replication-factor 1 \
  --config retention.ms=86400000
```

## 🔒 Security

### SSL/TLS Configuration

```yaml
kafka:
  security_protocol: "SSL"
  ssl_cafile: "/path/to/ca.pem"
  ssl_certfile: "/path/to/cert.pem"
  ssl_keyfile: "/path/to/key.pem"
```

### SASL Authentication

```yaml
kafka:
  security_protocol: "SASL_PLAINTEXT"
  sasl_mechanism: "PLAIN"
  sasl_username: "your-username"
  sasl_password: "your-password"
```

## 📚 API Reference

### KafkaProducerManager

```python
producer = KafkaProducerManager(config)

# Send single message
producer.send_message(topic, message, key)

# Send batch messages
producer.send_batch(topic, messages, key)

# Close producer
producer.close()
```

### KafkaConsumerManager

```python
consumer = KafkaConsumerManager(config, group_id)

# Start consuming
consumer.start_consuming(topics, message_handler)

# Stop consuming
consumer.stop_consuming()
```

### KafkaMessage

```python
message = KafkaMessage(
    message_id="unique-id",
    message_type=MessageType.RAW_DATA,
    timestamp="2024-01-01T00:00:00",
    source="data-ingestion",
    data={"key": "value"},
    metadata={"optional": "data"}
)
```

## 🎯 Best Practices

1. **Error Handling**: Always handle Kafka exceptions gracefully
2. **Message Idempotency**: Ensure message processing is idempotent
3. **Monitoring**: Monitor topic lag and consumer health
4. **Backup**: Configure topic retention and backup strategies
5. **Testing**: Test with different message sizes and volumes

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Kafka logs: `docker logs kafka`
3. Test connectivity with kafka-console tools
4. Verify configuration in `config/kafka_config.yaml`

---

**Happy streaming! 🚀** 