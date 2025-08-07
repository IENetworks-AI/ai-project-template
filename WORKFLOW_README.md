# Football Predictions MLOps Workflow

## 📊 Data Pipeline Flow

```mermaid
graph TD
    A[Dummy Data Generator] -->|Football Events| B(Kafka KRaft)
    B --> C[Dashboard (Flask)]
    B --> D[Airflow]
    C --> E[Model API (FastAPI)]
    D --> E
    E --> C
```

### Step-by-Step Flow
1. **Dummy Data Generator**: Simulates football match events and sends them to Kafka.
2. **Kafka (KRaft)**: Streams events in real-time to all consumers.
3. **Dashboard (Flask)**: Consumes Kafka events for live stats, match timeline, and predictions.
4. **Airflow**: Consumes Kafka events for ML pipeline orchestration (feature engineering, retraining, monitoring).
5. **Model API (FastAPI)**: Serves predictions to the dashboard and is used by Airflow for batch scoring.
6. **Dashboard**: Displays all results, system status, and allows Airflow DAG management.

---

## 🚀 Local Run Instructions

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Start Kafka (KRaft) Locally
- Recommended: Use Docker Compose for Kafka, API, Dashboard, Airflow.
```bash
docker-compose up -d kafka
```

### 4. Run Producer Locally
```bash
python producer/producer.py --kafka-broker localhost:9092 --delay 2.0 --max-events 50
```

### 5. Run API Locally
```bash
uvicorn api.app:app --reload --port 8000
```

### 6. Run Dashboard Locally
```bash
python dashboard/flask_app.py
```

### 7. Run Airflow Locally (Optional)
- Airflow is best run via Docker Compose, but you can run it locally if you have it installed:
```bash
airflow db init
airflow webserver &
airflow scheduler &
```

---

## ☁️ Oracle Server Deployment

1. **Install Docker & Docker Compose** (see previous instructions)
2. **Clone the repo**
3. **Configure environment** (see .env or docker-compose.yml)
4. **Run:**
```bash
docker-compose up -d --build
```
5. **Open required ports** (8501, 8000, 8080, 9092)
6. **Access services** via public IP.

---

## 🏈 System Overview

This is a comprehensive MLOps system for real-time football match predictions with the following components:

- **Kafka**: Real-time event streaming for football match data
- **Airflow**: Orchestration of ML pipelines and data workflows
- **FastAPI**: Model serving API for predictions
- **Flask Dashboard**: Dynamic web interface with real-time updates
- **Dummy Data Generator**: Simulates realistic football match events

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Producer      │    │     Kafka       │    │   Dashboard     │
│  (Dummy Data)   │───▶│   (Streaming)   │───▶│   (Flask UI)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airflow       │    │   FastAPI       │    │   Models        │
│ (Orchestration) │    │  (Predictions)  │    │ (ML Models)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start All Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Access Services
- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **Airflow**: http://localhost:8080
- **Kafka**: localhost:9092

### 3. Generate Data
```bash
# Start football event producer
python producer/producer.py --kafka-broker localhost:9092 --delay 2.0 --max-events 50
```

## 📊 Kafka's Role in the System

### What is Kafka?
Apache Kafka is a distributed event streaming platform that enables:
- **Real-time data streaming** from producers to consumers
- **Decoupled architecture** where components don't need to know about each other
- **Scalable message handling** with high throughput
- **Fault tolerance** and data persistence

### How Kafka Works in This Project

1. **Event Production**: The `producer/producer.py` generates realistic football match events and sends them to Kafka
2. **Event Streaming**: Kafka streams these events to multiple consumers simultaneously
3. **Event Consumption**: 
   - Dashboard consumes events for real-time display
   - Airflow consumes events for pipeline processing
   - API can consume events for model predictions

### Kafka Topics
- `live_football_events`: Contains match events (shots, goals, passes, etc.)

### Event Format
```json
{
  "id": 12345,
  "minute": 45,
  "second": 30,
  "type": {"name": "Shot"},
  "team": {"name": "Manchester United"},
  "player": {"name": "Marcus Rashford"},
  "shot": {
    "outcome": {"name": "Goal"},
    "xG": 0.75
  },
  "timestamp": "2025-08-07T10:30:00Z"
}
```

## 🔄 Airflow Integration

