#!/bin/bash

# Kafka Setup Script for ML Pipeline
# This script sets up Kafka topics and initializes the Kafka environment

set -e

echo "🚀 Setting up Kafka for ML Pipeline..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Start Kafka services
start_kafka_services() {
    print_status "Starting Kafka services..."
    
    # Check if docker-compose.kafka.yml exists
    if [ ! -f "docker-compose.kafka.yml" ]; then
        print_error "docker-compose.kafka.yml not found. Please run this script from the project root."
        exit 1
    fi
    
    # Start services
    docker-compose -f docker-compose.kafka.yml up -d
    
    print_success "Kafka services started"
}

# Wait for Kafka to be ready
wait_for_kafka() {
    print_status "Waiting for Kafka to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
            print_success "Kafka is ready"
            return 0
        fi
        
        print_status "Waiting for Kafka... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    print_error "Kafka failed to start within the expected time"
    exit 1
}

# Create Kafka topics
create_topics() {
    print_status "Creating Kafka topics for ML pipeline..."
    
    # Define topics
    declare -a topics=(
        "ml-pipeline-raw-data"
        "ml-pipeline-processed-data"
        "ml-pipeline-model-training"
        "ml-pipeline-model-evaluation"
        "ml-pipeline-prediction-requests"
        "ml-pipeline-prediction-results"
        "ml-pipeline-monitoring"
        "ml-pipeline-model-monitoring"
        "ml-pipeline-alerts"
        "ml-pipeline-dead-letter"
        "health-check-topic"
    )
    
    for topic in "${topics[@]}"; do
        print_status "Creating topic: $topic"
        
        docker exec kafka kafka-topics \
            --bootstrap-server localhost:9092 \
            --create \
            --topic "$topic" \
            --partitions 3 \
            --replication-factor 1 \
            --if-not-exists
        
        if [ $? -eq 0 ]; then
            print_success "Topic $topic created successfully"
        else
            print_warning "Topic $topic may already exist or failed to create"
        fi
    done
}

# List created topics
list_topics() {
    print_status "Listing Kafka topics..."
    
    docker exec kafka kafka-topics \
        --bootstrap-server localhost:9092 \
        --list
}

# Test Kafka connectivity
test_kafka_connectivity() {
    print_status "Testing Kafka connectivity..."
    
    # Test producer
    echo "test-message" | docker exec -i kafka kafka-console-producer \
        --bootstrap-server localhost:9092 \
        --topic health-check-topic
    
    if [ $? -eq 0 ]; then
        print_success "Kafka producer test passed"
    else
        print_error "Kafka producer test failed"
        return 1
    fi
    
    # Test consumer
    timeout 10s docker exec kafka kafka-console-consumer \
        --bootstrap-server localhost:9092 \
        --topic health-check-topic \
        --from-beginning \
        --max-messages 1 > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Kafka consumer test passed"
    else
        print_warning "Kafka consumer test may have timed out (this is normal)"
    fi
}

# Setup Python environment
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Test Python Kafka integration
test_python_kafka() {
    print_status "Testing Python Kafka integration..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run Kafka health check
    python3 -c "
import sys
sys.path.append('src')
from kafka_utils import get_kafka_config, KafkaHealthChecker

try:
    config = get_kafka_config()
    health_checker = KafkaHealthChecker(config)
    health_status = health_checker.check_overall_health()
    print(f'Kafka Health Status: {health_status}')
    if health_status['producer'] and health_status['consumer']:
        print('✅ Kafka integration test passed')
    else:
        print('❌ Kafka integration test failed')
except Exception as e:
    print(f'❌ Kafka integration test failed: {e}')
"
}

# Display service URLs
display_service_urls() {
    echo ""
    echo "🎉 Kafka setup complete!"
    echo ""
    echo "📋 Service URLs:"
    echo "  • Kafka UI: http://localhost:8080"
    echo "  • Schema Registry: http://localhost:8081"
    echo "  • Kafka Connect: http://localhost:8083"
    echo "  • KSQL Server: http://localhost:8088"
    echo "  • Control Center: http://localhost:9021"
    echo ""
    echo "🔧 Kafka Configuration:"
    echo "  • Bootstrap Servers: localhost:9092"
    echo "  • Zookeeper: localhost:2181"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Start the ML pipeline: python pipelines/kafka_ml_pipeline.py"
    echo "  2. Start the API service: python api/kafka_api.py"
    echo "  3. Test the system with sample data"
    echo ""
}

# Main execution
main() {
    echo "🎯 Kafka ML Pipeline Setup"
    echo "=========================="
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Start services
    start_kafka_services
    
    # Wait for Kafka
    wait_for_kafka
    
    # Create topics
    create_topics
    
    # List topics
    list_topics
    
    # Test connectivity
    test_kafka_connectivity
    
    # Setup Python environment
    setup_python_environment
    
    # Test Python integration
    test_python_kafka
    
    # Display results
    display_service_urls
}

# Run main function
main "$@" 