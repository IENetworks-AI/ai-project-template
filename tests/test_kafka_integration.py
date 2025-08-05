"""
Test Kafka Integration for ML Pipeline

This module tests the Kafka integration components including
producers, consumers, and message handling.
"""

import pytest
import time
import threading
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kafka_utils import (
    KafkaConfig, KafkaProducerManager, KafkaConsumerManager,
    KafkaMessage, MessageType, create_message, get_kafka_config
)


class TestKafkaConfig:
    """Test Kafka configuration management"""
    
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        config = get_kafka_config()
        assert config is not None
        assert hasattr(config, 'config')
        assert 'kafka' in config.config
        assert 'topics' in config.config
    
    def test_get_topic(self):
        """Test topic name retrieval"""
        config = get_kafka_config()
        topic = config.get_topic("raw_data_topic")
        assert topic == "ml-pipeline-raw-data"
    
    def test_producer_config(self):
        """Test producer configuration"""
        config = get_kafka_config()
        producer_config = config.get_producer_config()
        assert 'bootstrap_servers' in producer_config
        assert 'acks' in producer_config
    
    def test_consumer_config(self):
        """Test consumer configuration"""
        config = get_kafka_config()
        consumer_config = config.get_consumer_config("test-group")
        assert 'bootstrap_servers' in consumer_config
        assert 'group_id' in consumer_config
        assert consumer_config['group_id'] == "test-group"


class TestKafkaMessage:
    """Test Kafka message creation and serialization"""
    
    def test_message_creation(self):
        """Test creating a Kafka message"""
        message = create_message(
            MessageType.RAW_DATA,
            {"test": "data"},
            "test-source"
        )
        
        assert message.message_type == MessageType.RAW_DATA
        assert message.source == "test-source"
        assert message.data == {"test": "data"}
        assert message.message_id is not None
        assert message.timestamp is not None
    
    def test_message_serialization(self):
        """Test message serialization to dictionary"""
        message = create_message(
            MessageType.PROCESSED_DATA,
            {"processed": "data"},
            "test-source"
        )
        
        message_dict = message.to_dict()
        assert 'message_id' in message_dict
        assert 'message_type' in message_dict
        assert 'timestamp' in message_dict
        assert 'source' in message_dict
        assert 'data' in message_dict
        assert message_dict['message_type'] == "processed_data"
    
    def test_message_deserialization(self):
        """Test message deserialization from dictionary"""
        original_message = create_message(
            MessageType.MODEL_TRAINING,
            {"model": "data"},
            "test-source"
        )
        
        message_dict = original_message.to_dict()
        reconstructed_message = KafkaMessage.from_dict(message_dict)
        
        assert reconstructed_message.message_type == original_message.message_type
        assert reconstructed_message.source == original_message.source
        assert reconstructed_message.data == original_message.data


class TestKafkaProducerManager:
    """Test Kafka producer functionality"""
    
    @patch('kafka_utils.KafkaProducer')
    def test_producer_initialization(self, mock_kafka_producer):
        """Test producer initialization"""
        config = get_kafka_config()
        producer = KafkaProducerManager(config)
        
        # Mock the producer to avoid actual Kafka connection
        mock_producer_instance = Mock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        # Test that producer can be created
        assert producer is not None
        assert hasattr(producer, 'config')
    
    @patch('kafka_utils.KafkaProducer')
    def test_send_message(self, mock_kafka_producer):
        """Test sending a message"""
        config = get_kafka_config()
        producer = KafkaProducerManager(config)
        
        # Mock the producer
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_future.get.return_value = Mock(partition=0, offset=1)
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        # Create test message
        message = create_message(
            MessageType.RAW_DATA,
            {"test": "data"},
            "test-source"
        )
        
        # Test sending message
        success = producer.send_message("test-topic", message)
        assert success is True
    
    def test_producer_close(self):
        """Test producer cleanup"""
        config = get_kafka_config()
        producer = KafkaProducerManager(config)
        
        # Test that close method exists
        assert hasattr(producer, 'close')
        assert callable(producer.close)


class TestKafkaConsumerManager:
    """Test Kafka consumer functionality"""
    
    def test_consumer_initialization(self):
        """Test consumer initialization"""
        config = get_kafka_config()
        consumer = KafkaConsumerManager(config, "test-group")
        
        assert consumer is not None
        assert consumer.group_id == "test-group"
        assert hasattr(consumer, 'config')
    
    def test_consumer_stop(self):
        """Test consumer stop functionality"""
        config = get_kafka_config()
        consumer = KafkaConsumerManager(config, "test-group")
        
        # Test that stop method exists
        assert hasattr(consumer, 'stop_consuming')
        assert callable(consumer.stop_consuming)


