#!/bin/bash

# Switch to Oracle Configuration Script
# This script switches the Kafka configuration from local to Oracle deployment

set -e

echo "🔄 Switching to Oracle Kafka configuration..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Backup current config
if [ -f "config/kafka_config.yaml" ]; then
    echo "💾 Backing up current Kafka config..."
    cp config/kafka_config.yaml config/kafka_config_local.yaml
fi

# Switch to Oracle config
if [ -f "config/oracle_kafka_config.yaml" ]; then
    echo "🔄 Switching to Oracle Kafka configuration..."
    cp config/oracle_kafka_config.yaml config/kafka_config.yaml
    echo "✅ Switched to Oracle Kafka configuration"
else
    echo "❌ Oracle Kafka configuration not found: config/oracle_kafka_config.yaml"
    exit 1
fi

# Update environment variables
export KAFKA_CONFIG_PATH="$(pwd)/config/kafka_config.yaml"
export KAFKA_DEPLOYMENT="oracle"

echo "✅ Configuration switched to Oracle!"
echo "📋 Current settings:"
echo "  - KAFKA_CONFIG_PATH: $KAFKA_CONFIG_PATH"
echo "  - KAFKA_DEPLOYMENT: $KAFKA_DEPLOYMENT"
echo ""
echo "🎯 You can now connect to Oracle Kafka server!"
echo ""
echo "📋 Available commands:"
echo "  - Test Oracle Kafka: python3 test_oracle_kafka.py"
echo "  - Switch back to local: ./scripts/switch_to_local.sh"
echo "  - Deactivate venv: deactivate" 