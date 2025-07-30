import pandas as pd
import joblib
import os
import yaml
from src.utils.logging import get_logger

logger = get_logger('load_data')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def save_to_csv(df, file_path):
    """Save DataFrame to CSV"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        logger.info(f"Data saved to CSV: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV {file_path}: {e}")
        return False

def save_to_oracle(df, table_name, config):
    """Save DataFrame to Oracle database"""
    try:
        import cx_Oracle
        connection_string = f"{config['database']['username']}/{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['service_name']}"
        connection = cx_Oracle.connect(connection_string)
        
        # Create table if not exists
        create_table_sql = f"""
        CREATE TABLE {table_name} (
            {', '.join([f'{col} VARCHAR2(255)' for col in df.columns])}
        )
        """
        try:
            connection.execute(create_table_sql)
        except:
            pass  # Table might already exist
        
        # Insert data
        for _, row in df.iterrows():
            insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in df.columns])})"
            connection.execute(insert_sql, row.values.tolist())
        
        connection.commit()
        connection.close()
        logger.info(f"Data saved to Oracle table: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error saving to Oracle database: {e}")
        return False

def save_model(model, model_name, config):
    """Save trained model"""
    try:
        models_dir = config['models_path']
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, f"{model_name}.joblib")
        joblib.dump(model, model_path)
        logger.info(f"Model saved: {model_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving model {model_name}: {e}")
        return False

def save_scaler(scaler, scaler_name, config):
    """Save fitted scaler"""
    try:
        models_dir = config['models_path']
        os.makedirs(models_dir, exist_ok=True)
        scaler_path = os.path.join(models_dir, f"{scaler_name}.joblib")
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved: {scaler_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving scaler {scaler_name}: {e}")
        return False

def load_data(file_path, file_type='csv'):
    """Load data from various sources"""
    try:
        if file_type == 'csv':
            return pd.read_csv(file_path)
        elif file_type == 'joblib':
            return joblib.load(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return None 