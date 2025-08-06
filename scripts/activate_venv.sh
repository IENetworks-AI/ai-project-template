#!/bin/bash

# Virtual Environment Activation Script
# This script activates the virtual environment and sets up the development environment

set -e

echo "🔧 Setting up development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing/upgrading Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install kafka-python confluent-kafka pyyaml

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export KAFKA_CONFIG_PATH="$(pwd)/config/kafka_config.yaml"

echo "✅ Virtual environment activated!"
echo "📋 Environment variables set:"
echo "  - PYTHONPATH: $PYTHONPATH"
echo "  - KAFKA_CONFIG_PATH: $KAFKA_CONFIG_PATH"
echo ""
echo "🎯 You can now run Python scripts with Kafka integration!"
echo ""
echo "📋 Available commands:"
echo "  - Test local Kafka: python3 test_kafka_integration.py"
echo "  - Run ML pipeline: python3 pipelines/ai_pipeline.py"
echo "  - Start API server: python3 api/app.py"
echo "  - Deactivate venv: deactivate"
echo ""
echo "💡 To use this environment in a new terminal, run:"
echo "   source scripts/activate_venv.sh" 