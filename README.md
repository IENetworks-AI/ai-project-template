# Oracle AI Project - MLOps Pipeline

A production-grade, modular MLOps pipeline for AI/ML projects deployed on Oracle Cloud Infrastructure.

## 🏗️ Architecture

```
ai-project-template/
├── config/           # Configuration files (YAML)
├── data/
│   ├── raw/          # Raw data files
│   └── processed/    # Processed data and models
├── etl/
│   ├── extract/      # Data extraction (CSV, Oracle DB)
│   ├── transform/    # Data preprocessing & feature engineering
│   └── load/         # Data & model persistence
├── pipelines/        # Pipeline orchestration
├── src/
│   ├── data/         # Training & evaluation logic
│   ├── validation/   # Data validation
│   └── utils/        # Utilities & logging
├── api/              # Flask API for model serving
├── tests/            # Unit tests
├── docs/             # Documentation
└── .github/workflows/ # CI/CD pipelines
```

## 🚀 Features

- **Modular ETL Pipeline**: Extract from CSV/Oracle DB, transform, and load
- **Oracle Cloud Integration**: Native support for Oracle Database
- **MLOps Ready**: Automated training, evaluation, and deployment
- **RESTful API**: Model serving with prediction endpoints
- **CI/CD Pipeline**: GitHub Actions for automated deployment
- **Configurable**: YAML-based configuration management

## 🛠️ Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Oracle database (optional)
# Edit config/config.yaml with your Oracle DB credentials
```

### 2. Run Pipeline
```bash
# Run complete AI pipeline
python pipelines/ai_pipeline.py
```

### 3. Start API
```bash
# Start Flask API server
python api/app.py
```

### 4. Test API
```bash
# Health check
curl http://localhost:5000/health

# Get model info
curl http://localhost:5000/model/info

# Make prediction
curl -X POST http://localhost:5000/model/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.0, 2.0, 3.0, 4.0]}'
```

## 🔧 Configuration

Edit `config/config.yaml` to configure:

- **Oracle Database**: Connection settings
- **Model Parameters**: Training configuration
- **Data Paths**: Input/output directories
- **Server Settings**: Oracle Cloud deployment

## 🚀 Deployment

### Oracle Cloud Setup
1. **Server Details**:
   - IP: `139.185.33.139`
   - Username: `ubuntu`
   - OS: Ubuntu Server (AI/ML-optimized)

2. **GitHub Secrets** (Required):
   - `SSH_PRIVATE_KEY`: Your SSH private key
   - `SSH_USER`: `ubuntu`
   - `SSH_HOST`: `139.185.33.139`
   - `SSH_TARGET_DIR`: `/home/ubuntu/ai-project`

### CI/CD Pipeline
The pipeline automatically:
1. **Tests**: Run unit tests
2. **Preprocesses**: Extract and transform data
3. **Trains**: Train and evaluate models
4. **Deploys**: Deploy to Oracle Cloud server

## 📊 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /model/info` - Model information
- `POST /model/predict` - Make predictions
- `GET /data/features` - Get processed features

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_preprocess.py -v
```

## 📁 Key Files

- `pipelines/ai_pipeline.py` - Main orchestration
- `config/config.yaml` - Configuration
- `api/app.py` - Flask application
- `.github/workflows/data_pipeline.yml` - CI/CD workflow

## 🔄 Migration from Old Structure

The project has been migrated from the old structure to a modular MLOps architecture:

- **Old**: Single scripts in `src/`
- **New**: Modular ETL, pipelines, and API structure
- **Old**: Hardcoded Oracle server settings
- **New**: Flexible configuration with GitHub secrets
- **Old**: Basic training scripts
- **New**: Comprehensive ML pipeline with evaluation

## 📝 Logs

Logs are automatically generated in the `logs/` directory with timestamps and structured formatting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Status**: ✅ Production-ready MLOps pipeline for Oracle Cloud Infrastructure
