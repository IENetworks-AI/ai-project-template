"""
API Routes for Retail Sales Insight
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request
from src.utils.logging import get_logger
from pipelines.data_pipeline import get_sales_insights, run_data_pipeline

logger = get_logger('api_routes')

# Create blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'Retail Sales Insight API',
        'version': '1.0.0',
        'endpoints': [
            '/health',
            '/top_categories',
            '/process_data'
        ]
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Retail Sales Insight API is running'
    })

@api_bp.route('/top_categories', methods=['GET'])
def get_top_categories():
    """Get top performing product categories"""
    try:
        logger.info("API request: Get top categories")
        
        # Get insights from processed data
        insights = get_sales_insights()
        
        if insights is None:
            return jsonify({
                'error': 'No sales insights available. Please run data processing first.'
            }), 404
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Error in top_categories endpoint: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@api_bp.route('/process_data', methods=['POST'])
def process_data():
    """Trigger data processing pipeline"""
    try:
        logger.info("API request: Process data")
        
        # Run the data pipeline
        success = run_data_pipeline()
        
        if success:
            # Get the latest insights
            insights = get_sales_insights()
            
            return jsonify({
                'message': 'Data processing completed successfully',
                'insights': insights
            })
        else:
            return jsonify({
                'error': 'Data processing failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in process_data endpoint: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500 