# Apache Airflow Setup and Usage Guide

## Overview
This guide covers the setup and usage of Apache Airflow in the Real-time Football Match Prediction MLOps Pipeline.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kafka         │    │   Airflow       │    │   Model API     │
│   Events        │───▶│   Pipeline      │───▶│   Predictions   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Storage  │
                       │   & Monitoring  │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Start Airflow Services

```bash
# Start Airflow webserver and scheduler
docker-compose up -d airflow-webserver airflow-scheduler

# Check service status
docker-compose ps
```

### 2. Access Airflow Web UI

- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow

### 3. Initialize Airflow Database (First Time Only)

```bash
# Initialize the database
docker exec airflow-webserver airflow db init

# Create admin user
docker exec airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin123

# Start the webserver
docker exec airflow-webserver airflow webserver --port 8080
```

## 📁 DAG Structure

### Available DAGs

| DAG Name | Description | Schedule | Status |
|----------|-------------|----------|--------|
| `football_pipeline` | Real-time football match prediction pipeline | `*/5 * * * *` (every 5 min) | Active |
| `retraining_pipeline` | Model retraining and evaluation pipeline | `0 2 * * 0` (weekly) | Active |

### DAG Locations
- **DAGs Directory**: `./dags/`
- **Logs Directory**: `./logs/`
- **Plugins Directory**: `./plugins/`

## 🔧 Configuration

### Environment Variables

```bash
# Core Airflow settings
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:////usr/local/airflow/airflow.db
AIRFLOW__CORE__FERNET_KEY=''
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__API__AUTH_BACKEND='airflow.api.auth.backend.basic_auth'
```

### Docker Configuration

```yaml
# docker-compose.yml
airflow-webserver:
  image: apache/airflow:2.7.0
  ports:
    - "8080:8080"
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./data:/opt/airflow/data
```

## 📊 Pipeline Tasks

### Football Pipeline DAG

#### Task Flow
```
consume_kafka_events → engineer_features → call_model_api → store_results
```

#### Task Details

1. **consume_kafka_events**
   - **Purpose**: Consume football events from Kafka
   - **Input**: Kafka topic `live_football_events`
   - **Output**: JSON file with consumed events
   - **Schedule**: Every 5 minutes

2. **engineer_features**
   - **Purpose**: Extract and engineer features from events
   - **Input**: Consumed events JSON
   - **Output**: Feature matrix for model prediction
   - **Dependencies**: consume_kafka_events

3. **call_model_api**
   - **Purpose**: Call the ML model API for predictions
   - **Input**: Engineered features
   - **Output**: Prediction results
   - **Dependencies**: engineer_features

4. **store_results**
   - **Purpose**: Store prediction results and metrics
   - **Input**: Prediction results
   - **Output**: Database records and monitoring data
   - **Dependencies**: call_model_api

### Retraining Pipeline DAG

#### Task Flow
```
collect_training_data → preprocess_data → train_model → evaluate_model → deploy_model
```

## 📝 Usage Examples

### 1. Trigger DAG Manually

```bash
# Trigger football pipeline
docker exec airflow-webserver airflow dags trigger football_pipeline

# Trigger retraining pipeline
docker exec airflow-webserver airflow dags trigger retraining_pipeline
```

### 2. Check DAG Status

```bash
# List all DAGs
docker exec airflow-webserver airflow dags list

# Check specific DAG
docker exec airflow-webserver airflow dags show football_pipeline
```

### 3. View Task Logs

```bash
# View logs for specific task
docker exec airflow-webserver airflow tasks logs football_pipeline consume_kafka_events latest
```

### 4. Test DAG

```bash
# Test DAG without running
docker exec airflow-webserver airflow dags test football_pipeline $(date +%Y-%m-%d)
```

## 🔍 Monitoring and Debugging

### Web UI Monitoring

1. **DAGs View**: http://localhost:8080/dags
2. **Grid View**: http://localhost:8080/grid
3. **Graph View**: http://localhost:8080/graph
4. **Task Instances**: http://localhost:8080/task-instances

### Command Line Monitoring

```bash
# Check DAG runs
docker exec airflow-webserver airflow dags list-runs

# Check task instances
docker exec airflow-webserver airflow tasks list football_pipeline

# Check recent failures
docker exec airflow-webserver airflow dags list-runs --state failed
```

### Log Analysis

```bash
# View scheduler logs
docker-compose logs airflow-scheduler

# View webserver logs
docker-compose logs airflow-webserver

# View specific task logs
docker exec airflow-webserver airflow tasks logs football_pipeline engineer_features latest
```

## 🛠️ Troubleshooting

### Common Issues

1. **DAG Not Appearing**
   ```bash
   # Check DAG file syntax
   docker exec airflow-webserver python -c "import sys; sys.path.append('/opt/airflow/dags'); import football_pipeline"
   
   # Restart scheduler
   docker-compose restart airflow-scheduler
   ```

2. **Task Failures**
   ```bash
   # Check task logs
   docker exec airflow-webserver airflow tasks logs football_pipeline consume_kafka_events latest
   
   # Clear failed tasks
   docker exec airflow-webserver airflow tasks clear football_pipeline --yes
   ```

3. **Database Issues**
   ```bash
   # Reset database (WARNING: This will delete all data)
   docker exec airflow-webserver airflow db reset --yes
   docker exec airflow-webserver airflow db init
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R 50000:50000 ./dags ./logs ./plugins
   ```

### Performance Tuning

#### Scheduler Settings
```bash
# Increase parallelism
AIRFLOW__CORE__PARALLELISM=32

# Increase max active runs
AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=16

# Increase max active tasks
AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=16
```

#### Database Settings
```bash
# Use PostgreSQL for better performance
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
```

## 🔐 Security

### Authentication
- **Default**: Basic authentication
- **Username**: airflow
- **Password**: airflow

### Custom Authentication
```bash
# Enable LDAP authentication
AIRFLOW__API__AUTH_BACKEND='airflow.api.auth.backend.ldap_auth'
AIRFLOW__LDAP__URI='ldap://ldap.example.com'
AIRFLOW__LDAP__USER_FILTER='(uid={})'
```

### SSL/TLS
```bash
# Enable SSL for webserver
AIRFLOW__WEBSERVER__WEB_SERVER_SSL_CERT=/path/to/cert.pem
AIRFLOW__WEBSERVER__WEB_SERVER_SSL_KEY=/path/to/key.pem
```

## 📊 Metrics and Monitoring

### Prometheus Metrics
```bash
# Enable Prometheus metrics
AIRFLOW__METRICS__STATSD_ON=True
AIRFLOW__METRICS__STATSD_HOST=statsd
AIRFLOW__METRICS__STATSD_PORT=8125
```

### Custom Metrics
```python
# In DAG tasks
from airflow.models import Variable
from airflow.utils.db import provide_session

@provide_session
def log_metric(session, metric_name, value):
    Variable.set(metric_name, str(value), session=session)
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/airflow.yml
name: Deploy DAGs
on:
  push:
    paths:
      - 'dags/**'
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Airflow
        run: |
          # Copy DAGs to server
          scp -r dags/ user@server:/opt/airflow/dags/
```

## 📚 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Python API](https://airflow.apache.org/docs/apache-airflow/stable/python-api/index.html)
- [Airflow Docker Image](https://hub.docker.com/r/apache/airflow)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) 