"""
Oracle Server Kafka Integration for ML Pipeline System

This module provides Oracle-specific Kafka integration for the deployed ML pipeline
system on Oracle Cloud Infrastructure.
"""

import json
import logging
import time
import threading
import subprocess
import socket
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


class OracleKafkaConfig:
    """Oracle-specific Kafka configuration manager"""
    
    def __init__(self, config_path: str = "config/oracle_kafka_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.oracle_settings = self.config.get('oracle_deployment', {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Oracle-specific configuration"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Oracle Kafka config file not found: {self.config_path}")
            return self._get_default_oracle_config()
        except Exception as e:
            logger.error(f"Error loading Oracle Kafka config: {e}")
            return self._get_default_oracle_config()
    
    def _get_default_oracle_config(self) -> Dict[str, Any]:
        """Get default Oracle configuration"""
        return {
            'kafka': {
                'bootstrap_servers': '139.185.33.139:9092',
                'external_bootstrap_servers': '139.185.33.139:29092',
                'security_protocol': 'PLAINTEXT'
            },
            'oracle_deployment': {
                'server_ip': '139.185.33.139',
                'kafka_service_name': 'kafka.service',
                'zookeeper_service_name': 'zookeeper.service'
            }
        }
    
    def get_kafka_config(self) -> Dict[str, Any]:
        """Get Kafka connection configuration for Oracle"""
        kafka_config = self.config.get('kafka', {})
        # Use external bootstrap servers for remote connections
        if 'external_bootstrap_servers' in kafka_config:
            kafka_config['bootstrap_servers'] = kafka_config['external_bootstrap_servers']
        return kafka_config
    
    def get_oracle_settings(self) -> Dict[str, Any]:
        """Get Oracle deployment settings"""
        return self.oracle_settings


class OracleKafkaServiceManager:
    """Manages Kafka services on Oracle server"""
    
    def __init__(self, config: OracleKafkaConfig):
        self.config = config
        self.oracle_settings = config.get_oracle_settings()
    
    def check_service_status(self, service_name: str) -> bool:
        """Check if a systemd service is running"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and result.stdout.strip() == 'active'
        except Exception as e:
            logger.error(f"Error checking service {service_name}: {e}")
            return False
    
    def start_service(self, service_name: str) -> bool:
        """Start a systemd service"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'start', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"Started service: {service_name}")
                return True
            else:
                logger.error(f"Failed to start {service_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a systemd service"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'stop', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"Stopped service: {service_name}")
                return True
            else:
                logger.error(f"Failed to stop {service_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a systemd service"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"Restarted service: {service_name}")
                return True
            else:
                logger.error(f"Failed to restart {service_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            return False
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> str:
        """Get recent logs for a service"""
        try:
            result = subprocess.run(
                ['sudo', 'journalctl', '-u', service_name, '-n', str(lines), '--no-pager'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            logger.error(f"Error getting logs for {service_name}: {e}")
            return ""
    
    def check_kafka_health(self) -> Dict[str, Any]:
        """Check overall Kafka health on Oracle server"""
        zookeeper_service = self.oracle_settings.get('zookeeper_service_name', 'zookeeper.service')
        kafka_service = self.oracle_settings.get('kafka_service_name', 'kafka.service')
        
        zookeeper_status = self.check_service_status(zookeeper_service)
        kafka_status = self.check_service_status(kafka_service)
        
        # Check ports
        zookeeper_port = self.oracle_settings.get('zookeeper_port', 2181)
        kafka_port = self.oracle_settings.get('internal_port', 9092)
        kafka_external_port = self.oracle_settings.get('external_port', 29092)
        
        zookeeper_port_open = self.check_port_open('localhost', zookeeper_port)
        kafka_port_open = self.check_port_open('localhost', kafka_port)
        kafka_external_open = self.check_port_open('localhost', kafka_external_port)
        
        return {
            'zookeeper_service': zookeeper_status,
            'kafka_service': kafka_status,
            'zookeeper_port': zookeeper_port_open,
            'kafka_port': kafka_port_open,
            'kafka_external_port': kafka_external_open,
            'overall_healthy': zookeeper_status and kafka_status and zookeeper_port_open and kafka_port_open
        }
    
    def check_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
            return False
    
    def create_topics(self, topics: List[str]) -> bool:
        """Create Kafka topics on Oracle server"""
        try:
            kafka_home = self.oracle_settings.get('kafka_home', '/opt/kafka')
            bootstrap_server = f"localhost:{self.oracle_settings.get('internal_port', 9092)}"
            
            for topic in topics:
                cmd = [
                    'sudo', '-u', self.oracle_settings.get('kafka_user', 'kafka'),
                    f'{kafka_home}/bin/kafka-topics.sh',
                    '--create',
                    '--bootstrap-server', bootstrap_server,
                    '--replication-factor', '1',
                    '--partitions', '1',
                    '--topic', topic
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info(f"Created topic: {topic}")
                else:
                    logger.warning(f"Topic {topic} may already exist: {result.stderr}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating topics: {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """List all Kafka topics on Oracle server"""
        try:
            kafka_home = self.oracle_settings.get('kafka_home', '/opt/kafka')
            bootstrap_server = f"localhost:{self.oracle_settings.get('internal_port', 9092)}"
            
            cmd = [
                'sudo', '-u', self.oracle_settings.get('kafka_user', 'kafka'),
                f'{kafka_home}/bin/kafka-topics.sh',
                '--list',
                '--bootstrap-server', bootstrap_server
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                topics = [topic.strip() for topic in result.stdout.split('\n') if topic.strip()]
                return topics
            else:
                logger.error(f"Error listing topics: {result.stderr}")
                return []
        except Exception as e:
            logger.error(f"Error listing topics: {e}")
            return []


class OracleKafkaProducer:
    """Oracle-specific Kafka producer with enhanced error handling"""
    
    def __init__(self, config: OracleKafkaConfig):
        self.config = config
        self.producer = None
        self._lock = threading.Lock()
        self.service_manager = OracleKafkaServiceManager(config)
    
    def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer with Oracle settings"""
        if self.producer is None:
            with self._lock:
                if self.producer is None:
                    try:
                        producer_config = self.config.get_kafka_config()
                        # Add Oracle-specific producer settings
                        oracle_producer_settings = self.config.config.get('producer', {})
                        producer_config.update(oracle_producer_settings)
                        
                        self.producer = KafkaProducer(
                            bootstrap_servers=producer_config['bootstrap_servers'],
                            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                            key_serializer=lambda k: k.encode('utf-8') if k else None,
                            **{k: v for k, v in producer_config.items() if k != 'bootstrap_servers'}
                        )
                        logger.info("Oracle Kafka producer initialized successfully")
                    except Exception as e:
                        logger.error(f"Failed to initialize Oracle Kafka producer: {e}")
                        raise
        return self.producer
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """Send a message to Kafka topic with Oracle-specific error handling"""
        try:
            producer = self._get_producer()
            future = producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=30)  # Increased timeout for Oracle
            logger.info(f"Message sent to {topic} [partition: {record_metadata.partition}, offset: {record_metadata.offset}]")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            # Check if Kafka service is healthy
            health_status = self.service_manager.check_kafka_health()
            if not health_status['overall_healthy']:
                logger.warning("Kafka service appears to be unhealthy, attempting restart...")
                self.service_manager.restart_service('kafka.service')
            return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()
            self.producer = None
            logger.info("Oracle Kafka producer closed")


class OracleKafkaConsumer:
    """Oracle-specific Kafka consumer with enhanced error handling"""
    
    def __init__(self, config: OracleKafkaConfig, group_id: str = None):
        self.config = config
        self.group_id = group_id or config.config.get('consumer', {}).get('group_id', 'oracle-ml-pipeline-consumer')
        self.consumer = None
        self._running = False
        self._lock = threading.Lock()
        self.service_manager = OracleKafkaServiceManager(config)
    
    def _get_consumer(self, topics: List[str]) -> KafkaConsumer:
        """Get or create Kafka consumer with Oracle settings"""
        if self.consumer is None:
            with self._lock:
                if self.consumer is None:
                    try:
                        consumer_config = self.config.get_kafka_config()
                        # Add Oracle-specific consumer settings
                        oracle_consumer_settings = self.config.config.get('consumer', {})
                        consumer_config.update(oracle_consumer_settings)
                        consumer_config['group_id'] = self.group_id
                        
                        self.consumer = KafkaConsumer(
                            *topics,
                            bootstrap_servers=consumer_config['bootstrap_servers'],
                            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                            key_deserializer=lambda k: k.decode('utf-8') if k else None,
                            **{k: v for k, v in consumer_config.items() if k != 'bootstrap_servers'}
                        )
                        logger.info(f"Oracle Kafka consumer initialized for topics: {topics}")
                    except Exception as e:
                        logger.error(f"Failed to initialize Oracle Kafka consumer: {e}")
                        raise
        return self.consumer
    
    def start_consuming(self, topics: List[str], message_handler: Callable[[Dict[str, Any]], None]):
        """Start consuming messages with Oracle-specific error handling"""
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
                    
                    # Handle the message
                    message_handler(message_data)
                    
                    logger.debug(f"Processed message from {message.topic}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue processing other messages
                    
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            # Check if Kafka service is healthy
            health_status = self.service_manager.check_kafka_health()
            if not health_status['overall_healthy']:
                logger.warning("Kafka service appears to be unhealthy, attempting restart...")
                self.service_manager.restart_service('kafka.service')
        finally:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self._running = False
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            logger.info("Oracle Kafka consumer stopped and closed")


# Utility functions for Oracle deployment
def get_oracle_kafka_config() -> OracleKafkaConfig:
    """Get Oracle Kafka configuration instance"""
    return OracleKafkaConfig()


def check_oracle_kafka_health() -> Dict[str, Any]:
    """Check Oracle Kafka health"""
    config = get_oracle_kafka_config()
    service_manager = OracleKafkaServiceManager(config)
    return service_manager.check_kafka_health()


def create_oracle_ml_topics() -> bool:
    """Create ML pipeline topics on Oracle server"""
    config = get_oracle_kafka_config()
    service_manager = OracleKafkaServiceManager(config)
    
    topics = [
        'ml-pipeline-raw-data',
        'ml-pipeline-processed-data',
        'ml-pipeline-model-training',
        'ml-pipeline-model-evaluation',
        'ml-pipeline-prediction-requests',
        'ml-pipeline-prediction-results',
        'ml-pipeline-monitoring',
        'ml-pipeline-alerts',
        'ml-pipeline-dead-letter'
    ]
    
    return service_manager.create_topics(topics)


def get_oracle_kafka_status() -> Dict[str, Any]:
    """Get comprehensive Oracle Kafka status"""
    config = get_oracle_kafka_config()
    service_manager = OracleKafkaServiceManager(config)
    
    health_status = service_manager.check_kafka_health()
    topics = service_manager.list_topics()
    
    return {
        'health': health_status,
        'topics': topics,
        'server_ip': config.oracle_settings.get('server_ip', '139.185.33.139'),
        'kafka_port': config.oracle_settings.get('external_port', 29092),
        'zookeeper_port': config.oracle_settings.get('zookeeper_port', 2181)
    }


# Example usage
if __name__ == "__main__":
    logger.info("Testing Oracle Kafka integration...")
    
    # Check health
    health = check_oracle_kafka_health()
    logger.info(f"Oracle Kafka health: {health}")
    
    # Get status
    status = get_oracle_kafka_status()
    logger.info(f"Oracle Kafka status: {status}")
    
    # Create topics
    if create_oracle_ml_topics():
        logger.info("ML pipeline topics created successfully")
    else:
        logger.warning("Failed to create some topics (may already exist)") 