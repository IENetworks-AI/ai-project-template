#!/bin/bash

# Switch to Local Configuration Script
# This script switches the Kafka configuration from Oracle back to local deployment

set -e

echo "🔄 Switching to local Kafka configuration..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Restore local config
if [ -f "config/kafka_config_local.yaml" ]; then
    echo "🔄 Restoring local Kafka configuration..."
    cp config/kafka_config_local.yaml config/kafka_config.yaml
    echo "✅ Switched to local Kafka configuration"
else
    echo "⚠️ Local Kafka configuration backup not found"
    echo "📝 Creating default local configuration..."
    cat > config/kafka_config.yaml << 'EOF'
# Kafka Configuration for Local Development

kafka:
  # Bootstrap servers (comma-separated list)
  bootstrap_servers: "localhost:9092"
  
  # Security settings
  security_protocol: "PLAINTEXT"
  
  # Topic names for ML pipeline
  topics:
    data_input: "ml-data-input"
    data_processed: "ml-data-processed"
    model_training: "ml-model-training"
    model_predictions: "ml-model-predictions"
    model_evaluation: "ml-model-evaluation"
    system_health: "ml-system-health"
  
  # Producer settings
  producer:
    acks: "all"
    retries: 3
    batch_size: 16384
    linger_ms: 1
    buffer_memory: 33554432
  
  # Consumer settings
  consumer:
    auto_offset_reset: "earliest"
    enable_auto_commit: true
    auto_commit_interval_ms: 1000
    session_timeout_ms: 30000
    heartbeat_interval_ms: 3000
    max_poll_records: 500
    max_poll_interval_ms: 300000

# Application settings
app:
  name: "ML Pipeline Kafka Integration"
  version: "1.0.0"
  environment: "local"
  log_level: "INFO"
EOF
    echo "✅ Created default local Kafka configuration"
fi

# Update environment variables
export KAFKA_CONFIG_PATH="$(pwd)/config/kafka_config.yaml"
export KAFKA_DEPLOYMENT="local"

echo "✅ Configuration switched to local!"
echo "📋 Current settings:"
echo "  - KAFKA_CONFIG_PATH: $KAFKA_CONFIG_PATH"
echo "  - KAFKA_DEPLOYMENT: $KAFKA_DEPLOYMENT"
echo ""
echo "🎯 You can now connect to local Kafka server!"
echo ""
echo "📋 Available commands:"
echo "  - Start local Kafka: ./scripts/setup_local_kafka.sh"
echo "  - Test local Kafka: python3 test_kafka_integration.py"
echo "  - Switch to Oracle: ./scripts/switch_to_oracle.sh"
echo "  - Deactivate venv: deactivate" 