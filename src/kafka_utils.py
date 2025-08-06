"""
Kafka Utilities for ML Pipeline System

This module provides Kafka producers, consumers, and utility functions
for integrating Kafka messaging with the ML pipeline system.
"""

import json
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import yaml
import os
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError, KafkaTimeoutError
    from confluent_kafka import Producer as ConfluentProducer, Consumer as ConfluentConsumer
    from confluent_kafka.admin import AdminClient, NewTopic
    from confluent_kafka.cimpl import KafkaException
except ImportError:
    print("Warning: Kafka libraries not installed. Install with: pip install kafka-python confluent-kafka")
    KafkaProducer = None
    KafkaConsumer = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Enum for different message types in the ML pipeline"""
    RAW_DATA = "raw_data"
    PROCESSED_DATA = "processed_data"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    PREDICTION_REQUEST = "prediction_request"
    PREDICTION_RESULT = "prediction_result"
    MONITORING = "monitoring"
    ALERT = "alert"


@dataclass
class KafkaMessage:
    """Standardized message format for ML pipeline"""
    message_id: str
    message_type: MessageType
    timestamp: str
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp,
            'source': self.source,
            'data': self.data,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KafkaMessage':
        """Create from dictionary"""
        return cls(
            message_id=data['message_id'],
            message_type=MessageType(data['message_type']),
            timestamp=data['timestamp'],
            source=data['source'],
            data=data['data'],
            metadata=data.get('metadata')
        )


class KafkaConfig:
    """Kafka configuration manager"""
    
    def __init__(self, config_path: str = "config/kafka_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Kafka config file not found: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading Kafka config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'kafka': {
                'bootstrap_servers': 'localhost:9092',
                'security_protocol': 'PLAINTEXT'
            },
            'topics': {
                'raw_data_topic': 'ml-pipeline-raw-data',
                'processed_data_topic': 'ml-pipeline-processed-data',
                'model_training_topic': 'ml-pipeline-model-training',
                'prediction_requests_topic': 'ml-pipeline-prediction-requests',
                'prediction_results_topic': 'ml-pipeline-prediction-results'
            }
        }
    
    def get_kafka_config(self) -> Dict[str, Any]:
        """Get Kafka connection configuration"""
        return self.config.get('kafka', {})
    
    def get_topic(self, topic_name: str) -> str:
        """Get topic name from configuration"""
        return self.config.get('topics', {}).get(topic_name, f"ml-pipeline-{topic_name}")
    
    def get_producer_config(self) -> Dict[str, Any]:
        """Get producer configuration"""
        kafka_config = self.get_kafka_config()
        producer_config = self.config.get('producer', {})
        return {**kafka_config, **producer_config}
    
    def get_consumer_config(self, group_id: str = None) -> Dict[str, Any]:
        """Get consumer configuration"""
        kafka_config = self.get_kafka_config()
        consumer_config = self.config.get('consumer', {})
        if group_id:
            consumer_config['group_id'] = group_id
        return {**kafka_config, **consumer_config} 


class KafkaProducerManager:
    """Manages Kafka producers for the ML pipeline"""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer = None
        self._lock = threading.Lock()
    
    def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self.producer is None:
            with self._lock:
                if self.producer is None:
                    try:
                        producer_config = self.config.get_producer_config()
                        self.producer = KafkaProducer(
                            bootstrap_servers=producer_config['bootstrap_servers'],
                            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                            key_serializer=lambda k: k.encode('utf-8') if k else None,
                            **{k: v for k, v in producer_config.items() if k != 'bootstrap_servers'}
                        )
                        logger.info("Kafka producer initialized successfully")
                    except Exception as e:
                        logger.error(f"Failed to initialize Kafka producer: {e}")
                        raise
        return self.producer
    
    def send_message(self, topic: str, message: KafkaMessage, key: str = None) -> bool:
        """Send a message to Kafka topic"""
        try:
            producer = self._get_producer()
            future = producer.send(topic, value=message.to_dict(), key=key)
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to {topic} [partition: {record_metadata.partition}, offset: {record_metadata.offset}]")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False
    
    def send_batch(self, topic: str, messages: List[KafkaMessage], key: str = None) -> bool:
        """Send multiple messages to Kafka topic"""
        try:
            producer = self._get_producer()
            futures = []
            
            for message in messages:
                future = producer.send(topic, value=message.to_dict(), key=key)
                futures.append(future)
            
            # Wait for all messages to be sent
            for future in futures:
                record_metadata = future.get(timeout=10)
                logger.info(f"Batch message sent to {topic} [partition: {record_metadata.partition}, offset: {record_metadata.offset}]")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send batch messages to {topic}: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()
            self.producer = None
            logger.info("Kafka producer closed")


class KafkaConsumerManager:
    """Manages Kafka consumers for the ML pipeline"""
    
    def __init__(self, config: KafkaConfig, group_id: str = None):
        self.config = config
        self.group_id = group_id or config.config.get('consumer', {}).get('group_id', 'ml-pipeline-consumer')
        self.consumer = None
        self._running = False
        self._lock = threading.Lock()
    
    def _get_consumer(self, topics: List[str]) -> KafkaConsumer:
        """Get or create Kafka consumer"""
        if self.consumer is None:
            with self._lock:
                if self.consumer is None:
                    try:
                        consumer_config = self.config.get_consumer_config(self.group_id)
                        self.consumer = KafkaConsumer(
                            *topics,
                            bootstrap_servers=consumer_config['bootstrap_servers'],
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                            key_deserializer=lambda k: k.decode('utf-8') if k else None,
                            **{k: v for k, v in consumer_config.items() if k != 'bootstrap_servers'}
                        )
                        logger.info(f"Kafka consumer initialized for topics: {topics}")
                    except Exception as e:
                        logger.error(f"Failed to initialize Kafka consumer: {e}")
                        raise
        return self.consumer
    
    def start_consuming(self, topics: List[str], message_handler: Callable[[KafkaMessage], None]):
        """Start consuming messages from specified topics"""
        try:
            consumer = self._get_consumer(topics)
            self._running = True
            
            logger.info(f"Starting to consume messages from topics: {topics}")
            
            for message in consumer:
                if not self._running:
                    break
                
                try:
                    # Parse the message
                    message_data = message.value
                    kafka_message = KafkaMessage.from_dict(message_data)
                    
                    # Handle the message
                    message_handler(kafka_message)
                    
                    logger.debug(f"Processed message: {kafka_message.message_id} from {message.topic}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue processing other messages
                    
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
        finally:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self._running = False
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            logger.info("Kafka consumer stopped and closed") 


# Utility functions
def create_message(message_type: MessageType, data: Dict[str, Any], source: str = "ml-pipeline") -> KafkaMessage:
    """Create a standardized Kafka message"""
    return KafkaMessage(
        message_id=f"{source}-{int(time.time() * 1000)}",
        message_type=message_type,
        timestamp=datetime.now().isoformat(),
        source=source,
        data=data
    )


def get_kafka_config() -> KafkaConfig:
    """Get Kafka configuration instance"""
    return KafkaConfig()


class KafkaHealthChecker:
    """Health checker for Kafka connections"""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
    
    def check_producer_health(self) -> bool:
        """Check if producer can connect and send messages"""
        try:
            producer_config = self.config.get_producer_config()
            producer = KafkaProducer(
                bootstrap_servers=producer_config['bootstrap_servers'],
                **{k: v for k, v in producer_config.items() if k != 'bootstrap_servers'}
            )
            
            # Try to send a test message
            test_topic = "health-check-topic"
            future = producer.send(test_topic, value=b"health-check")
            record_metadata = future.get(timeout=5)
            
            producer.close()
            return True
            
        except Exception as e:
            logger.error(f"Producer health check failed: {e}")
            return False
    
    def check_consumer_health(self) -> bool:
        """Check if consumer can connect and receive messages"""
        try:
            consumer_config = self.config.get_consumer_config("health-check-group")
            consumer = KafkaConsumer(
                "health-check-topic",
                bootstrap_servers=consumer_config['bootstrap_servers'],
                **{k: v for k, v in consumer_config.items() if k != 'bootstrap_servers'}
            )
            
            # Try to poll for messages
            consumer.poll(timeout_ms=1000)
            consumer.close()
            return True
            
        except Exception as e:
            logger.error(f"Consumer health check failed: {e}")
            return False
    
    def check_overall_health(self) -> Dict[str, bool]:
        """Check overall Kafka health"""
        return {
            'producer': self.check_producer_health(),
            'consumer': self.check_consumer_health()
        }


# Example usage functions
def example_producer_usage():
    """Example of how to use the Kafka producer"""
    config = get_kafka_config()
    producer = KafkaProducerManager(config)
    
    # Create a message
    message = create_message(
        MessageType.RAW_DATA,
        {"data": "example data", "size": 1000},
        "data-ingestion"
    )
    
    # Send message
    topic = config.get_topic("raw_data_topic")
    success = producer.send_message(topic, message)
    
    if success:
        logger.info("Message sent successfully")
    else:
        logger.error("Failed to send message")
    
    producer.close()


def example_consumer_usage():
    """Example of how to use the Kafka consumer"""
    config = get_kafka_config()
    consumer = KafkaConsumerManager(config, "example-consumer-group")
    
    def message_handler(message: KafkaMessage):
        """Handle incoming messages"""
        logger.info(f"Received message: {message.message_id}")
        logger.info(f"Message type: {message.message_type}")
        logger.info(f"Data: {message.data}")
    
    # Start consuming
    topics = [config.get_topic("raw_data_topic")]
    consumer.start_consuming(topics, message_handler)


if __name__ == "__main__":
    # Example usage
    logger.info("Testing Kafka utilities...")
    
    config = get_kafka_config()
    
    # Test health check
    health_checker = KafkaHealthChecker(config)
    health_status = health_checker.check_overall_health()
    logger.info(f"Kafka health status: {health_status}")
    
    # Test producer
    example_producer_usage() 