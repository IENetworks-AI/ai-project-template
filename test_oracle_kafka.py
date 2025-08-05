#!/usr/bin/env python3
"""
Oracle Kafka Test Script

This script tests the Kafka installation and functionality on the Oracle server.
Run this script to verify that Kafka is working correctly.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src directory to path
sys.path.append('src')

try:
    from oracle_kafka_integration import (
        get_oracle_kafka_config,
        OracleKafkaProducer,
        OracleKafkaConsumer,
        check_oracle_kafka_health,
        get_oracle_kafka_status,
        create_oracle_ml_topics
    )
except ImportError as e:
    print(f"Error importing Oracle Kafka modules: {e}")
    print("Make sure you're running this on the Oracle server with the correct setup")
    sys.exit(1)

def test_kafka_health():
    """Test Kafka health status"""
    print("=== Testing Kafka Health ===")
    
    try:
        health = check_oracle_kafka_health()
        print(f"Health status: {json.dumps(health, indent=2)}")
        
        if health['overall_healthy']:
            print("✅ Kafka is healthy")
            return True
        else:
            print("❌ Kafka is not healthy")
            return False
    except Exception as e:
        print(f"❌ Error checking Kafka health: {e}")
        return False

def test_kafka_status():
    """Test Kafka status and topics"""
    print("\n=== Testing Kafka Status ===")
    
    try:
        status = get_oracle_kafka_status()
        print(f"Server IP: {status['server_ip']}")
        print(f"Kafka Port: {status['kafka_port']}")
        print(f"Zookeeper Port: {status['zookeeper_port']}")
        print(f"Topics: {status['topics']}")
        
        if len(status['topics']) > 0:
            print("✅ Topics are available")
            return True
        else:
            print("❌ No topics found")
            return False
    except Exception as e:
        print(f"❌ Error getting Kafka status: {e}")
        return False

def test_kafka_producer():
    """Test Kafka producer functionality"""
    print("\n=== Testing Kafka Producer ===")
    
    try:
        config = get_oracle_kafka_config()
        producer = OracleKafkaProducer(config)
        
        # Create test message
        test_message = {
            'message_id': f'test-{int(time.time())}',
            'message_type': 'test',
            'timestamp': datetime.now().isoformat(),
            'source': 'oracle-kafka-test',
            'data': {
                'test': True,
                'value': 42,
                'description': 'Oracle Kafka test message'
            }
        }
        
        # Send message to test topic
        topic = 'ml-pipeline-raw-data'
        success = producer.send_message(topic, test_message)
        
        if success:
            print(f"✅ Message sent successfully to {topic}")
            producer.close()
            return True
        else:
            print(f"❌ Failed to send message to {topic}")
            producer.close()
            return False
    except Exception as e:
        print(f"❌ Error testing producer: {e}")
        return False

def test_kafka_consumer():
    """Test Kafka consumer functionality"""
    print("\n=== Testing Kafka Consumer ===")
    
    try:
        config = get_oracle_kafka_config()
        consumer = OracleKafkaConsumer(config, 'test-consumer-group')
        
        # Flag to track if message was received
        message_received = {'received': False, 'data': None}
        
        def message_handler(message_data):
            """Handle received messages"""
            print(f"✅ Received message: {message_data}")
            message_received['received'] = True
            message_received['data'] = message_data
        
        # Start consuming in a separate thread
        import threading
        consumer_thread = threading.Thread(
            target=consumer.start_consuming,
            args=(['ml-pipeline-raw-data'], message_handler)
        )
        consumer_thread.daemon = True
        consumer_thread.start()
        
        # Wait for message or timeout
        timeout = 30  # seconds
        start_time = time.time()
        
        while not message_received['received'] and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        consumer.stop_consuming()
        
        if message_received['received']:
            print("✅ Consumer test successful")
            return True
        else:
            print("❌ No message received within timeout")
            return False
    except Exception as e:
        print(f"❌ Error testing consumer: {e}")
        return False

def test_topic_creation():
    """Test topic creation"""
    print("\n=== Testing Topic Creation ===")
    
    try:
        success = create_oracle_ml_topics()
        if success:
            print("✅ Topics created successfully")
            return True
        else:
            print("❌ Failed to create topics")
            return False
    except Exception as e:
        print(f"❌ Error creating topics: {e}")
        return False

def main():
    """Run all Kafka tests"""
    print("Oracle Kafka Test Suite")
    print("=" * 50)
    
    # Test results
    results = {}
    
    # Run tests
    results['health'] = test_kafka_health()
    results['status'] = test_kafka_status()
    results['topics'] = test_topic_creation()
    results['producer'] = test_kafka_producer()
    results['consumer'] = test_kafka_consumer()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Kafka is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 