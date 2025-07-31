# ML Pipeline - Sales Prediction Model

A streamlined ML pipeline for training and deploying a sales prediction model using a sample dataset, with Oracle Cloud Infrastructure deployment.

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
- **MLOps Ready**: GitHub Actions CI/CD pipeline
- **Oracle Cloud Integration**: Automated deployment to Oracle Cloud Infrastructure
- **Configurable**: YAML-based configuration management
- **Clean Architecture**: Modular ETL pipeline

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

## 🔧 Configuration

Edit `config/config.yaml` to configure:

- **Oracle Server**: Connection settings for deployment
- **Model Parameters**: Training configuration
- **Data Paths**: Input/output directories
- **Target Column**: "Total Amount" for sales prediction

## 🚀 CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **Test**: Run unit tests
2. **Preprocess**: Extract and transform data
3. **Train**: Train and evaluate models
4. **Deploy**: Deploy to Oracle Cloud Infrastructure

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
5. **Configures**: Sets up systemd service for ML pipeline

### Setup Instructions
See `ORACLE_DEPLOYMENT_SETUP.md` for detailed setup instructions.

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
- `config/config.yaml` - Configuration
- `data/Sales Dataset.csv` - Sample dataset
- `.github/workflows/ml_pipeline.yml` - CI/CD workflow
- `deploy.sh` - Oracle server deployment script

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

**Status**: ✅ Streamlined ML pipeline for sales prediction with Oracle Cloud deployment
