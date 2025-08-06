"""
Model Retraining Pipeline
This DAG handles weekly model retraining using aggregated historical data.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
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

def collect_historical_data(**context):
    """
    Collect and aggregate historical prediction data for model retraining
    """
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Load historical predictions
    predictions_file = '/opt/airflow/data/predictions_history.csv'
    
    try:
        if os.path.exists(predictions_file):
            df = pd.read_csv(predictions_file)
            logger.info(f"Loaded {len(df)} historical predictions")
        else:
            logger.warning("No historical predictions found, creating sample data")
            df = pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading historical data: {e}")
        df = pd.DataFrame()
    
    # If no data, create sample data for demonstration
    if df.empty:
        logger.info("Creating sample historical data for retraining")
        sample_data = []
        for i in range(100):
            sample_data.append({
                'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
                'match_id': f"match_{i}",
                'current_minute': np.random.randint(1, 90),
                'home_goals': np.random.randint(0, 4),
                'away_goals': np.random.randint(0, 4),
                'home_shots': np.random.randint(0, 15),
                'away_shots': np.random.randint(0, 15),
                'home_shots_on_target': np.random.randint(0, 8),
                'away_shots_on_target': np.random.randint(0, 8),
                'home_possession': np.random.uniform(30, 70),
                'away_possession': np.random.uniform(30, 70),
                'home_xg': np.random.uniform(0, 3),
                'away_xg': np.random.uniform(0, 3),
                'home_win_prob': np.random.uniform(0.2, 0.6),
                'away_win_prob': np.random.uniform(0.2, 0.6),
                'draw_prob': np.random.uniform(0.1, 0.3),
                'confidence': np.random.uniform(0.5, 0.9)
            })
        df = pd.DataFrame(sample_data)
    
    # Save aggregated data
    aggregated_file = '/opt/airflow/data/aggregated_training_data.csv'
    df.to_csv(aggregated_file, index=False)
    
    logger.info(f"Collected {len(df)} historical records for retraining")
    context['task_instance'].xcom_push(key='data_count', value=len(df))
    
    return len(df)

def prepare_training_data(**context):
    """
    Prepare features and labels for model training
    """
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    
    # Load aggregated data
    data_file = '/opt/airflow/data/aggregated_training_data.csv'
    
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        logger.error("No aggregated data found")
        return {}
    
    # Prepare features
    feature_columns = [
        'current_minute', 'home_goals', 'away_goals',
        'home_shots', 'away_shots', 'home_shots_on_target', 'away_shots_on_target',
        'home_possession', 'away_possession', 'home_xg', 'away_xg'
    ]
    
    # Create target variable (simplified win prediction)
    # For demonstration, we'll create a simple target based on goal difference
    df['goal_diff'] = df['home_goals'] - df['away_goals']
    df['target'] = np.where(df['goal_diff'] > 0, 'home_win',
                           np.where(df['goal_diff'] < 0, 'away_win', 'draw'))
    
    # Prepare X and y
    X = df[feature_columns].fillna(0)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed data
    training_data = {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train.values,
        'y_test': y_test.values,
        'feature_names': feature_columns,
        'scaler': scaler
    }
    
    # Save to files
    joblib.dump(X_train_scaled, '/opt/airflow/data/X_train.joblib')
    joblib.dump(X_test_scaled, '/opt/airflow/data/X_test.joblib')
    joblib.dump(y_train.values, '/opt/airflow/data/y_train.joblib')
    joblib.dump(y_test.values, '/opt/airflow/data/y_test.joblib')
    joblib.dump(scaler, '/opt/airflow/data/feature_scaler.joblib')
    
    logger.info(f"Prepared training data: {X_train.shape[0]} train, {X_test.shape[0]} test samples")
    context['task_instance'].xcom_push(key='training_info', value={
        'train_samples': X_train.shape[0],
        'test_samples': X_test.shape[0],
        'features': len(feature_columns)
    })
    
    return training_data

def train_model(**context):
    """
    Train a new model using the prepared data
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
    
    # Load training data
    X_train = joblib.load('/opt/airflow/data/X_train.joblib')
    X_test = joblib.load('/opt/airflow/data/X_test.joblib')
    y_train = joblib.load('/opt/airflow/data/y_train.joblib')
    y_test = joblib.load('/opt/airflow/data/y_test.joblib')
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Save model
    model_path = '/opt/airflow/data/retrained_model.joblib'
    joblib.dump(model, model_path)
    
    # Save evaluation results
    evaluation_results = {
        'accuracy': accuracy,
        'classification_report': report,
        'model_path': model_path,
        'timestamp': datetime.now().isoformat()
    }
    
    evaluation_file = '/opt/airflow/data/model_evaluation.json'
    with open(evaluation_file, 'w') as f:
        json.dump(evaluation_results, f, indent=2, default=str)
    
    logger.info(f"Model trained with accuracy: {accuracy:.3f}")
    context['task_instance'].xcom_push(key='model_accuracy', value=accuracy)
    
    return evaluation_results

def deploy_model(**context):
    """
    Deploy the new model by replacing the old one
    """
    import shutil
    import joblib
    from datetime import datetime
    
    # Source paths
    new_model_path = '/opt/airflow/data/retrained_model.joblib'
    new_scaler_path = '/opt/airflow/data/feature_scaler.joblib'
    
    # Target paths (where the API expects the model)
    target_model_path = '/opt/airflow/models/sales_prediction_model.joblib'
    target_scaler_path = '/opt/airflow/models/feature_scaler.joblib'
    
    # Create backup of current model
    backup_dir = f'/opt/airflow/models/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(target_model_path):
        shutil.copy2(target_model_path, f'{backup_dir}/old_model.joblib')
        logger.info(f"Backed up old model to {backup_dir}")
    
    if os.path.exists(target_scaler_path):
        shutil.copy2(target_scaler_path, f'{backup_dir}/old_scaler.joblib')
    
    # Deploy new model
    try:
        shutil.copy2(new_model_path, target_model_path)
        shutil.copy2(new_scaler_path, target_scaler_path)
        
        # Verify model can be loaded
        test_model = joblib.load(target_model_path)
        test_scaler = joblib.load(target_scaler_path)
        
        logger.info("New model deployed successfully")
        
        # Save deployment info
        deployment_info = {
            'deployment_time': datetime.now().isoformat(),
            'model_path': target_model_path,
            'scaler_path': target_scaler_path,
            'backup_dir': backup_dir,
            'status': 'success'
        }
        
        deployment_file = '/opt/airflow/data/last_deployment.json'
        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        context['task_instance'].xcom_push(key='deployment_status', value='success')
        return deployment_info
        
    except Exception as e:
        logger.error(f"Model deployment failed: {e}")
        context['task_instance'].xcom_push(key='deployment_status', value='failed')
        raise

# Create the DAG
dag = DAG(
    'model_retraining_pipeline',
    default_args=default_args,
    description='Weekly model retraining pipeline',
    schedule_interval=timedelta(weeks=1),  # Run weekly
    catchup=False,
    tags=['mlops', 'retraining', 'model']
)

# Define tasks
collect_data_task = PythonOperator(
    task_id='collect_historical_data',
    python_callable=collect_historical_data,
    dag=dag
)

prepare_data_task = PythonOperator(
    task_id='prepare_training_data',
    python_callable=prepare_training_data,
    dag=dag
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

deploy_model_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag
)

# Define task dependencies
collect_data_task >> prepare_data_task >> train_model_task >> deploy_model_task 