class TestKafkaIntegration:
    """Integration tests for Kafka components"""
    
    def test_message_flow(self):
        """Test complete message flow"""
        # Create configuration
        config = get_kafka_config()
        
        # Create message
        message = create_message(
            MessageType.RAW_DATA,
            {"integration": "test"},
            "test-source"
        )
        
        # Verify message structure
        assert message.message_type == MessageType.RAW_DATA
        assert message.data == {"integration": "test"}
        assert message.source == "test-source"
        
        # Test serialization
        message_dict = message.to_dict()
        assert message_dict['message_type'] == "raw_data"
        assert message_dict['data'] == {"integration": "test"}
        
        # Test deserialization
        reconstructed = KafkaMessage.from_dict(message_dict)
        assert reconstructed.message_type == message.message_type
        assert reconstructed.data == message.data
    
    def test_config_integration(self):
        """Test configuration integration"""
        config = get_kafka_config()
        
        # Test topic configuration
        topics = [
            "raw_data_topic",
            "processed_data_topic",
            "model_training_topic",
            "prediction_requests_topic"
        ]
        
        for topic_name in topics:
            topic = config.get_topic(topic_name)
            assert topic is not None
            assert isinstance(topic, str)
            assert len(topic) > 0
    
    def test_message_types(self):
        """Test all message types"""
        message_types = [
            MessageType.RAW_DATA,
            MessageType.PROCESSED_DATA,
            MessageType.MODEL_TRAINING,
            MessageType.MODEL_EVALUATION,
            MessageType.PREDICTION_REQUEST,
            MessageType.PREDICTION_RESULT,
            MessageType.MONITORING,
            MessageType.ALERT
        ]
        
        for msg_type in message_types:
            message = create_message(msg_type, {"test": "data"}, "test")
            assert message.message_type == msg_type
            assert message.to_dict()['message_type'] == msg_type.value


class TestKafkaHealthCheck:
    """Test Kafka health checking functionality"""
    
    @patch('kafka_utils.KafkaProducer')
    @patch('kafka_utils.KafkaConsumer')
    def test_health_checker_initialization(self, mock_consumer, mock_producer):
        """Test health checker initialization"""
        from kafka_utils import KafkaHealthChecker
        
        config = get_kafka_config()
        health_checker = KafkaHealthChecker(config)
        
        assert health_checker is not None
        assert hasattr(health_checker, 'config')
    
    def test_health_check_methods_exist(self):
        """Test that health check methods exist"""
        from kafka_utils import KafkaHealthChecker
        
        config = get_kafka_config()
        health_checker = KafkaHealthChecker(config)
        
        assert hasattr(health_checker, 'check_producer_health')
        assert hasattr(health_checker, 'check_consumer_health')
        assert hasattr(health_checker, 'check_overall_health')
        
        assert callable(health_checker.check_producer_health)
        assert callable(health_checker.check_consumer_health)
        assert callable(health_checker.check_overall_health)


# Utility functions for testing
def create_test_message(message_type: MessageType, data: dict = None):
    """Create a test message"""
    if data is None:
        data = {"test": "data"}
    
    return create_message(message_type, data, "test-source")


def test_kafka_connectivity():
    """Test basic Kafka connectivity (requires running Kafka)"""
    try:
        config = get_kafka_config()
        from kafka_utils import KafkaHealthChecker
        
        health_checker = KafkaHealthChecker(config)
        health_status = health_checker.check_overall_health()
        
        print(f"Kafka Health Status: {health_status}")
        return health_status
        
    except Exception as e:
        print(f"Kafka connectivity test failed: {e}")
        return None


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running Kafka Integration Tests...")
    
    # Test configuration
    config = get_kafka_config()
    print(f"✅ Configuration loaded: {config.config_path}")
    
    # Test message creation
    message = create_test_message(MessageType.RAW_DATA)
    print(f"✅ Message created: {message.message_id}")
    
    # Test health check (if Kafka is running)
    health_status = test_kafka_connectivity()
    if health_status:
        print(f"✅ Kafka health check: {health_status}")
    else:
        print("⚠️ Kafka not available for health check")
    
    print("🎉 Kafka integration tests completed!") 