### Purpose
Airflow orchestrates the entire MLOps pipeline:
- **Data Ingestion**: Consumes Kafka events
- **Feature Engineering**: Processes raw events into features
- **Model Training**: Retrains models with new data
- **Model Deployment**: Updates production models
- **Monitoring**: Tracks pipeline performance

### DAGs Available
1. **football_pipeline**: Main pipeline for football predictions
2. **retraining_pipeline**: Model retraining workflow

### Airflow Features
- **Web UI**: http://localhost:8080
- **API Access**: REST API for programmatic control
- **DAG Management**: Pause/resume/trigger DAGs
- **Task Monitoring**: Real-time task status

## 🎯 Dashboard Features

### Dynamic UI Components
1. **Sidebar Navigation**:
   - Match selection dropdown
   - System status indicators
   - Airflow controls
   - Recent events list
   - Quick action buttons

2. **Real-time Charts**:
   - Match statistics (shots, possession)
   - Win probability predictions
   - Match timeline
   - Possession breakdown

3. **Interactive Features**:
   - Switch between different matches
   - Real-time data updates (5-second intervals)
   - Airflow DAG management
   - System health monitoring

### Match Selection
- **5 Pre-configured Matches**: Premier League fixtures
- **Dynamic Stats**: Each match has unique statistics
- **Real-time Updates**: Stats change as match progresses

## 🔧 System Status Monitoring

### Service Health Checks
- **Dashboard**: Flask health endpoint
- **API**: FastAPI health endpoint  
- **Airflow**: Webserver health check
- **Kafka**: Connection status and event count

### Status Indicators
- 🟢 **Online**: Service is healthy and responding
- 🔴 **Offline**: Service is down or unreachable
- ⚠️ **Warning**: Service has issues but is partially functional

## 📈 Real-time Features

### Live Data Updates
- **Auto-refresh**: Dashboard updates every 5 seconds
- **Event Streaming**: Kafka events displayed in real-time
- **Dynamic Predictions**: Win probabilities update based on match state
- **Timeline Visualization**: Match events plotted over time

### Interactive Controls
- **Match Switching**: Change between different matches instantly
- **Airflow Management**: Trigger DAGs from dashboard
- **Data Refresh**: Manual refresh button
- **New Match Generation**: Create new match scenarios

## 🚀 Deployment to Oracle Server

### Prerequisites
- Oracle Cloud Infrastructure (OCI) account
- Docker and Docker Compose installed on Oracle server
- SSH access to Oracle instance

### Deployment Steps

#### 1. Prepare Oracle Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 2. Clone and Deploy
```bash
# Clone repository
git clone <your-repo-url>
cd ai-project-template

# Create environment file for Oracle
cat > .env << EOF
KAFKA_BROKER=localhost:9092
AIRFLOW_UID=50000
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### 3. Configure Firewall
```bash
# Open required ports
sudo ufw allow 8501  # Dashboard
sudo ufw allow 8000  # API
sudo ufw allow 8080  # Airflow
sudo ufw allow 9092  # Kafka
sudo ufw allow 2181  # Zookeeper
```

#### 4. Set Up SSL (Optional)
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure nginx for SSL termination
```

### Oracle-Specific Considerations

#### 1. Resource Allocation
- **Minimum**: 2 vCPUs, 8GB RAM
- **Recommended**: 4 vCPUs, 16GB RAM
- **Storage**: At least 50GB for Docker images and data

#### 2. Network Configuration
- **Public IP**: Required for external access
- **Security Lists**: Configure to allow required ports
- **Load Balancer**: Optional for high availability

#### 3. Monitoring
```bash
# Monitor resource usage
htop
docker stats

# Check logs
docker-compose logs -f

# Monitor disk space
df -h
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Dashboard Not Loading
```bash
# Check dashboard logs
docker logs football-dashboard

# Restart dashboard
docker-compose restart dashboard
```

#### 2. Kafka Connection Issues
```bash
# Check Kafka status
docker logs kafka

# Restart Kafka
docker-compose restart kafka
```

#### 3. Airflow Not Starting
```bash
# Initialize Airflow database
docker-compose run airflow-webserver airflow db init

# Create admin user
docker-compose run airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

#### 4. API Connection Issues
```bash
# Check API logs
docker logs football-api

# Test API endpoint
curl http://localhost:8000/health
```

### Performance Optimization

#### 1. Memory Issues
```bash
# Increase Docker memory limit
# Edit /etc/docker/daemon.json
{
  "default-shm-size": "2G",
  "storage-driver": "overlay2"
}
```

