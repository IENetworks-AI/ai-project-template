#!/bin/bash

# Local Kafka Setup Script with Virtual Environment
# This script sets up Kafka locally for development with venv activation

set -e

echo "🚀 Setting up Kafka locally for development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install kafka-python confluent-kafka pyyaml

# Start Kafka using Docker Compose
echo "🚀 Starting Kafka with Docker Compose..."
docker-compose -f docker-compose.kafka.yml up -d

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
sleep 30

# Test Kafka connectivity
echo "🧪 Testing Kafka connectivity..."
python3 -c "
import sys
sys.path.append('src')
try:
    from kafka_utils import KafkaConfig, KafkaProducerManager
    config = KafkaConfig()
    producer = KafkaProducerManager(config)
    print('✅ Local Kafka connectivity test passed')
except Exception as e:
    print(f'❌ Local Kafka connectivity test failed: {e}')
    exit(1)
"

echo "✅ Local Kafka setup completed!"
echo ""
echo "📋 Available commands:"
echo "  - Start Kafka: docker-compose -f docker-compose.kafka.yml up -d"
echo "  - Stop Kafka: docker-compose -f docker-compose.kafka.yml down"
echo "  - View logs: docker-compose -f docker-compose.kafka.yml logs -f"
echo "  - Kafka UI: http://localhost:8080"
echo "  - Activate venv: source venv/bin/activate"
echo ""
echo "🎯 Your local Kafka is now ready for development!" 