#!/usr/bin/env python3
"""
ML Pipeline API Server
Provides REST API and Web UI for testing the deployed sales prediction model
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Prediction Model API</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            opacity: 0.9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            font-weight: 600;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .endpoints {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
        }
        .endpoint {
            margin-bottom: 10px;
            padding: 8px;
            background: white;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Sales Prediction Model API</h1>
        <p>Test your deployed ML model on Oracle Cloud</p>
    </div>

    <div class="container">
        <div class="card">
            <h2>📊 Single Prediction</h2>
            <form id="predictionForm">
                <div class="form-group">
                    <label for="date">Date:</label>
                    <input type="date" id="date" name="date" required>
                </div>
                <div class="form-group">
                    <label for="gender">Gender:</label>
                    <select id="gender" name="gender" required>
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="age">Age:</label>
                    <input type="number" id="age" name="age" min="18" max="100" required>
                </div>
                <div class="form-group">
                    <label for="product_category">Product Category:</label>
                    <select id="product_category" name="product_category" required>
                        <option value="">Select Category</option>
                        <option value="Beauty">Beauty</option>
                        <option value="Clothing">Clothing</option>
                        <option value="Electronics">Electronics</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="quantity">Quantity:</label>
                    <input type="number" id="quantity" name="quantity" min="1" max="10" required>
                </div>
                <div class="form-group">
                    <label for="price_per_unit">Price per Unit:</label>
                    <input type="number" id="price_per_unit" name="price_per_unit" min="1" step="0.01" required>
                </div>
                <button type="submit">Predict Total Amount</button>
            </form>
            <div id="predictionResult"></div>
        </div>

        <div class="card">
            <h2>🔧 API Information</h2>
            <div class="info">
                <strong>Model Status:</strong> <span id="modelStatus">Loading...</span><br>
                <strong>Features:</strong> <span id="featureCount">Loading...</span><br>
                <strong>Last Updated:</strong> <span id="lastUpdated">Loading...</span>
            </div>
            
            <h3>📡 API Endpoints</h3>
            <div class="endpoints">
                <div class="endpoint">
                    <strong>GET</strong> /health - Health check
                </div>
                <div class="endpoint">
                    <strong>GET</strong> /model/info - Model information
                </div>
                <div class="endpoint">
                    <strong>POST</strong> /api/predict - Single prediction
                </div>
                <div class="endpoint">
                    <strong>POST</strong> /api/batch_predict - Batch predictions
                </div>
            </div>

            <h3>🧪 Quick Test</h3>
            <button onclick="testAPI()">Test API Connection</button>
            <div id="testResult"></div>
        </div>
    </div>

    <script>
        // Load model info on page load
        window.onload = function() {
            loadModelInfo();
        };

        // Handle prediction form submission
        document.getElementById('predictionForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                Date: formData.get('date'),
                Gender: formData.get('gender'),
                Age: parseInt(formData.get('age')),
                'Product Category': formData.get('product_category'),
                Quantity: parseInt(formData.get('quantity')),
                'Price per Unit': parseFloat(formData.get('price_per_unit'))
            };

            fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('predictionResult');
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                } else {
                    resultDiv.innerHTML = `
                        <div class="success">
                            ✅ Prediction: $${data.prediction.toFixed(2)}<br>
                            📊 Input: ${JSON.stringify(data.input_data, null, 2)}
                        </div>
                    `;
                }
            })
            .catch(error => {
                document.getElementById('predictionResult').innerHTML = 
                    `<div class="error">❌ Error: ${error.message}</div>`;
            });
        });

        // Load model information
        function loadModelInfo() {
            fetch('/model/info')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('modelStatus').textContent = 'Error loading model';
                    document.getElementById('featureCount').textContent = 'N/A';
                    document.getElementById('lastUpdated').textContent = 'N/A';
                } else {
                    document.getElementById('modelStatus').textContent = '✅ Loaded';
                    document.getElementById('featureCount').textContent = data.features_count;
                    document.getElementById('lastUpdated').textContent = new Date(data.model_loaded_at).toLocaleString();
                }
            })
            .catch(error => {
                document.getElementById('modelStatus').textContent = '❌ Error';
                document.getElementById('featureCount').textContent = 'N/A';
                document.getElementById('lastUpdated').textContent = 'N/A';
            });
        }

        // Test API connection
        function testAPI() {
            fetch('/health')
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('testResult');
                if (data.status === 'healthy') {
                    resultDiv.innerHTML = `
                        <div class="success">
                            ✅ API is healthy<br>
                            Model loaded: ${data.model_loaded}<br>
                            Scaler loaded: ${data.scaler_loaded}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ API is not healthy</div>`;
                }
            })
            .catch(error => {
                document.getElementById('testResult').innerHTML = 
                    `<div class="error">❌ Error: ${error.message}</div>`;
            });
        }
    </script>
</body>
</html>
"""