#### 2. Disk Space
```bash
# Clean up Docker
docker system prune -a

# Clean up volumes
docker volume prune
```

## 📚 API Documentation

### Dashboard API Endpoints

#### GET `/api/matches`
Returns available matches for selection.

#### POST `/api/select-match`
Select a match to display.
```json
{
  "match_id": "man_utd_liverpool"
}
```

#### GET `/api/match-stats`
Returns current match statistics.

#### GET `/api/prediction`
Returns current win probability predictions.

#### GET `/api/system/status`
Returns system health status for all services.

#### GET `/api/kafka/events`
Returns recent Kafka events.

### Airflow API Endpoints

#### GET `/api/airflow/dags`
Returns list of available DAGs.

#### GET `/api/airflow/dags/{dag_id}/runs`
Returns DAG run history.

#### POST `/api/airflow/dags/{dag_id}/trigger`
Triggers a DAG run.

## 🎯 Usage Examples

### 1. Start a New Match
1. Open dashboard at http://localhost:8501
2. Click "New Match" in sidebar
3. Select a different match from dropdown
4. Watch real-time updates

### 2. Monitor Airflow
1. Click "Open Airflow" in sidebar
2. Navigate to DAGs page
3. Trigger football_pipeline DAG
4. Monitor task execution

### 3. Generate Live Data
```bash
# Start producer with custom parameters
python producer/producer.py \
  --kafka-broker localhost:9092 \
  --delay 1.0 \
  --max-events 100 \
  --home-team "Arsenal" \
  --away-team "Chelsea"
```

### 4. Check System Health
```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs dashboard
docker-compose logs api
docker-compose logs airflow-webserver
```

## 🔄 Continuous Integration

### GitHub Actions Workflow
```yaml
name: Deploy to Oracle
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Oracle
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.ORACLE_HOST }}
          username: ${{ secrets.ORACLE_USERNAME }}
          key: ${{ secrets.ORACLE_SSH_KEY }}
          script: |
            cd ai-project-template
            git pull
            docker-compose down
            docker-compose up -d --build
```

## 📊 Monitoring and Alerting

### Metrics to Monitor
- **Response Time**: API and dashboard response times
- **Error Rate**: Failed requests and exceptions
- **Resource Usage**: CPU, memory, disk usage
- **Event Throughput**: Kafka messages per second
- **DAG Success Rate**: Airflow pipeline success rate

### Alerting Setup
```bash
# Set up monitoring with Prometheus/Grafana
# Configure alerts for:
# - Service downtime
# - High error rates
# - Resource exhaustion
# - Pipeline failures
```

## 🎉 Conclusion

This MLOps system provides:
- **Real-time football predictions** with live data streaming
- **Dynamic web interface** with match selection and real-time updates
- **Robust orchestration** with Airflow pipelines
- **Scalable architecture** with Kafka event streaming
- **Production-ready deployment** with Oracle Cloud integration

The system demonstrates modern MLOps practices including:
- Event-driven architecture
- Real-time data processing
- Automated model pipelines
- Comprehensive monitoring
- Cloud-native deployment

For questions or issues, please refer to the troubleshooting section or create an issue in the repository. 

## ⚡ Scheduled Producer: Showcasing Kafka & Airflow Collaboration

The producer can now be run on a schedule (interval or cron) using APScheduler. This allows you to:
- Continuously generate and stream new football match events to Kafka every N seconds (or on a cron schedule).
- The dashboard consumes these events in real time for live stats and timeline.
- Airflow can be configured to run batch jobs (e.g., retraining, analytics) on a schedule or in response to new data in Kafka.

### Example: Run Producer Every 5 Seconds
```bash
python producer/producer.py --kafka-broker localhost:9092 --delay 1.0 --max-events 10 --schedule-interval 5
```

### Example: Run Producer on a Cron Schedule (every minute)
```bash
python producer/producer.py --kafka-broker localhost:9092 --delay 1.0 --max-events 10 --schedule-cron "* * * * *"
```

**How this helps:**
- Kafka enables real-time streaming to the dashboard (for live updates) and to Airflow (for batch ML/data pipelines).
- Airflow can be scheduled to process new data from Kafka, retrain models, or trigger analytics, showing true MLOps collaboration.
- This setup demonstrates how event-driven and scheduled workflows can coexist and power modern data/ML systems. 