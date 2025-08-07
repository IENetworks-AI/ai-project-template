#!/usr/bin/env python3
"""
Scheduled Kafka Integration Demo for ML Pipeline

This script demonstrates the Kafka integration with the ML pipeline system,
showing real-time data processing, model training, and prediction serving.
Now includes scheduling functionality to run demos at regular intervals.

Scheduling Options:
- Every N seconds: --interval 5
- Cron expression: --cron "*/5 * * * *"
- One-time run: --once
"""

import os
import sys
import time
import threading
import logging
import argparse
import signal
import schedule
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import random

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
    """Demo class for Kafka integration with enhanced Airflow collaboration showcase"""
    
    def __init__(self, demo_id: Optional[str] = None):
        self.config = get_kafka_config()
        self.producer = KafkaProducerManager(self.config)
        self.consumer = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        self.demo_id = demo_id or f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_count = 0
        
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


class ScheduledKafkaDemo:
    """Scheduler wrapper for Kafka Integration Demo"""
    
    def __init__(self):
        self.is_running = False
        self.demo_count = 0
        self.start_time = datetime.now()
        
    def run_demo_job(self):
        """Job function to be scheduled - runs a single demo instance"""
        if self.is_running:
            logger.warning("⚠️ Previous demo still running, skipping this execution")
            return
            
        self.is_running = True
        self.demo_count += 1
        
        try:
            print(f"\n🚀 Starting Scheduled Demo #{self.demo_count}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Total demos run: {self.demo_count}")
            print(f"⏱️ Uptime: {datetime.now() - self.start_time}")
            print("=" * 60)
            
            # Create demo instance with unique ID
            demo = KafkaIntegrationDemo(f"scheduled_demo_{self.demo_count}")
            
            # Check Kafka health
            if not demo.check_kafka_health():
                logger.error("❌ Kafka is not available. Please start Kafka first")
                return
            
            # Generate enhanced demo data for Airflow integration
            self.generate_airflow_integration_data(demo)
            
            # Run the demo
            demo.run_full_demo()
            
            print(f"\n✅ Scheduled Demo #{self.demo_count} completed successfully!")
            logger.info(f"Demo #{self.demo_count} completed at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"❌ Scheduled demo #{self.demo_count} failed: {e}")
        finally:
            self.is_running = False
    
    def generate_airflow_integration_data(self, demo: KafkaIntegrationDemo):
        """Generate enhanced data that showcases Kafka-Airflow collaboration"""
        try:
            # Generate football match events that will trigger Airflow DAGs
            football_events = self.create_football_events()
            
            # Send events to Kafka topics that Airflow monitors
            for event in football_events:
                message = create_message(
                    message_type=MessageType.TRAINING_DATA,
                    data=event,
                    metadata={
                        "demo_id": demo.demo_id,
                        "event_type": "football_match",
                        "airflow_trigger": True,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Send to live_football_events topic (monitored by Airflow)
                demo.producer.send_message("live_football_events", message)
                logger.info(f"📤 Sent football event to Airflow: {event['match_id']}")
                
            print(f"🏈 Generated {len(football_events)} football events for Airflow processing")
            
        except Exception as e:
            logger.error(f"Failed to generate Airflow integration data: {e}")
    
    def create_football_events(self) -> list:
        """Create realistic football match events for Airflow DAG processing"""
        teams = [
            ("Manchester United", "Liverpool"),
            ("Barcelona", "Real Madrid"),
            ("Bayern Munich", "Borussia Dortmund"),
            ("PSG", "Marseille"),
            ("Juventus", "AC Milan")
        ]
        
        events = []
        for i, (home_team, away_team) in enumerate(teams):
            match_id = f"match_{self.demo_count}_{i+1}"
            
            # Generate realistic match statistics
            event = {
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
                "league": "Demo League",
                "season": "2024",
                "match_date": datetime.now().isoformat(),
                "home_score": random.randint(0, 4),
                "away_score": random.randint(0, 4),
                "home_shots": random.randint(5, 20),
                "away_shots": random.randint(5, 20),
                "home_possession": round(random.uniform(30, 70), 1),
                "away_possession": None,  # Will be calculated as 100 - home_possession
                "home_corners": random.randint(0, 12),
                "away_corners": random.randint(0, 12),
                "home_fouls": random.randint(5, 25),
                "away_fouls": random.randint(5, 25),
                "home_yellow_cards": random.randint(0, 5),
                "away_yellow_cards": random.randint(0, 5),
                "home_red_cards": random.randint(0, 1),
                "away_red_cards": random.randint(0, 1),
                "referee": f"Referee_{random.randint(1, 10)}",
                "stadium": f"{home_team} Stadium",
                "attendance": random.randint(20000, 80000),
                "weather": random.choice(["Clear", "Rainy", "Cloudy", "Sunny"]),
                "temperature": random.randint(10, 30)
            }
            
            # Calculate away possession
            event["away_possession"] = round(100 - event["home_possession"], 1)
            
            events.append(event)
        
        return events


def run_scheduled_demo(interval_seconds: int = 5):
    """Run the demo on a schedule every N seconds"""
    scheduler = ScheduledKafkaDemo()
    
    # Schedule the job
    schedule.every(interval_seconds).seconds.do(scheduler.run_demo_job)
    
    print(f"🕐 Kafka Demo Scheduler Started")
    print(f"⚡ Running every {interval_seconds} seconds")
    print(f"🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down scheduler...")
        print(f"📊 Total demos executed: {scheduler.demo_count}")
        print(f"⏱️ Total uptime: {datetime.now() - scheduler.start_time}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_cron_demo(cron_expression: str):
    """Run the demo based on a cron-like schedule"""
    print(f"🕐 Cron-style scheduling not implemented in basic schedule library")
    print(f"📝 Cron expression: {cron_expression}")
    print(f"💡 Consider using APScheduler for cron expressions")
    print(f"🔄 Falling back to 5-second interval...")
    run_scheduled_demo(5)


def run_once():
    """Run the demo once"""
    print("🎯 Running Kafka ML Pipeline Integration Demo (One-time)")
    print("=" * 50)
    print()
    
    # Create demo instance
    demo = KafkaIntegrationDemo("onetime_demo")
    
    # Check Kafka health
    if not demo.check_kafka_health():
        print("❌ Kafka is not available. Please start Kafka first:")
        print("   ./scripts/setup_kafka.sh")
        return
    
    try:
        # Generate enhanced demo data for Airflow integration
        scheduler = ScheduledKafkaDemo()
        scheduler.generate_airflow_integration_data(demo)
        
        # Run the demo
        demo.run_full_demo()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📚 Next Steps:")
        print("  1. Check Kafka UI: http://localhost:8080")
        print("  2. Check Airflow UI: http://localhost:8081")
        print("  3. Monitor Airflow DAGs processing the football events")
        print("  4. Start the ML pipeline: python pipelines/kafka_ml_pipeline.py")
        print("  5. Start the API service: python api/kafka_api.py")
        print("  6. Test with real data")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        demo.cleanup()


def main():
    """Main function with command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Scheduled Kafka Integration Demo for ML Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_kafka_integration.py --once                    # Run once
  python demo_kafka_integration.py --interval 10             # Every 10 seconds
  python demo_kafka_integration.py --cron "*/5 * * * *"       # Every 5 minutes (cron)
  python demo_kafka_integration.py                           # Default: every 5 seconds
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--once", 
        action="store_true", 
        help="Run the demo once and exit"
    )
    group.add_argument(
        "--interval", 
        type=int, 
        default=5, 
        help="Run the demo every N seconds (default: 5)"
    )
    group.add_argument(
        "--cron", 
        type=str, 
        help="Run the demo based on cron expression (e.g., '*/5 * * * *')"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('kafka_demo_scheduler.log')
        ]
    )
    
    if args.once:
        run_once()
    elif args.cron:
        run_cron_demo(args.cron)
    else:
        run_scheduled_demo(args.interval)


if __name__ == "__main__":
    main() 