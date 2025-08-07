# Scheduled Kafka Integration Demo

This document describes the enhanced scheduling functionality added to the Kafka integration demo, showcasing how Kafka and Airflow work collaboratively in a real-time ML pipeline.

## Overview

The scheduling system provides multiple ways to run the Kafka integration demo:

1. **One-time execution** - Run the demo once for testing
2. **Interval scheduling** - Run every N seconds using the `schedule` library
3. **Advanced scheduling** - Use APScheduler for cron expressions and better job management

## Files

### Core Files
- `demo_kafka_integration.py` - Original demo with basic scheduling support
- `scheduled_kafka_demo.py` - Advanced demo with APScheduler support
- `requirements.txt` - Updated with scheduling dependencies

### New Features Added

#### Enhanced Data Generation
- Realistic football match data with comprehensive statistics
- Multiple data streams for different Airflow DAGs
- Enhanced metadata for ML pipeline processing

#### Kafka-Airflow Integration Showcase
- Sends data to multiple Kafka topics:
  - `live_football_events` - Main topic for football prediction pipeline
  - `ml_training_data` - High-scoring games for model training
  - `betting_analysis` - Important matches for betting analysis
  - `social_media_triggers` - Viral matches for social media monitoring

## Usage Examples

### Basic Scheduling (demo_kafka_integration.py)

```bash
# Run once
python demo_kafka_integration.py --once

# Run every 5 seconds (default)
python demo_kafka_integration.py

# Run every 10 seconds
python demo_kafka_integration.py --interval 10

# Cron expression (falls back to interval)
python demo_kafka_integration.py --cron "*/5 * * * *"
```

### Advanced Scheduling (scheduled_kafka_demo.py)

```bash
# Install APScheduler first
pip install apscheduler

# Run once with enhanced features
python scheduled_kafka_demo.py --once

# Run every 30 seconds
python scheduled_kafka_demo.py --interval 30

# Run every 5 minutes
python scheduled_kafka_demo.py --cron "*/5 * * * *"

# Run at 9 AM on weekdays
python scheduled_kafka_demo.py --cron "0 9 * * 1-5"

# Run every 2 hours
python scheduled_kafka_demo.py --cron "0 */2 * * *"
```

## Kafka-Airflow Collaboration Showcase

### Data Flow
1. **Scheduled Demo** generates realistic football match data
2. **Kafka Producer** sends data to multiple topics based on match characteristics
3. **Airflow DAGs** consume from these topics and process data differently:
   - `football_prediction_pipeline` - Processes live events for real-time predictions
   - `retraining_pipeline` - Uses high-scoring games for model retraining

### Enhanced Data Features
- **Match Statistics**: Goals, shots, possession, cards, fouls
- **Context Data**: Weather, attendance, referee, stadium
- **ML Features**: Team form, rankings, market values, betting odds
- **Processing Metadata**: Priority levels, expected social media volume

### Topic Routing Logic
- **live_football_events**: All matches
- **ml_training_data**: Matches with >2 total goals
- **betting_analysis**: High/very high rivalry matches
- **social_media_triggers**: Matches with high expected social media volume

## Monitoring and Logging

### Log Files
- `kafka_demo_scheduler.log` - Detailed execution logs
- Console output with emoji indicators for easy monitoring

### Key Metrics Tracked
- Demo execution count
- Scheduler uptime
- Kafka health status
- Message send success/failure rates

## Integration with Existing Airflow DAGs

The enhanced demo data is specifically designed to work with existing Airflow DAGs:

### football_pipeline.py
- Consumes from `live_football_events` topic
- Processes match data for real-time predictions
- Calls ML model API for win probability predictions

### retraining_pipeline.py
- Can be extended to consume from `ml_training_data` topic
- Uses high-scoring games for model improvement

## Prerequisites

### Required Services
1. **Kafka** - Must be running on localhost:29092
   ```bash
   docker-compose -f docker-compose.kafka.yml up -d
   ```

2. **Airflow** - Should be running to see full integration
   ```bash
   # Start Airflow services
   ./start_mlops.sh
   ```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **Kafka Not Available**
   - Ensure Kafka is running: `docker-compose -f docker-compose.kafka.yml up -d`
   - Check Kafka health: `docker-compose -f docker-compose.kafka.yml ps`

2. **APScheduler Import Error**
   - Install APScheduler: `pip install apscheduler`
   - Use basic demo if APScheduler is not needed

3. **Permission Errors**
   - Ensure write permissions for log files
   - Run with appropriate user permissions

### Monitoring Commands

```bash
# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Monitor Kafka messages
docker exec -it kafka kafka-console-consumer --topic live_football_events --bootstrap-server localhost:9092

# Check Airflow DAGs
curl http://localhost:8081/api/v1/dags
```

## Next Steps

1. **Start the scheduled demo** to generate continuous data
2. **Monitor Airflow UI** at http://localhost:8081 to see DAG executions
3. **Check Kafka UI** at http://localhost:8080 to see message flow
4. **Extend the demo** with additional data types or processing logic
5. **Scale the system** by adding more Kafka partitions or Airflow workers

## Architecture Benefits

This scheduling system demonstrates:
- **Decoupled Architecture**: Kafka acts as the message broker between data generation and processing
- **Scalable Processing**: Airflow DAGs can process different data streams independently
- **Real-time Capabilities**: Continuous data generation simulates live event streams
- **Flexible Scheduling**: Multiple scheduling options for different use cases
- **Monitoring and Observability**: Comprehensive logging and metrics tracking
