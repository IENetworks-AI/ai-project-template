# Business Insights Dashboard - Sales Analytics

A modern business intelligence platform for analyzing top product categories by sales performance, featuring a beautiful web dashboard, real-time analytics, and deployable business insights.

## 🏗️ Architecture

```
ai-project-template/
├── config/           # Configuration files (YAML)
├── data/
│   └── Sales Dataset.csv    # Sales data for analysis
├── api/              # Flask API server with modern web UI
├── src/
│   └── utils/        # Utilities & logging
├── tests/            # Unit tests
└── .github/workflows/ # CI/CD pipelines
```

## 🚀 Features

- **Business Intelligence**: Top N Product Categories by Sales analysis
- **Modern Dashboard**: Beautiful, responsive web interface with real-time insights
- **Flexible Date Ranges**: Last month, last quarter, last year, or custom periods
- **Interactive Analytics**: Dynamic filtering and ranking of product categories
- **Oracle Cloud Integration**: Automated deployment to Oracle Cloud Infrastructure
- **Real-time Insights**: Instant business intelligence via web interface
- **Configurable Analysis**: Adjustable top N categories and date ranges
- **Clean Architecture**: Modular business logic pipeline

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

### 2. Run Business Insights API
```bash
# Start the API server
python api/app.py
```

### 3. Access Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## 🌐 Web Dashboard Features

### Access the Business Intelligence Dashboard
Once deployed to Oracle Cloud, access your insights at:
```
http://139.185.33.139:5000
```

### Dashboard Features
- **📊 Modern Analytics**: Beautiful, responsive business intelligence interface
- **🎯 Top Categories**: Real-time ranking of product categories by sales
- **📅 Flexible Time Periods**: Analyze last month, quarter, year, or custom ranges
- **📈 Market Share Analysis**: Percentage breakdown of category performance
- **🔧 Interactive Controls**: Adjust top N categories and date ranges
- **📡 Real-time Updates**: Instant analysis results

### API Endpoints
- `GET /health` - Health check and data status
- `POST /api/analyze` - Analyze top product categories
- `GET /api/data/summary` - Get data summary and available categories

## 📊 Business Insight Model

### Purpose
The simplified "Model" represents business insights as deployable logic without complex machine learning training, focusing on MLOps pipeline for logic updates.

### Logic: "Top N Product Categories by Sales"
- **Input**: Date range (last month, last quarter, last year, or custom dates) and N value
- **Output**: Identifies and returns the top N product categories based on Total Amount sold within the given period
- **Format**: Structured JSON with rankings, sales amounts, market share percentages, and transaction counts

### Analysis Features
- **Sales Ranking**: Categories ranked by total sales amount
- **Market Share**: Percentage of total sales for each category
- **Transaction Count**: Number of sales transactions per category
- **Average Sale**: Average transaction value per category
- **Period Summary**: Total sales and analysis period information

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
- `