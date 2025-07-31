# ML Pipeline - Sales Prediction Model

A streamlined ML pipeline for training and deploying a sales prediction model using a sample dataset, with Oracle Cloud Infrastructure deployment, modern CI/CD workflow, and a beautiful web API for testing.

## 🏗️ Architecture

```
ai-project-template/
├── config/           # Configuration files (YAML)
├── data/
│   └── processed/    # Processed data and results
├── etl/
│   ├── extract/      # Data extraction (CSV)
│   ├── transform/    # Data preprocessing & feature engineering
│   └── load/         # Data & model persistence
├── pipelines/        # Pipeline orchestration
├── api/              # Flask API server with web UI
├── src/
│   ├── data/         # Training & evaluation logic
│   └── utils/        # Utilities & logging
├── models/           # Trained models
├── tests/            # Unit tests
└── .github/workflows/ # CI/CD pipelines
```

## 🚀 Features

- **Sample Dataset**: Uses Sales Dataset for training
- **Automated Pipeline**: Extract, transform, train, evaluate, and deploy
- **Modern CI/CD**: GitHub Actions with consolidated workflow
- **Team Collaboration**: Test-Branch for safe testing, Main for production
- **Oracle Cloud Integration**: Automated deployment to Oracle Cloud Infrastructure
- **Beautiful Web API**: Flask server with modern UI for model testing
- **Real-time Predictions**: Instant sales predictions via web interface
- **Configurable**: YAML-based configuration management
- **Clean Architecture**: Modular ETL pipeline

## 🌿 Branching Strategy

### Modern Workflow
```
Feature Branches → Test-Branch → Main → Production
```

- **Feature Branches**: Individual development work
- **Test-Branch**: Team collaboration and testing (NO deployment)
- **Main**: Production-ready code with automatic deployment

### Workflow Rules
1. **Developers**: Create PRs to `Test-Branch` for review
2. **Admins**: Review and merge to `main` when approved
3. **Deployment**: Only runs on `main` branch

## 🛠️ Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run Pipeline
```bash
# Run complete ML pipeline
python pipelines/ai_pipeline.py
```

### 3. Check Results
```bash
# View trained model
ls models/

# View evaluation results
cat data/processed/evaluation_results.csv
cat data/processed/evaluation_report.txt
```

## 🌐 Web API Testing

### Access the Web Interface
Once deployed to Oracle Cloud, access your model at:
```
http://139.185.33.139:5000
```

### Features
- **📊 Beautiful Dashboard**: Modern, responsive web interface
- **🎯 Real-time Predictions**: Instant sales predictions
- **🧪 Test Cases**: Pre-built testing scenarios
- **📡 API Documentation**: Built-in endpoint documentation
- **🔧 Health Monitoring**: Live model status and performance

### API Endpoints
- `GET /health` - Health check
- `GET /model/info` - Model information
- `POST /api/predict` - Single prediction
- `POST /api/batch_predict` - Batch predictions
- `GET /test` - Test page with sample scenarios

## 🔧 Configuration

Edit `config/config.yaml` to configure:

- **Oracle Server**: Connection settings for deployment
- **Model Parameters**: Training configuration
- **Data Paths**: Input/output directories
- **Target Column**: "Total Amount" for sales prediction

## 🚀 CI/CD Pipeline

### Consolidated Workflow Jobs

1. **validation**: Code quality, security, documentation, and branch-specific checks
2. **test**: Run unit tests
3. **preprocess**: Extract and transform data
4. **train**: Train and evaluate models
5. **deploy**: Deploy to Oracle Cloud (Main branch only)
6. **summary**: Display results and deployment status

### Branch-Specific Behavior

#### Test-Branch
- ✅ All validation checks
- ✅ Full ML pipeline (test, preprocess, train)
- ✅ Performance evaluation
- ❌ **NO deployment** (safe testing)

#### Main Branch
- ✅ All validation checks
- ✅ Full ML pipeline
- ✅ **Oracle Cloud deployment**
- ✅ **API server deployment**
- ✅ Service configuration
- ✅ Deployment verification

## 🚀 Oracle Cloud Deployment

### Server Setup
1. **Server Details**:
   - IP: `139.185.33.139`
   - Username: `ubuntu`
   - OS: Ubuntu Server

2. **GitHub Secret** (Required):
   - `ORACLE_SSH_KEY`: Your SSH private key content

### Deployment Process
The pipeline automatically:
1. **Tests**: Run unit tests
2. **Preprocesses**: Extract and transform data
3. **Trains**: Train and evaluate models
4. **Deploys**: Deploy to Oracle Cloud server using rsync
5. **Configures**: Sets up systemd service for API server
6. **Starts**: Launches Flask API server with web UI

### Setup Instructions
See `ORACLE_DEPLOYMENT_SETUP.md` for detailed setup instructions.

## 🧪 Testing Your Model

### Web Interface Testing
1. **Access**: Go to `http://139.185.33.139:5000`
2. **Fill Form**: Enter sales data (Date, Gender, Age, Product Category, Quantity, Price)
3. **Get Prediction**: Click "Predict Total Amount" for instant results
4. **Test Cases**: Use the test page for pre-built scenarios

### API Testing
```bash
# Health check
curl http://139.185.33.139:5000/health

# Single prediction
curl -X POST http://139.185.33.139:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
  }'
```

### Python Testing
```python
import requests

# Test prediction
response = requests.post('http://139.185.33.139:5000/api/predict', json={
    "Date": "2024-01-15",
    "Gender": "Female",
    "Age": 25,
    "Product Category": "Beauty",
    "Quantity": 2,
    "Price per Unit": 50.0
})
print(response.json())
```

## 📊 Sample Dataset

The pipeline uses a Sales Dataset with the following features:
- Date, Gender, Age, Product Category
- Quantity, Price per Unit, Total Amount (target)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_preprocess.py -v
```

## 📁 Key Files

- `pipelines/ai_pipeline.py` - Main orchestration
- `api/app.py` - Flask API server with web UI
- `config/config.yaml` - Configuration
- `data/Sales Dataset.csv` - Sample dataset
- `.github/workflows/ml_pipeline.yml` - Consolidated CI/CD workflow
- `deploy.sh` - Oracle server deployment script
- `WORKFLOW_GUIDE.md` - Modern CI/CD workflow guide
- `MODEL_TESTING_GUIDE.md` - Comprehensive testing guide

## 📝 Logs

Logs are automatically generated in the `logs/` directory with timestamps and structured formatting.

## 🤝 Contributing

### For Developers
1. Create feature branch: `git checkout -b feature/description`
2. Make changes and commit
3. Create PR to `Test-Branch` for review
4. Wait for admin approval

### For Admins
1. Review PRs in `Test-Branch`
2. Merge to `main` when approved
3. Monitor deployment to Oracle Cloud

## 📚 Documentation

- `WORKFLOW_GUIDE.md` - Complete workflow guide
- `ORACLE_DEPLOYMENT_SETUP.md` - Oracle deployment setup
- `MODEL_TESTING_GUIDE.md` - Comprehensive testing guide
- `README.md` - This file

## 📄 License

This project is licensed under the MIT License.

---

**Status**: ✅ Streamlined ML pipeline with consolidated CI/CD workflow, Oracle Cloud deployment, and beautiful web API for testing
