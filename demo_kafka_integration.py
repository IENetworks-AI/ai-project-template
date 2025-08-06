#!/usr/bin/env python3
"""
Kafka Integration Demo for ML Pipeline

This script demonstrates the Kafka integration with the ML pipeline system,
showing real-time data processing, model training, and prediction serving.
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from kafka_utils import (
    KafkaConfig, KafkaProducerManager, KafkaConsumerManager,
    KafkaMessage, MessageType, create_message, get_kafka_config
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KafkaIntegrationDemo:
    """Demo class for Kafka integration"""
    
    def __init__(self):
        self.config = get_kafka_config()
        self.producer = KafkaProducerManager(self.config)
        self.consumer = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        
    def setup_consumer(self):
        """Setup consumer to listen for messages"""
        def message_handler(message: KafkaMessage):
            """Handle incoming messages"""
            with self.message_lock:
                self.received_messages.append(message)
                logger.info(f"📨 Received: {message.message_type.value} - {message.message_id}")
        
        # Start consumer in background thread
        self.consumer = KafkaConsumerManager(self.config, "demo-consumer-group")
        topics = [
            self.config.get_topic("raw_data_topic"),
            self.config.get_topic("processed_data_topic"),
            self.config.get_topic("model_training_topic"),
            self.config.get_topic("prediction_requests_topic"),
            self.config.get_topic("prediction_results_topic")
        ]
        
        consumer_thread = threading.Thread(
            target=self.consumer.start_consuming,
            args=(topics, message_handler),
            name="demo-consumer"
        )
        consumer_thread.daemon = True
        consumer_thread.start()
        
        logger.info("✅ Consumer started")
    
    def demo_data_ingestion(self):
        """Demo data ingestion"""
        logger.info("📥 Demo: Data Ingestion")
        
        # Create sample data
        sample_data = {
            'file_path': 'data/Sales Dataset.csv',
            'ingestion_time': datetime.now().isoformat(),
            'file_size': 1024,
            'source': 'demo'
        }
        
        message = create_message(
            MessageType.RAW_DATA,
            sample_data,
            "demo-data-ingestion"
        )
        
        topic = self.config.get_topic("raw_data_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Data ingested: {message.message_id}")
        else:
            logger.error("❌ Failed to ingest data")
        
        return success
    
    def demo_data_processing(self):
        """Demo data processing"""
        logger.info("🔄 Demo: Data Processing")
        
        # Simulate processed data
        processed_data = {
            'data_shape': (1000, 10),
            'columns': ['feature1', 'feature2', 'feature3', 'target'],
            'processing_time': 2.5,
            'quality_score': 0.95
        }
        
        message = create_message(
            MessageType.PROCESSED_DATA,
            processed_data,
            "demo-data-processing"
        )
        
        topic = self.config.get_topic("processed_data_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Data processed: {message.message_id}")
        else:
            logger.error("❌ Failed to process data")
        
        return success
    
    def demo_model_training(self):
        """Demo model training"""
        logger.info("🤖 Demo: Model Training")
        
        # Simulate training results
        training_results = {
            'model_type': 'RandomForestRegressor',
            'metrics': {
                'mse': 0.0456,
                'r2_score': 0.8923,
                'mae': 0.1234
            },
            'training_time': 15.7,
            'model_path': 'models/demo_model.joblib'
        }
        
        message = create_message(
            MessageType.MODEL_TRAINING,
            training_results,
            "demo-model-training"
        )
        
        topic = self.config.get_topic("model_training_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Model trained: {message.message_id}")
        else:
            logger.error("❌ Failed to train model")
        
        return success
    
    def demo_prediction_request(self):
        """Demo prediction request"""
        logger.info("🔮 Demo: Prediction Request")
        
        # Create prediction request
        request_data = {
            'features': [100, 50, 25, 10, 5],
            'request_time': datetime.now().isoformat(),
            'client_id': 'demo-client'
        }
        
        message = create_message(
            MessageType.PREDICTION_REQUEST,
            request_data,
            "demo-prediction-client"
        )
        
        topic = self.config.get_topic("prediction_requests_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Prediction requested: {message.message_id}")
        else:
            logger.error("❌ Failed to request prediction")
        
        return success
    
    def demo_prediction_result(self):
        """Demo prediction result"""
        logger.info("🎯 Demo: Prediction Result")
        
        # Simulate prediction result
        prediction_result = {
            'prediction': 42.5,
            'confidence': 0.89,
            'model_used': 'demo_model.joblib',
            'processing_time': 0.023
        }
        
        message = create_message(
            MessageType.PREDICTION_RESULT,
            prediction_result,
            "demo-prediction-serving"
        )
        
        topic = self.config.get_topic("prediction_results_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Prediction served: {message.message_id}")
        else:
            logger.error("❌ Failed to serve prediction")
        
        return success
    
    def demo_monitoring(self):
        """Demo monitoring messages"""
        logger.info("📊 Demo: Monitoring")
        
        # Create monitoring message
        monitoring_data = {
            'pipeline_status': 'healthy',
            'active_consumers': 5,
            'messages_processed': 150,
            'error_rate': 0.01
        }
        
        message = create_message(
            MessageType.MONITORING,
            monitoring_data,
            "demo-monitoring"
        )
        
        topic = self.config.get_topic("pipeline_monitoring_topic")
        success = self.producer.send_message(topic, message)
        
        if success:
            logger.info(f"✅ Monitoring data sent: {message.message_id}")
        else:
            logger.error("❌ Failed to send monitoring data")
        
        return success
    
    def run_full_demo(self):
        """Run the complete demo"""
        logger.info("🎯 Starting Kafka Integration Demo")
        logger.info("=" * 50)
        
        # Setup consumer
        self.setup_consumer()
        time.sleep(2)  # Wait for consumer to start
        
        # Run demo stages
        demos = [
            ("Data Ingestion", self.demo_data_ingestion),
            ("Data Processing", self.demo_data_processing),
            ("Model Training", self.demo_model_training),
            ("Prediction Request", self.demo_prediction_request),
            ("Prediction Result", self.demo_prediction_result),
            ("Monitoring", self.demo_monitoring)
        ]
        
        for demo_name, demo_func in demos:
            logger.info(f"\n🚀 Running {demo_name} Demo...")
            success = demo_func()
            
            if success:
                logger.info(f"✅ {demo_name} demo completed successfully")
            else:
                logger.error(f"❌ {demo_name} demo failed")
            
            time.sleep(1)  # Brief pause between demos
        
        # Wait for messages to be processed
        logger.info("\n⏳ Waiting for messages to be processed...")
        time.sleep(5)
        
        # Display results
        self.display_results()
        
        # Cleanup
        self.cleanup()
    
    def display_results(self):
        """Display demo results"""
        logger.info("\n📊 Demo Results")
        logger.info("=" * 30)
        
        with self.message_lock:
            message_count = len(self.received_messages)
            logger.info(f"📨 Total messages received: {message_count}")
            
            if message_count > 0:
                logger.info("\n📋 Message Summary:")
                for i, message in enumerate(self.received_messages, 1):
                    logger.info(f"  {i}. {message.message_type.value} - {message.message_id}")
                    logger.info(f"     Source: {message.source}")
                    logger.info(f"     Data keys: {list(message.data.keys())}")
            else:
                logger.warning("⚠️ No messages received. Check Kafka connectivity.")
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("\n🧹 Cleaning up...")
        
        if self.producer:
            self.producer.close()
        
        if self.consumer:
            self.consumer.stop_consuming()
        
        logger.info("✅ Cleanup completed")
    
    def check_kafka_health(self):
        """Check Kafka health before running demo"""
        try:
            from kafka_utils import KafkaHealthChecker
            health_checker = KafkaHealthChecker(self.config)
            health_status = health_checker.check_overall_health()
            
            logger.info(f"🔍 Kafka Health Check: {health_status}")
            
            if health_status['producer'] and health_status['consumer']:
                logger.info("✅ Kafka is healthy and ready for demo")
                return True
            else:
                logger.warning("⚠️ Kafka health check failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Kafka health check error: {e}")
            return False


def main():
    """Main function to run the demo"""
    print("🎯 Kafka ML Pipeline Integration Demo")
    print("=" * 50)
    print()
    
    # Create demo instance
    demo = KafkaIntegrationDemo()
    
    # Check Kafka health
    if not demo.check_kafka_health():
        print("❌ Kafka is not available. Please start Kafka first:")
        print("   ./scripts/setup_kafka.sh")
        return
    
    try:
        # Run the demo
        demo.run_full_demo()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Check Kafka UI: http://localhost:8080")
        print("  2. Start the ML pipeline: python pipelines/kafka_ml_pipeline.py")
        print("  3. Start the API service: python api/kafka_api.py")
        print("  4. Test with real data")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main() 