"""
Real-time Football Match Prediction Pipeline
This DAG orchestrates the end-to-end MLOps pipeline for real-time football match predictions.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
import logging
import pandas as pd
import requests
from typing import Dict, List, Any
import os
import sys

# Add the project root to Python path
sys.path.append('/opt/airflow')

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def consume_kafka_events(**context):
    """
    Consume events from Kafka topic and store them for processing
    """
    from kafka import KafkaConsumer
    import json
    from datetime import datetime
    
    # Kafka configuration
    kafka_broker = 'kafka:29092'
    topic = 'live_football_events'
    
    # File to store consumed events
    events_file = '/opt/airflow/data/consumed_events.json'
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[kafka_broker],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',  # Only consume new messages
            enable_auto_commit=True,
            group_id='airflow_consumer_group'
        )
        
        events = []
        # Consume messages for a limited time
        start_time = datetime.now()
        timeout = 30  # seconds
        
        logger.info(f"Starting to consume events from topic: {topic}")
        
        for message in consumer:
            if (datetime.now() - start_time).seconds > timeout:
                break
                
            event = message.value
            events.append(event)
            logger.info(f"Consumed event: {event.get('type', {}).get('name', 'Unknown')}")
        
        consumer.close()
        
        # Save consumed events
        os.makedirs(os.path.dirname(events_file), exist_ok=True)
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=2)
        
        logger.info(f"Consumed {len(events)} events and saved to {events_file}")
        
        # Pass event count to next task
        context['task_instance'].xcom_push(key='event_count', value=len(events))
        
        return len(events)
        
    except Exception as e:
        logger.error(f"Error consuming Kafka events: {e}")
        # Create sample events if Kafka is not available
        sample_events = [
            {
                'id': 1,
                'minute': 15,
                'type': {'name': 'Shot'},
                'team': {'name': 'Manchester United'},
                'shot': {'outcome': {'name': 'Goal'}},
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 2,
                'minute': 25,
                'type': {'name': 'Pass'},
                'team': {'name': 'Liverpool'},
                'pass': {'outcome': {'name': 'Complete'}},
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        os.makedirs(os.path.dirname(events_file), exist_ok=True)
        with open(events_file, 'w') as f:
            json.dump(sample_events, f, indent=2)
        
        logger.info(f"Created {len(sample_events)} sample events")
        context['task_instance'].xcom_push(key='event_count', value=len(sample_events))
        return len(sample_events)

def engineer_features(**context):
    """
    Perform feature engineering on consumed events
    """
    import json
    from collections import defaultdict
    
    # Load consumed events
    events_file = '/opt/airflow/data/consumed_events.json'
    
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        logger.warning("No events file found, creating sample features")
        events = []
    
    if not events:
        logger.warning("No events to process")
        return {}
    
    # Initialize feature tracking
    features = {
        'home_team': 'Manchester United',
        'away_team': 'Liverpool',
        'current_minute': 0,
        'home_goals': 0,
        'away_goals': 0,
        'home_shots': 0,
        'away_shots': 0,
        'home_shots_on_target': 0,
        'away_shots_on_target': 0,
        'home_passes': 0,
        'away_passes': 0,
        'home_passes_completed': 0,
        'away_passes_completed': 0,
        'home_possession': 0,
        'away_possession': 0,
        'home_xg': 0.0,
        'away_xg': 0.0
    }
    
    # Process events to calculate features
    for event in events:
        minute = event.get('minute', 0)
        event_type = event.get('type', {}).get('name', '')
        team_name = event.get('team', {}).get('name', '')
        
        # Update current minute
        features['current_minute'] = max(features['current_minute'], minute)
        
        # Determine if it's home or away team
        is_home = team_name == features['home_team']
        is_away = team_name == features['away_team']
        
        if not (is_home or is_away):
            continue
        
        # Count goals
        if event_type == 'Shot':
            if is_home:
                features['home_shots'] += 1
                if event.get('shot', {}).get('outcome', {}).get('name') == 'Goal':
                    features['home_goals'] += 1
                    features['home_shots_on_target'] += 1
                elif event.get('shot', {}).get('outcome', {}).get('name') == 'Saved':
                    features['home_shots_on_target'] += 1
            elif is_away:
                features['away_shots'] += 1
                if event.get('shot', {}).get('outcome', {}).get('name') == 'Goal':
                    features['away_goals'] += 1
                    features['away_shots_on_target'] += 1
                elif event.get('shot', {}).get('outcome', {}).get('name') == 'Saved':
                    features['away_shots_on_target'] += 1
        
        # Count passes
        elif event_type == 'Pass':
            if is_home:
                features['home_passes'] += 1
                if event.get('pass', {}).get('outcome', {}).get('name') == 'Complete':
                    features['home_passes_completed'] += 1
            elif is_away:
                features['away_passes'] += 1
                if event.get('pass', {}).get('outcome', {}).get('name') == 'Complete':
                    features['away_passes_completed'] += 1
    
    # Calculate possession (simplified)
    total_passes = features['home_passes'] + features['away_passes']
    if total_passes > 0:
        features['home_possession'] = (features['home_passes'] / total_passes) * 100
        features['away_possession'] = (features['away_passes'] / total_passes) * 100
    
    # Calculate xG (simplified based on shots)
    features['home_xg'] = features['home_shots'] * 0.15  # Simplified xG calculation
    features['away_xg'] = features['away_shots'] * 0.15
    
    # Save features
    features_file = '/opt/airflow/data/match_features.json'
    os.makedirs(os.path.dirname(features_file), exist_ok=True)
    with open(features_file, 'w') as f:
        json.dump(features, f, indent=2)
    
    logger.info(f"Engineered features: {features}")
    context['task_instance'].xcom_push(key='features', value=features)
    
    return features

def call_model_api(**context):
    """
    Call the model API to get win probability prediction
    """
    import requests
    import json
    
    # Load features
    features_file = '/opt/airflow/data/match_features.json'
    
    try:
        with open(features_file, 'r') as f:
            features = json.load(f)
    except FileNotFoundError:
        logger.error("Features file not found")
        return {}
    
    # Prepare prediction request
    prediction_data = {
        'home_goals': features.get('home_goals', 0),
        'away_goals': features.get('away_goals', 0),
        'current_minute': features.get('current_minute', 0),
        'home_shots': features.get('home_shots', 0),
        'away_shots': features.get('away_shots', 0),
        'home_shots_on_target': features.get('home_shots_on_target', 0),
        'away_shots_on_target': features.get('away_shots_on_target', 0),
        'home_possession': features.get('home_possession', 50),
        'away_possession': features.get('away_possession', 50),
        'home_xg': features.get('home_xg', 0.0),
        'away_xg': features.get('away_xg', 0.0)
    }
    
    try:
        # Call model API
        api_url = 'http://api:8000/predict'
        response = requests.post(api_url, json=prediction_data, timeout=10)
        
        if response.status_code == 200:
            prediction = response.json()
            logger.info(f"Model prediction: {prediction}")
            
            # Save prediction
            prediction_file = '/opt/airflow/data/prediction.json'
            os.makedirs(os.path.dirname(prediction_file), exist_ok=True)
            with open(prediction_file, 'w') as f:
                json.dump(prediction, f, indent=2)
            
            context['task_instance'].xcom_push(key='prediction', value=prediction)
            return prediction
        else:
            logger.error(f"API call failed with status {response.status_code}")
            return {}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling model API: {e}")
        # Create sample prediction if API is not available
        sample_prediction = {
            'home_win_probability': 0.45,
            'away_win_probability': 0.35,
            'draw_probability': 0.20,
            'confidence': 0.75,
            'timestamp': datetime.now().isoformat()
        }
        
        prediction_file = '/opt/airflow/data/prediction.json'
        os.makedirs(os.path.dirname(prediction_file), exist_ok=True)
        with open(prediction_file, 'w') as f:
            json.dump(sample_prediction, f, indent=2)
        
        context['task_instance'].xcom_push(key='prediction', value=sample_prediction)
        return sample_prediction

def store_results(**context):
    """
    Store the processed results and predictions
    """
    import json
    import pandas as pd
    from datetime import datetime
    
    # Load all data
    features_file = '/opt/airflow/data/match_features.json'
    prediction_file = '/opt/airflow/data/prediction.json'
    
    try:
        with open(features_file, 'r') as f:
            features = json.load(f)
    except FileNotFoundError:
        features = {}
    
    try:
        with open(prediction_file, 'r') as f:
            prediction = json.load(f)
    except FileNotFoundError:
        prediction = {}
    
    # Combine all results
    results = {
        'timestamp': datetime.now().isoformat(),
        'match_id': f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'features': features,
        'prediction': prediction
    }
    
    # Save to JSON
    results_file = '/opt/airflow/data/pipeline_results.json'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save to CSV for analysis
    csv_data = {
        'timestamp': [results['timestamp']],
        'match_id': [results['match_id']],
        'current_minute': [features.get('current_minute', 0)],
        'home_goals': [features.get('home_goals', 0)],
        'away_goals': [features.get('away_goals', 0)],
        'home_win_prob': [prediction.get('home_win_probability', 0)],
        'away_win_prob': [prediction.get('away_win_probability', 0)],
        'draw_prob': [prediction.get('draw_probability', 0)],
        'confidence': [prediction.get('confidence', 0)]
    }
    
    df = pd.DataFrame(csv_data)
    csv_file = '/opt/airflow/data/predictions_history.csv'
    
    # Append to existing CSV or create new
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)
    
    logger.info(f"Stored results: {results}")
    context['task_instance'].xcom_push(key='results', value=results)
    
    return results

# Create the DAG
dag = DAG(
    'football_prediction_pipeline',
    default_args=default_args,
    description='Real-time football match prediction pipeline',
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    tags=['mlops', 'football', 'prediction']
)

# Define tasks
consume_events_task = PythonOperator(
    task_id='consume_kafka_events',
    python_callable=consume_kafka_events,
    dag=dag
)

engineer_features_task = PythonOperator(
    task_id='engineer_features',
    python_callable=engineer_features,
    dag=dag
)

call_model_task = PythonOperator(
    task_id='call_model_api',
    python_callable=call_model_api,
    dag=dag
)

store_results_task = PythonOperator(
    task_id='store_results',
    python_callable=store_results,
    dag=dag
)

# Define task dependencies
consume_events_task >> engineer_features_task >> call_model_task >> store_results_task 