TEST_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .test-case { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .result { margin-top: 10px; padding: 10px; border-radius: 3px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🧪 Model Test Page</h1>
    
    <div class="test-case">
        <h3>Test Case 1: Beauty Product</h3>
        <button onclick="testCase1()">Run Test</button>
        <div id="result1"></div>
    </div>

    <div class="test-case">
        <h3>Test Case 2: Electronics Product</h3>
        <button onclick="testCase2()">Run Test</button>
        <div id="result2"></div>
    </div>

    <div class="test-case">
        <h3>Test Case 3: Clothing Product</h3>
        <button onclick="testCase3()">Run Test</button>
        <div id="result3"></div>
    </div>

    <script>
        function testCase1() {
            const data = {
                Date: '2024-01-15',
                Gender: 'Female',
                Age: 25,
                'Product Category': 'Beauty',
                Quantity: 2,
                'Price per Unit': 50.0
            };
            runTest(data, 'result1');
        }

        function testCase2() {
            const data = {
                Date: '2024-01-15',
                Gender: 'Male',
                Age: 35,
                'Product Category': 'Electronics',
                Quantity: 1,
                'Price per Unit': 500.0
            };
            runTest(data, 'result2');
        }

        function testCase3() {
            const data = {
                Date: '2024-01-15',
                Gender: 'Female',
                Age: 28,
                'Product Category': 'Clothing',
                Quantity: 3,
                'Price per Unit': 100.0
            };
            runTest(data, 'result3');
        }

        function runTest(data, resultId) {
            fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                const resultDiv = document.getElementById(resultId);
                if (result.error) {
                    resultDiv.innerHTML = `<div class="result error">❌ Error: ${result.error}</div>`;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result success">
                            ✅ Prediction: $${result.prediction.toFixed(2)}<br>
                            📊 Input: ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                }
            })
            .catch(error => {
                document.getElementById(resultId).innerHTML = 
                    `<div class="result error">❌ Error: ${error.message}</div>`;
            });
        }
    </script>
