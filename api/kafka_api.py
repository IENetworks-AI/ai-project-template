"""
Kafka-Integrated API Service

This API service integrates with Kafka for real-time ML pipeline operations,
providing REST endpoints for data ingestion, model training, and predictions.
"""

import os
import sys
import logging
import json
import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kafka_utils import (
    KafkaConfig, KafkaProducerManager, KafkaConsumerManager,
    KafkaMessage, MessageType, create_message, get_kafka_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
kafka_config = None
producer = None
prediction_results = {}
prediction_results_lock = threading.Lock()


class KafkaAPIService:
    """Kafka-integrated API service for ML pipeline operations"""
    
    def __init__(self):
        self.config = get_kafka_config()
        self.producer = KafkaProducerManager(self.config)
        self.consumer = None
        self.prediction_results = {}
        self.prediction_results_lock = threading.Lock()
        
        # Start prediction results consumer
        self._start_prediction_results_consumer()
    
    def _start_prediction_results_consumer(self):
        """Start consumer for prediction results"""
        def handle_prediction_result(message: KafkaMessage):
            """Handle incoming prediction results"""
            try:
                prediction_data = message.data
                request_id = message.message_id
                
                with self.prediction_results_lock:
                    self.prediction_results[request_id] = {
                        'prediction': prediction_data.get('prediction'),
                        'model_used': prediction_data.get('model_used'),
                        'timestamp': prediction_data.get('timestamp'),
                        'status': 'completed'
                    }
                
                logger.info(f"📊 Prediction result received: {request_id}")
                
            except Exception as e:
                logger.error(f"❌ Error handling prediction result: {e}")
        
        # Start consumer in background thread
        consumer = KafkaConsumerManager(self.config, "api-prediction-results-group")
        topics = [self.config.get_topic("prediction_results_topic")]
        
        consumer_thread = threading.Thread(
            target=consumer.start_consuming,
            args=(topics, handle_prediction_result),
            name="prediction-results-consumer"
        )
        consumer_thread.daemon = True
        consumer_thread.start()
        
        self.consumer = consumer
    
    def ingest_data(self, file_path: str) -> Dict[str, Any]:
        """Ingest data into the Kafka pipeline"""
        try:
            # Create ingestion message
            data = {
                'file_path': file_path,
                'ingestion_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
            message = create_message(
                MessageType.RAW_DATA,
                data,
                "api-data-ingestion"
            )
            
            # Send to raw data topic
            topic = self.config.get_topic("raw_data_topic")
            success = self.producer.send_message(topic, message)
            
            if success:
                logger.info(f"📥 Data ingested via API: {message.message_id}")
                return {
                    'status': 'success',
                    'message_id': message.message_id,
                    'message': 'Data ingested successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to ingest data'
                }
                
        except Exception as e:
            logger.error(f"❌ Data ingestion error: {e}")
            return {
                'status': 'error',
                'message': f'Data ingestion failed: {str(e)}'
            }
    
    def request_prediction(self, features: List[float]) -> Dict[str, Any]:
        """Request a prediction from the Kafka pipeline"""
        try:
            # Create prediction request
            request_data = {
                'features': features,
                'request_time': datetime.now().isoformat()
            }
            
            message = create_message(
                MessageType.PREDICTION_REQUEST,
                request_data,
                "api-prediction-client"
            )
            
            # Send to prediction requests topic
            topic = self.config.get_topic("prediction_requests_topic")
            success = self.producer.send_message(topic, message)
            
            if success:
                logger.info(f"📤 Prediction request sent via API: {message.message_id}")
                return {
                    'status': 'success',
                    'message_id': message.message_id,
                    'message': 'Prediction request sent successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send prediction request'
                }
                
        except Exception as e:
            logger.error(f"❌ Prediction request error: {e}")
            return {
                'status': 'error',
                'message': f'Prediction request failed: {str(e)}'
            }
    
    def get_prediction_result(self, message_id: str) -> Dict[str, Any]:
        """Get prediction result by message ID"""
        with self.prediction_results_lock:
            result = self.prediction_results.get(message_id)
            
            if result:
                return {
                    'status': 'success',
                    'result': result
                }
            else:
                return {
                    'status': 'pending',
                    'message': 'Prediction result not yet available'
                }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        try:
            # Check Kafka health
            from kafka_utils import KafkaHealthChecker
            health_checker = KafkaHealthChecker(self.config)
            health_status = health_checker.check_overall_health()
            
            return {
                'status': 'success',
                'kafka_health': health_status,
                'timestamp': datetime.now().isoformat(),
                'active_predictions': len(self.prediction_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Pipeline status error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get pipeline status: {str(e)}'
            }
    
    def close(self):
        """Close the API service"""
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.stop_consuming()


# Initialize API service
api_service = KafkaAPIService()


# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Kafka ML Pipeline API'
    })


@app.route('/api/ingest', methods=['POST'])
def ingest_data():
    """Ingest data into the pipeline"""
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({
                'status': 'error',
                'message': 'file_path is required'
            }), 400
        
        file_path = data['file_path']
        
        # Validate file exists
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'message': f'File not found: {file_path}'
            }), 404
        
        # Ingest data
        result = api_service.ingest_data(file_path)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ API ingest error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/predict', methods=['POST'])
def request_prediction():
    """Request a prediction from the pipeline"""
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'features array is required'
            }), 400
        
        features = data['features']
        
        # Validate features
        if not isinstance(features, list):
            return jsonify({
                'status': 'error',
                'message': 'features must be an array'
            }), 400
        
        if not all(isinstance(f, (int, float)) for f in features):
            return jsonify({
                'status': 'error',
                'message': 'features must be numeric values'
            }), 400
        
        # Request prediction
        result = api_service.request_prediction(features)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ API prediction error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/prediction/<message_id>', methods=['GET'])
def get_prediction_result(message_id):
    """Get prediction result by message ID"""
    try:
        result = api_service.get_prediction_result(message_id)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        elif result['status'] == 'pending':
            return jsonify(result), 202
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"❌ API get prediction error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/status', methods=['GET'])
def get_pipeline_status():
    """Get pipeline status"""
    try:
        status = api_service.get_pipeline_status()
        
        if status['status'] == 'success':
            return jsonify(status), 200
        else:
            return jsonify(status), 500
            
    except Exception as e:
        logger.error(f"❌ API status error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/topics', methods=['GET'])
def get_kafka_topics():
    """Get Kafka topics information"""
    try:
        topics_config = api_service.config.config.get('topics', {})
        
        return jsonify({
            'status': 'success',
            'topics': topics_config
        }), 200
        
    except Exception as e:
        logger.error(f"❌ API topics error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/health/kafka', methods=['GET'])
def kafka_health_check():
    """Check Kafka health"""
    try:
        from kafka_utils import KafkaHealthChecker
        health_checker = KafkaHealthChecker(api_service.config)
        health_status = health_checker.check_overall_health()
        
        return jsonify({
            'status': 'success',
            'kafka_health': health_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Kafka health check error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Kafka health check failed: {str(e)}'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


def main():
    """Main function to run the Kafka API service"""
    logger.info("🚀 Starting Kafka ML Pipeline API Service")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Kafka API Service...")
        api_service.close()
        logger.info("✅ Kafka API Service stopped")


if __name__ == "__main__":
    main() 