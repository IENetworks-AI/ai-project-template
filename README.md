# Retail Sales Insight & Top Category Dashboard

A production-grade, modular, and CI/CD-ready pipeline for a Flask-based data insight API that provides retail sales analytics and top product category insights.

## 🎯 Objective

Design the data engineering pipeline + API logic for a retail MLOps demo application that simulates a real-world CI/CD system for deploying daily/weekly sales insights to a RESTful Flask API.

## 🏗️ Architecture

```
ai-project-template/
├── config/                 # Configuration files
│   └── config.yaml        # Pipeline configuration
├── data/                  # Data storage
│   ├── raw/              # Ingested sales CSV files
│   └── processed/        # Cleaned, enriched data
├── docs/                 # Documentation
├── etl/                  # Extract-Transform-Load scripts
│   ├── extract/          # Load CSVs
│   ├── transform/        # Clean + aggregate sales
│   └── load/            # Save final output
├── pipelines/            # Pipeline orchestration logic
│   └── data_pipeline.py # Main pipeline orchestration
├── src/                  # Source code
│   ├── data/            # Preprocessing functions
│   ├── validation/      # Data validation checks
│   └── utils/           # Logging, file I/O helpers
├── tests/               # Unit and integration tests
│   ├── test_etl.py     # ETL component tests
│   └── test_utils.py   # Utility function tests
├── api/                 # Flask API
│   ├── app.py          # Flask entrypoint
│   └── routes.py       # API endpoints
├── .github/            # CI/CD workflows
│   └── workflows/
│       └── data_pipeline.yml # CI/CD workflow
├── requirements.txt    # Python dependencies
├── environment.yml     # Conda environment
└── README.md          # Project documentation
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-project-template

# Install dependencies
pip install -r requirements.txt

# Or using conda
conda env create -f environment.yml
conda activate oracle-ai-pipeline
```

### 2. Add Your Data

Place your sales CSV files in the `data/raw/` directory. The expected format:

```csv
Date,Product Category,Total Amount,Customer ID
2023-01-01,Electronics,1500.0,C001
2023-01-02,Clothing,800.0,C002
2023-01-03,Electronics,2000.0,C003
```

### 3. Run the Pipeline

```bash
# Run the complete data pipeline
python pipelines/data_pipeline.py
```

### 4. Start the API

```bash
# Start the Flask API
python api/app.py
```

### 5. Test the API

```bash
# Health check
curl http://localhost:5000/health

# Get top categories
curl http://localhost:5000/top_categories

# Process data via API
curl -X POST http://localhost:5000/process_data
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check endpoint |
| `/top_categories` | GET | Get top performing product categories |
| `/process_data` | POST | Trigger data processing pipeline |

### Example API Response

```json
{
  "top_categories": [
    {
      "category": "Electronics",
      "total_sales": 3500.0,
      "transaction_count": 2,
      "avg_transaction": 1750.0
    },
    {
      "category": "Clothing",
      "total_sales": 800.0,
      "transaction_count": 1,
      "avg_transaction": 800.0
    }
  ],
  "total_categories": 3,
  "categories_above_threshold": 2,
  "threshold": 1000,
  "total_sales": 4900.0,
  "message": "Found 2 categories above $1,000.00"
}
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- **Data Paths**: Input/output directories
- **Business Logic**: Category thresholds and limits
- **API Settings**: Host, port, debug mode
- **Oracle Cloud**: Deployment settings

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_etl.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 🚀 Deployment

### Oracle Cloud Setup

1. **Server Details**:
   - IP: `139.185.33.139`
   - Username: `ubuntu`
   - OS: Ubuntu Server (AI/ML-optimized)

2. **GitHub Secrets** (Required):
   - `ORACLE_SSH_KEY`: Your SSH private key
   - `SSH_USER`: `ubuntu`
   - `SSH_HOST`: `139.185.33.139`
   - `SSH_TARGET_DIR`: `/home/ubuntu/ai-project-template`

### CI/CD Pipeline

The pipeline automatically:
1. **Tests**: Run unit tests
2. **Processes**: Extract, transform, and load data
3. **Deploys**: Deploy to Oracle Cloud server

## 📁 Key Files

- `pipelines/data_pipeline.py` - Main orchestration
- `config/config.yaml` - Configuration
- `api/app.py` - Flask application
- `etl/transform/transform_sales.py` - Business logic
- `.github/workflows/data_pipeline.yml` - CI/CD workflow

## 🔧 Development

### Adding New Features

1. **Data Processing**: Add new transformations in `etl/transform/`
2. **API Endpoints**: Add new routes in `api/routes.py`
3. **Validation**: Add new checks in `src/validation/`
4. **Tests**: Add corresponding tests in `tests/`

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
python -m pytest tests/ -v
```

## 📈 Business Logic

The pipeline implements lightweight business logic to compute top product categories:

1. **Data Cleaning**: Remove missing values, convert data types
2. **Aggregation**: Group by Product Category, sum Total Amount
3. **Ranking**: Sort by total sales (descending)
4. **Filtering**: Apply threshold to identify "top" categories
5. **Insights**: Calculate transaction counts and averages

## 🔍 Monitoring

- **Logs**: Structured logging in `logs/` directory
- **API Health**: `/health` endpoint for monitoring
- **Data Quality**: Validation checks in pipeline
- **CI/CD**: GitHub Actions for automated testing and deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Status**: ✅ Production-ready Retail Sales Insight pipeline for Oracle Cloud Infrastructure