</body>
</html>
"""

app = Flask(__name__)

# Global variables for model and scaler
model = None
scaler = None
feature_names = None

def load_model():
    """Load the trained model and scaler"""
    global model, scaler, feature_names
    
    try:
        # Define paths using project root
        models_dir = project_root / 'models'
        data_dir = project_root / 'data' / 'processed'
        
        logger.info(f"Project root: {project_root}")
        logger.info(f"Models directory: {models_dir}")
        logger.info(f"Data directory: {data_dir}")
        
        # Load model
        model_path = models_dir / 'sales_prediction_model.joblib'
        if model_path.exists():
            model = joblib.load(str(model_path))
            logger.info(f"Model loaded successfully from {model_path}")
        else:
            logger.error(f"Model file not found at {model_path}")
            # Check if model files exist in root directory (legacy)
            root_model_path = project_root / 'sales_prediction_model.joblib'
            if root_model_path.exists():
                logger.info(f"Found model in root directory, moving to models/")
                model = joblib.load(str(root_model_path))
                # Move file to correct location
                import shutil
                shutil.move(str(root_model_path), str(model_path))
                logger.info(f"Model moved to {model_path}")
            else:
                logger.error(f"Model file not found in root directory either")
                return False
        
        # Load scaler
        scaler_path = models_dir / 'feature_scaler.joblib'
        if scaler_path.exists():
            scaler = joblib.load(str(scaler_path))
            logger.info(f"Scaler loaded successfully from {scaler_path}")
        else:
            logger.error(f"Scaler file not found at {scaler_path}")
            # Check if scaler files exist in root directory (legacy)
            root_scaler_path = project_root / 'feature_scaler.joblib'
            if root_scaler_path.exists():
                logger.info(f"Found scaler in root directory, moving to models/")
                scaler = joblib.load(str(root_scaler_path))
                # Move file to correct location
                import shutil
                shutil.move(str(root_scaler_path), str(scaler_path))
                logger.info(f"Scaler moved to {scaler_path}")
            else:
                logger.error(f"Scaler file not found in root directory either")
                return False
        
        # Load feature names from processed data
        features_path = data_dir / 'features.csv'
        if features_path.exists():
            features_df = pd.read_csv(str(features_path))
            feature_names = features_df.columns.tolist()
            logger.info(f"Feature names loaded: {len(feature_names)} features")
        else:
            logger.warning(f"Features file not found at {features_path}, using default feature names")
            feature_names = ['feature_' + str(i) for i in range(65)]  # Default based on your model
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def preprocess_input(data):
    """Preprocess input data for prediction"""
    try:
        # Convert input to DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)
        
        # Handle date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df['Date_year'] = df['Date'].dt.year
            df['Date_month'] = df['Date'].dt.month
            df['Date_day'] = df['Date'].dt.day
            df['Date_dayofweek'] = df['Date'].dt.dayofweek
            df = df.drop(columns=['Date'])
        
        # Handle categorical columns
        categorical_columns = ['Gender', 'Product Category']
        for col in categorical_columns:
            if col in df.columns:
                # Simple encoding - you might want to use the same encoding as training
                df[f'{col}_encoded'] = df[col].astype('category').cat.codes
                df = df.drop(columns=[col])
        
        # Ensure all required features are present
        if feature_names:
            missing_features = set(feature_names) - set(df.columns)
            for feature in missing_features:
                df[feature] = 0  # Default value for missing features
            
            # Reorder columns to match training features
            df = df[feature_names]
        
        # Scale features
        if scaler:
            df_scaled = scaler.transform(df)
            return df_scaled
        else:
            return df.values
            
    except Exception as e:
        logger.error(f"Error preprocessing input: {e}")
        return None

@app.route('/')
def home():
    """Home page with model information and prediction form"""
    return render_template_string(HOME_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/model/info')
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_type': type(model).__name__,
        'features_count': len(feature_names) if feature_names else 0,
        'feature_names': feature_names[:10] if feature_names else [],  # Show first 10
        'model_loaded_at': datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make prediction API endpoint"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Preprocess input
        processed_data = preprocess_input(data)
        if processed_data is None:
            return jsonify({'error': 'Error preprocessing input data'}), 400
        
        # Make prediction
        prediction = model.predict(processed_data)
        
        return jsonify({
            'prediction': float(prediction[0]),
            'input_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction API endpoint"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get input data
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': 'No data provided or invalid format'}), 400
        
        # Preprocess input
        processed_data = preprocess_input(data)
        if processed_data is None:
            return jsonify({'error': 'Error preprocessing input data'}), 400
        
        # Make predictions
        predictions = model.predict(processed_data)
        
        return jsonify({
            'predictions': [float(p) for p in predictions],
            'input_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test_page():
    """Test page with sample predictions"""
    return render_template_string(TEST_TEMPLATE)

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        logger.info("Model loaded successfully")
    else:
        logger.error("Failed to load model")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 