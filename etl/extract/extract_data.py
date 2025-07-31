import pandas as pd
import os
import yaml
from src.utils.logging import get_logger

logger = get_logger('extract_data')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def extract_from_csv(file_path):
    """Extract data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully extracted {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from CSV {file_path}: {e}")
        return None

def extract_data(source_type='csv', **kwargs):
    """Main extraction function"""
    config = load_config()
    
    if source_type == 'csv':
        file_path = kwargs.get('file_path', os.path.join(config['raw_data_path'], 'data.csv'))
        return extract_from_csv(file_path)
    else:
        logger.error(f"Unsupported source type: {source_type}")
        return None 