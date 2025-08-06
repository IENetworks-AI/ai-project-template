"""
Kafka-Integrated ML Pipeline

This pipeline integrates Kafka messaging for real-time data processing,
model training, and prediction serving in the ML pipeline system.
"""

import os
import sys
import logging
import json
import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kafka_utils import (
    KafkaConfig, KafkaProducerManager, KafkaConsumerManager,
    KafkaMessage, MessageType, create_message, get_kafka_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaMLPipeline:
    """Kafka-integrated ML Pipeline for real-time processing"""
    
    def __init__(self):
        self.config = get_kafka_config()
        self.producer = KafkaProducerManager(self.config)
        self.consumer = None
        self.model = None
        self.is_running = False
        
        # Pipeline stages (defined as methods)
        pass
    
    def start_pipeline(self):
        """Start the Kafka ML pipeline"""
        logger.info("🚀 Starting Kafka ML Pipeline...")
        self.is_running = True
        
        # Start consumer threads for each stage
        threads = []
        
        # Data processing consumer
        data_processing_thread = threading.Thread(
            target=self._start_data_processing_consumer,
            name="data-processing-consumer"
        )
        data_processing_thread.daemon = True
        data_processing_thread.start()
        threads.append(data_processing_thread)
        
        # Model training consumer
        model_training_thread = threading.Thread(
            target=self._start_model_training_consumer,
            name="model-training-consumer"
        )
        model_training_thread.daemon = True
        model_training_thread.start()
        threads.append(model_training_thread)
        
        # Prediction serving consumer
        prediction_thread = threading.Thread(
            target=self._start_prediction_consumer,
            name="prediction-consumer"
        )
        prediction_thread.daemon = True
        prediction_thread.start()
        threads.append(prediction_thread)
        
        # Monitoring consumer
        monitoring_thread = threading.Thread(
            target=self._start_monitoring_consumer,
            name="monitoring-consumer"
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()
        threads.append(monitoring_thread)
        
        logger.info(f"✅ Started {len(threads)} consumer threads")
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping Kafka ML Pipeline...")
            self.stop_pipeline()
    
    def stop_pipeline(self):
        """Stop the Kafka ML pipeline"""
        self.is_running = False
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.stop_consuming()
        logger.info("✅ Kafka ML Pipeline stopped")
    
    def _data_ingestion_stage(self, data: Dict[str, Any]) -> bool:
        """Data ingestion stage - sends raw data to Kafka"""
        try:
            # Create message for raw data
            message = create_message(
                MessageType.RAW_DATA,
                data,
                "data-ingestion"
            )
            
            # Send to raw data topic
            topic = self.config.get_topic("raw_data_topic")
            success = self.producer.send_message(topic, message)
            
            if success:
                logger.info(f"📥 Raw data ingested: {message.message_id}")
                return True
            else:
                logger.error("❌ Failed to ingest raw data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data ingestion error: {e}")
            return False
    
    def _start_data_processing_consumer(self):
        """Start consumer for data processing stage"""
        consumer = KafkaConsumerManager(self.config, "data-processing-group")
        
        def process_raw_data(message: KafkaMessage):
            """Process raw data and send to processed data topic"""
            try:
                logger.info(f"🔄 Processing raw data: {message.message_id}")
                
                # Extract data
                raw_data = message.data
                
                # Process the data (example: load CSV and preprocess)
                if 'file_path' in raw_data:
                    df = pd.read_csv(raw_data['file_path'])
                    
                    # Basic preprocessing
                    df = df.dropna()
                    
                    # Create processed data message
                    processed_data = {
                        'data': df.to_dict('records'),
                        'shape': df.shape,
                        'columns': list(df.columns),
                        'original_file': raw_data['file_path']
                    }
                    
                    processed_message = create_message(
                        MessageType.PROCESSED_DATA,
                        processed_data,
                        "data-processing"
                    )
                    
                    # Send to processed data topic
                    topic = self.config.get_topic("processed_data_topic")
                    success = self.producer.send_message(topic, processed_message)
                    
                    if success:
                        logger.info(f"✅ Data processed: {processed_message.message_id}")
                    else:
                        logger.error("❌ Failed to send processed data")
                        
            except Exception as e:
                logger.error(f"❌ Data processing error: {e}")
        
        # Start consuming raw data
        topics = [self.config.get_topic("raw_data_topic")]
        consumer.start_consuming(topics, process_raw_data)
    
    def _start_model_training_consumer(self):
        """Start consumer for model training stage"""
        consumer = KafkaConsumerManager(self.config, "model-training-group")
        
        def train_model(message: KafkaMessage):
            """Train model on processed data"""
            try:
                logger.info(f"🤖 Training model with data: {message.message_id}")
                
                # Extract processed data
                processed_data = message.data
                
                # Convert back to DataFrame
                df = pd.DataFrame(processed_data['data'])
                
                # Prepare features and target (assuming last column is target)
                X = df.iloc[:, :-1]
                y = df.iloc[:, -1]
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Save model
                model_path = f"models/model_{int(time.time())}.joblib"
                os.makedirs("models", exist_ok=True)
                joblib.dump(model, model_path)
                
                # Create training results message
                training_results = {
                    'model_path': model_path,
                    'metrics': {
                        'mse': mse,
                        'r2_score': r2,
                        'test_size': len(X_test),
                        'train_size': len(X_train)
                    },
                    'model_type': 'RandomForestRegressor',
                    'features': list(X.columns),
                    'target': y.name if hasattr(y, 'name') else 'target'
                }
                
                training_message = create_message(
                    MessageType.MODEL_TRAINING,
                    training_results,
                    "model-training"
                )
                
                # Send to model training topic
                topic = self.config.get_topic("model_training_topic")
                success = self.producer.send_message(topic, training_message)
                
                if success:
                    logger.info(f"✅ Model trained: {training_message.message_id}")
                    logger.info(f"📊 Model metrics - MSE: {mse:.4f}, R²: {r2:.4f}")
                else:
                    logger.error("❌ Failed to send training results")
                    
            except Exception as e:
                logger.error(f"❌ Model training error: {e}")
        
        # Start consuming processed data
        topics = [self.config.get_topic("processed_data_topic")]
        consumer.start_consuming(topics, train_model)
    
    def _start_prediction_consumer(self):
        """Start consumer for prediction serving stage"""
        consumer = KafkaConsumerManager(self.config, "prediction-serving-group")
        
        def serve_predictions(message: KafkaMessage):
            """Serve predictions for incoming requests"""
            try:
                logger.info(f"🔮 Serving prediction for: {message.message_id}")
                
                # Extract prediction request
                request_data = message.data
                
                # Load the latest model
                model_files = [f for f in os.listdir("models") if f.endswith(".joblib")]
                if not model_files:
                    logger.error("❌ No trained models found")
                    return
                
                latest_model = sorted(model_files)[-1]
                model_path = os.path.join("models", latest_model)
                model = joblib.load(model_path)
                
                # Make prediction
                features = request_data.get('features', [])
                if not features:
                    logger.error("❌ No features provided for prediction")
                    return
                
                # Convert to numpy array
                X = np.array(features).reshape(1, -1)
                prediction = model.predict(X)[0]
                
                # Create prediction result message
                prediction_result = {
                    'prediction': float(prediction),
                    'features': features,
                    'model_used': latest_model,
                    'timestamp': datetime.now().isoformat()
                }
                
                result_message = create_message(
                    MessageType.PREDICTION_RESULT,
                    prediction_result,
                    "prediction-serving"
                )
                
                # Send to prediction results topic
                topic = self.config.get_topic("prediction_results_topic")
                success = self.producer.send_message(topic, result_message)
                
                if success:
                    logger.info(f"✅ Prediction served: {result_message.message_id}")
                    logger.info(f"🔮 Prediction: {prediction}")
                else:
                    logger.error("❌ Failed to send prediction result")
                    
            except Exception as e:
                logger.error(f"❌ Prediction serving error: {e}")
        
        # Start consuming prediction requests
        topics = [self.config.get_topic("prediction_requests_topic")]
        consumer.start_consuming(topics, serve_predictions)
    
    def _start_monitoring_consumer(self):
        """Start consumer for monitoring stage"""
        consumer = KafkaConsumerManager(self.config, "monitoring-group")
        
        def monitor_pipeline(message: KafkaMessage):
            """Monitor pipeline activities"""
            try:
                logger.info(f"📊 Monitoring: {message.message_type.value} - {message.message_id}")
                
                # Create monitoring message
                monitoring_data = {
                    'message_type': message.message_type.value,
                    'message_id': message.message_id,
                    'timestamp': message.timestamp,
                    'source': message.source,
                    'status': 'processed'
                }
                
                monitoring_message = create_message(
                    MessageType.MONITORING,
                    monitoring_data,
                    "pipeline-monitoring"
                )
                
                # Send to monitoring topic
                topic = self.config.get_topic("pipeline_monitoring_topic")
                self.producer.send_message(topic, monitoring_message)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
        
        # Start consuming all topics for monitoring
        all_topics = [
            self.config.get_topic("raw_data_topic"),
            self.config.get_topic("processed_data_topic"),
            self.config.get_topic("model_training_topic"),
            self.config.get_topic("prediction_requests_topic"),
            self.config.get_topic("prediction_results_topic")
        ]
        consumer.start_consuming(all_topics, monitor_pipeline)
    
    def ingest_data(self, file_path: str) -> bool:
        """Ingest data into the pipeline"""
        try:
            data = {
                'file_path': file_path,
                'ingestion_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
            return self._data_ingestion_stage(data)
            
        except Exception as e:
            logger.error(f"❌ Data ingestion error: {e}")
            return False
    
    def request_prediction(self, features: List[float]) -> bool:
        """Request a prediction from the pipeline"""
        try:
            request_data = {
                'features': features,
                'request_time': datetime.now().isoformat()
            }
            
            message = create_message(
                MessageType.PREDICTION_REQUEST,
                request_data,
                "prediction-client"
            )
            
            topic = self.config.get_topic("prediction_requests_topic")
            success = self.producer.send_message(topic, message)
            
            if success:
                logger.info(f"📤 Prediction request sent: {message.message_id}")
                return True
            else:
                logger.error("❌ Failed to send prediction request")
                return False
                
        except Exception as e:
            logger.error(f"❌ Prediction request error: {e}")
            return False


def main():
    """Main function to run the Kafka ML Pipeline"""
    logger.info("🎯 Starting Kafka ML Pipeline System")
    
    # Create pipeline
    pipeline = KafkaMLPipeline()
    
    # Start the pipeline
    pipeline.start_pipeline()


if __name__ == "__main__":
    main() 