#!/usr/bin/env python3
"""
Business Insight API Server
Provides REST API and Web UI for analyzing top product categories by sales
"""

import os
import sys
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta
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
    <title>Business Insights Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2rem;
            color: #666;
            font-weight: 500;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        }
        
        .card h2 {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
            font-size: 0.95rem;
        }
        
        input, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 16px;
            background: #f8f9fa;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .results {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .result-item {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .result-item:hover {
            transform: translateX(5px);
        }
        
        .result-item h3 {
            font-size: 1.3rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 10px;
        }
        
        .result-item .rank {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .result-item .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat {
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #fee;
            color: #c53030;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #c53030;
        }
        
        .success {
            background: #f0fff4;
            color: #2f855a;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #2f855a;
        }
        
        .info-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .info-panel h3 {
            margin-bottom: 10px;
            font-size: 1.2rem;
        }
        
        .info-panel p {
            opacity: 0.9;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Business Insights Dashboard</h1>
            <p>Analyze Top Product Categories by Sales Performance</p>
        </div>

        <div class="main-content">
            <div class="card">
                <h2>🎯 Analysis Parameters</h2>
                <form id="analysisForm">
                    <div class="form-group">
                        <label for="dateRange">Date Range (2023 Data):</label>
                        <select id="dateRange" name="dateRange" required>
                            <option value="">Select Date Range</option>
                            <option value="last_month">December 2023 (Last Month)</option>
                            <option value="last_quarter">Q4 2023 (Oct-Dec)</option>
                            <option value="last_year">Full Year 2023</option>
                            <option value="custom">Custom Range (2023)</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="customDates" style="display: none;">
                        <label for="startDate">Start Date (2023):</label>
                        <input type="date" id="startDate" name="startDate" min="2023-01-01" max="2023-12-31">
                    </div>
                    
                    <div class="form-group" id="customDates2" style="display: none;">
                        <label for="endDate">End Date (2023):</label>
                        <input type="date" id="endDate" name="endDate" min="2023-01-01" max="2023-12-31">
                    </div>
                    
                    <div class="form-group">
                        <label for="topN">Top N Categories:</label>
                        <input type="number" id="topN" name="topN" min="1" max="20" value="5" required>
                    </div>
                    
                    <button type="submit" class="btn">🚀 Analyze Sales Data</button>
                </form>
                
                <div class="info-panel">
                    <h3>💡 How it works</h3>
                    <p>This insight model analyzes your 2023 sales data to identify the top-performing product categories based on total sales amount within your specified time period.</p>
                    <p><strong>Available Data:</strong> January 1, 2023 - December 31, 2023</p>
                </div>
            </div>

            <div class="results">
                <h2>📈 Analysis Results</h2>
                <div id="resultsContent">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Select parameters and click "Analyze Sales Data" to get started</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Handle date range selection
        document.getElementById('dateRange').addEventListener('change', function() {
            const customDates = document.getElementById('customDates');
            const customDates2 = document.getElementById('customDates2');
            
            if (this.value === 'custom') {
                customDates.style.display = 'block';
                customDates2.style.display = 'block';
            } else {
                customDates.style.display = 'none';
                customDates2.style.display = 'none';
            }
        });

        // Handle form submission
        document.getElementById('analysisForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                date_range: formData.get('dateRange'),
                start_date: formData.get('startDate'),
                end_date: formData.get('endDate'),
                top_n: parseInt(formData.get('topN'))
            };

            // Show loading
            const resultsContent = document.getElementById('resultsContent');
            resultsContent.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Analyzing sales data...</p>
                </div>
            `;

            fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsContent.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                } else {
                    displayResults(data.results, data.summary);
                }
            })
            .catch(error => {
                resultsContent.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
            });
        });

        function displayResults(results, summary) {
            const resultsContent = document.getElementById('resultsContent');
            
            let html = `
                <div class="success">
                    <h3>✅ Analysis Complete</h3>
                    <p><strong>Period:</strong> ${summary.period}</p>
                    <p><strong>Total Sales:</strong> $${summary.total_sales.toLocaleString()}</p>
                    <p><strong>Categories Analyzed:</strong> ${summary.categories_count}</p>
                </div>
            `;
            
            results.forEach((result, index) => {
                const rank = index + 1;
                const rankEmoji = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '🏆';
                
                html += `
                    <div class="result-item">
                        <span class="rank">${rankEmoji} Rank #${rank}</span>
                        <h3>${result.category}</h3>
                        <div class="stats">
                            <div class="stat">
                                <div class="stat-value">$${result.total_sales.toLocaleString()}</div>
                                <div class="stat-label">Total Sales</div>
                            </div>
                            <div class="stat">
                                <div class="stat-value">${result.percentage.toFixed(1)}%</div>
                                <div class="stat-label">Market Share</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            resultsContent.innerHTML = html;
        }
    </script>
</body>
</html>
"""

app = Flask(__name__)

# Global variable for sales data
sales_data = None

def load_sales_data():
    """Load the sales dataset"""
    global sales_data
    
    try:
        data_path = project_root / 'data' / 'Sales Dataset.csv'
        if data_path.exists():
            sales_data = pd.read_csv(str(data_path))
            # Convert Date column to datetime
            sales_data['Date'] = pd.to_datetime(sales_data['Date'])
            logger.info(f"Sales data loaded successfully: {len(sales_data)} records")
            return True
        else:
            logger.error(f"Sales data file not found at {data_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error loading sales data: {e}")
        return False

def get_date_range(date_range, start_date=None, end_date=None):
    """Get date range based on selection - adapted for 2023 data"""
    # Since our data is from 2023, we'll use 2023 as the reference year
    reference_year = 2023
    reference_date = datetime(2023, 12, 31)  # End of 2023
    
    if date_range == 'last_month':
        # Last month of 2023 (December)
        start = datetime(2023, 12, 1)
        end = datetime(2023, 12, 31)
    elif date_range == 'last_quarter':
        # Last quarter of 2023 (October-December)
        start = datetime(2023, 10, 1)
        end = datetime(2023, 12, 31)
    elif date_range == 'last_year':
        # Full year 2023
        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)
    elif date_range == 'custom':
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            raise ValueError("Custom date range requires both start and end dates")
    else:
        raise ValueError("Invalid date range")
    
    return start, end

def analyze_top_categories(date_range, start_date=None, end_date=None, top_n=5):
    """Analyze top N product categories by sales"""
    try:
        if sales_data is None:
            raise ValueError("Sales data not loaded")
        
        # Get date range
        start, end = get_date_range(date_range, start_date, end_date)
        
        # Filter data by date range
        mask = (sales_data['Date'] >= start) & (sales_data['Date'] <= end)
        filtered_data = sales_data[mask]
        
        if len(filtered_data) == 0:
            raise ValueError(f"No sales data found for the selected period: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        
        # Group by product category and calculate total sales
        category_sales = filtered_data.groupby('Product Category')['Total Amount'].agg([
            'sum', 'count', 'mean'
        ]).reset_index()
        
        category_sales.columns = ['category', 'total_sales', 'transaction_count', 'avg_sale']
        
        # Calculate percentage of total sales
        total_sales = category_sales['total_sales'].sum()
        category_sales['percentage'] = (category_sales['total_sales'] / total_sales) * 100
        
        # Sort by total sales and get top N
        top_categories = category_sales.nlargest(top_n, 'total_sales')
        
        # Format results
        results = []
        for _, row in top_categories.iterrows():
            results.append({
                'category': row['category'],
                'total_sales': float(row['total_sales']),
                'transaction_count': int(row['transaction_count']),
                'avg_sale': float(row['avg_sale']),
                'percentage': float(row['percentage'])
            })
        
        # Create summary
        period_text = f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
        if date_range == 'last_month':
            period_text = f"Last Month ({start.strftime('%B %Y')})"
        elif date_range == 'last_quarter':
            period_text = f"Last Quarter ({start.strftime('%B %Y')} - {end.strftime('%B %Y')})"
        elif date_range == 'last_year':
            period_text = f"Last Year ({start.year})"
        
        summary = {
            'period': period_text,
            'total_sales': float(total_sales),
            'categories_count': len(category_sales),
            'records_analyzed': len(filtered_data)
        }
        
        return results, summary
        
    except Exception as e:
        logger.error(f"Error analyzing categories: {e}")
        raise

@app.route('/')
def home():
    """Home page with business insights dashboard"""
    return render_template_string(HOME_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': sales_data is not None,
        'records_count': len(sales_data) if sales_data is not None else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze top product categories by sales"""
    try:
        if sales_data is None:
            return jsonify({'error': 'Sales data not loaded'}), 500
        
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        date_range = data.get('date_range')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        top_n = data.get('top_n', 5)
        
        if not date_range:
            return jsonify({'error': 'Date range is required'}), 400
        
        # Analyze data
        results, summary = analyze_top_categories(date_range, start_date, end_date, top_n)
        
        return jsonify({
            'results': results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/summary')
def data_summary():
    """Get summary of available data"""
    try:
        if sales_data is None:
            return jsonify({'error': 'Sales data not loaded'}), 500
        
        summary = {
            'total_records': len(sales_data),
            'date_range': {
                'start': sales_data['Date'].min().strftime('%Y-%m-%d'),
                'end': sales_data['Date'].max().strftime('%Y-%m-%d')
            },
            'categories': sales_data['Product Category'].unique().tolist(),
            'total_sales': float(sales_data['Total Amount'].sum()),
            'avg_sale': float(sales_data['Total Amount'].mean())
        }
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Data summary error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load sales data on startup
    if load_sales_data():
        logger.info("Sales data loaded successfully")
    else:
        logger.error("Failed to load sales data")
    
    # Configuration for different environments
    import os
    
    # Get configuration from environment variables
    HOST = os.environ.get('HOST', 'localhost')  # Default to localhost
    PORT = int(os.environ.get('PORT', 5000))    # Default to port 5000
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Business Insights API server on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    # Run the app
    app.run(host=HOST, port=PORT, debug=DEBUG) 