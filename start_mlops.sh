#!/bin/bash

# MLOps Pipeline Startup Script
# This script starts the entire MLOps environment and performs health checks

set -e

echo "⚽ Starting Real-time Football Match Prediction MLOps Pipeline"
echo "================================================================"

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

# Function to check if a service is healthy
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    print_status "Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            print_success "$service_name is healthy!"
            return 0
        else
            print_warning "$service_name not ready yet (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to wait for Kafka to be ready
wait_for_kafka() {
    print_status "Waiting for Kafka to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
            print_success "Kafka is ready!"
            return 0
        else
            print_warning "Kafka not ready yet (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    print_error "Kafka failed to start after $max_attempts attempts"
    return 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Starting MLOps services..."

# Stop any existing services
print_status "Stopping existing services..."
docker-compose down --remove-orphans

# Start services
print_status "Starting services with docker-compose..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."

# Wait for Zookeeper
sleep 10
print_status "Checking Zookeeper..."
if ! docker-compose exec -T zookeeper echo "Zookeeper is running" > /dev/null 2>&1; then
    print_error "Zookeeper failed to start"
    exit 1
fi
print_success "Zookeeper is running"

# Wait for Kafka
wait_for_kafka

# Create Kafka topic if it doesn't exist
print_status "Creating Kafka topic..."
docker-compose exec -T kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --topic live_football_events \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists

print_success "Kafka topic 'live_football_events' created/verified"

# Wait for Airflow to be ready
print_status "Waiting for Airflow to be ready..."
sleep 30

# Check Airflow health
if check_service_health "Airflow" "http://localhost:8080/health" 60; then
    print_success "Airflow is ready!"
else
    print_warning "Airflow may still be starting up. You can check manually at http://localhost:8080"
fi

# Wait for API to be ready
print_status "Waiting for Model API to be ready..."
sleep 20

# Check API health
if check_service_health "Model API" "http://localhost:8000/health" 30; then
    print_success "Model API is ready!"
else
    print_warning "Model API may still be starting up. You can check manually at http://localhost:8000/health"
fi

# Wait for Dashboard to be ready
print_status "Waiting for Dashboard to be ready..."
sleep 15

# Check Dashboard health
if check_service_health "Dashboard" "http://localhost:8501/_stcore/health" 30; then
    print_success "Dashboard is ready!"
else
    print_warning "Dashboard may still be starting up. You can check manually at http://localhost:8501"
fi

# Display service information
echo ""
echo "🎉 MLOps Pipeline is ready!"
echo "================================================================"
echo ""
echo "📊 Service URLs:"
echo "   • Airflow UI:        http://localhost:8080"
echo "   • Model API:         http://localhost:8000"
echo "   • API Docs:          http://localhost:8000/docs"
echo "   • Dashboard:         http://localhost:8501"
echo "   • Kafka:             localhost:9092"
echo ""
echo "🔧 Useful Commands:"
echo "   • View logs:         docker-compose logs -f"
echo "   • Stop services:     docker-compose down"
echo "   • Restart services:  docker-compose restart"
echo "   • Check status:      docker-compose ps"
echo ""
echo "📈 Next Steps:"
echo "   1. Open the Dashboard at http://localhost:8501"
echo "   2. Start the data producer: python producer/producer.py"
echo "   3. Monitor the pipeline in Airflow at http://localhost:8080"
echo "   4. Test the API: curl http://localhost:8000/health"
echo ""
echo "🚀 Happy predicting! ⚽"
echo ""

# Optional: Start the producer automatically
read -p "Would you like to start the data producer now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting data producer..."
    python producer/producer.py --kafka-broker localhost:9092 --delay 1.0 --max-events 50
fi 