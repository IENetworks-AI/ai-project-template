# Real-time Football Match Prediction MLOps Pipeline

A comprehensive MLOps pipeline for real-time football match predictions using Apache Kafka, Apache Airflow, FastAPI, and Streamlit.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   StatsBomb     │    │   Kafka         │    │   Airflow       │
│   Data Source   │───▶│   Producer      │───▶│   Pipeline      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   Model         │
│   Dashboard     │◀───│   Model API     │◀───│   Inference     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-project-template
```

### 2. Start the MLOps Environment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access the Services

- **Airflow UI**: http://localhost:8080
- **FastAPI Model API**: http://localhost:8000
- **Streamlit Dashboard**: http://localhost:8501
- **Kafka**: localhost:9092

### 4. Run the Data Producer

```bash
# Start the Kafka producer to stream football events
python producer/producer.py --kafka-broker localhost:9092 --delay 1.0
```

## 📁 Project Structure

```
ai-project-template/
├── api/                          # FastAPI model serving
│   └── app.py                   # Model API application
├── dashboard/                    # Streamlit dashboard
│   └── app.py                   # Real-time dashboard
├── dags/                        # Airflow DAGs
│   ├── football_pipeline.py     # Main prediction pipeline
│   └── retraining_pipeline.py   # Model retraining pipeline
├── producer/                    # Kafka producer
│   └── producer.py              # Football event producer
├── models/                      # Trained models
├── data/                        # Data storage
├── tests/                       # Unit and integration tests
├── docker-compose.yml           # Docker services configuration
├── Dockerfile.api              # API container
├── Dockerfile.dashboard        # Dashboard container
├── requirements.txt            # Python dependencies
└── .github/workflows/          # CI/CD pipelines
    └── main.yml               # GitHub Actions workflow
```

## 🔧 Services Configuration

### Kafka Configuration
- **Broker**: localhost:9092 (external), kafka:29092 (internal)
- **Topic**: `live_football_events`
- **Zookeeper**: localhost:2181

### Airflow Configuration
- **Web UI**: localhost:8080
- **Default User**: airflow/airflow
- **DAGs**: Automatically loaded from `./dags/`

### Model API Configuration
- **Endpoint**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Prediction**: POST http://localhost:8000/predict

### Dashboard Configuration
- **URL**: http://localhost:8501
- **Auto-refresh**: Configurable
- **Real-time updates**: Kafka consumer

## 📊 Pipeline Components

### 1. Data Ingestion (Kafka Producer)
- Reads StatsBomb football match data
- Streams events in real-time to Kafka
- Configurable delay for simulation

### 2. Feature Engineering (Airflow)
- Consumes events from Kafka
- Calculates match statistics (xG, possession, etc.)
- Prepares features for model inference

### 3. Model Inference (FastAPI)
- Loads pre-trained win probability model
- Provides REST API for predictions
- Health checks and monitoring

### 4. Real-time Dashboard (Streamlit)
- Displays live match statistics
- Shows win probability predictions
- Interactive charts and metrics

### 5. Model Retraining (Airflow)
- Weekly scheduled retraining
- Aggregates historical predictions
- Automatic model deployment

## 🧪 Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v
```

### API Testing
```bash
# Test API health
curl http://localhost:8000/health

# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "home_goals": 1,
    "away_goals": 0,
    "current_minute": 45,
    "home_shots": 8,
    "away_shots": 4,
    "home_shots_on_target": 3,
    "away_shots_on_target": 1,
    "home_possession": 60,
    "away_possession": 40,
    "home_xg": 1.2,
    "away_xg": 0.8
  }'
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Code Quality**: Linting and formatting checks
2. **Unit Testing**: Automated test execution
3. **Integration Testing**: End-to-end service testing
4. **Docker Build**: Container image creation
5. **Deployment**: Automated production deployment
6. **Monitoring**: Health checks and notifications

### Deployment Secrets

Configure these secrets in your GitHub repository:

- `HOST`: Production server hostname
- `USERNAME`: SSH username
- `SSH_KEY`: SSH private key
- `PORT`: SSH port (optional)

## 📈 Monitoring and Logs

### Service Logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs airflow-webserver
docker-compose logs api
docker-compose logs dashboard
```

### Airflow Monitoring
- Access Airflow UI at http://localhost:8080
- Monitor DAG execution and task status
- View task logs and XCom data

### API Monitoring
- Health check: `GET /health`
- Model info: `GET /model-info`
- Prediction metrics: Available in logs

## 🔧 Development

### Local Development Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up pre-commit hooks**:
```bash
pip install pre-commit
pre-commit install
```

3. **Run development server**:
```bash
# API
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# Dashboard
streamlit run dashboard/app.py --server.port 8501
```

### Adding New Features

1. **New DAG**: Add to `dags/` directory
2. **New API endpoint**: Add to `api/app.py`
3. **New dashboard component**: Add to `dashboard/app.py`
4. **New tests**: Add to `tests/` directory

## 🚨 Troubleshooting

### Common Issues

1. **Kafka connection failed**:
   - Check if Zookeeper is running: `docker-compose ps zookeeper`
   - Restart Kafka: `docker-compose restart kafka`

2. **Airflow DAGs not loading**:
   - Check DAG files in `dags/` directory
   - Verify Python syntax
   - Check Airflow logs: `docker-compose logs airflow-scheduler`

3. **API not responding**:
   - Check API logs: `docker-compose logs api`
   - Verify model files exist in `models/` directory
   - Test health endpoint: `curl http://localhost:8000/health`

4. **Dashboard not updating**:
   - Check Kafka connection in dashboard logs
   - Verify API endpoint is accessible
   - Test manual prediction update

### Performance Optimization

1. **Kafka Performance**:
   - Adjust `KAFKA_JMX_PORT` for monitoring
   - Configure appropriate retention policies

2. **Airflow Performance**:
   - Use `LocalExecutor` for single-node setup
   - Configure appropriate parallelism settings

3. **API Performance**:
   - Enable model caching
   - Use async endpoints for I/O operations

## 📚 API Documentation

### Prediction Endpoint

**POST** `/predict`

Request body:
```json
{
  "home_goals": 1,
  "away_goals": 0,
  "current_minute": 45,
  "home_shots": 8,
  "away_shots": 4,
  "home_shots_on_target": 3,
  "away_shots_on_target": 1,
  "home_possession": 60.0,
  "away_possession": 40.0,
  "home_xg": 1.2,
  "away_xg": 0.8
}
```

Response:
```json
{
  "home_win_probability": 0.65,
  "away_win_probability": 0.20,
  "draw_probability": 0.15,
  "confidence": 0.78,
  "timestamp": "2024-01-15T10:30:00",
  "model_version": "1.0.0"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- StatsBomb for providing open football data
- Apache Airflow for workflow orchestration
- Apache Kafka for real-time data streaming
- FastAPI for modern API development
- Streamlit for rapid dashboard development