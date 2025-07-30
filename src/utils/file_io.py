"""
File I/O utilities for Retail Sales Insight Pipeline
"""
import os
import yaml
import json
import pandas as pd

def ensure_dir(path: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        path: Directory path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if path and not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False

def load_yaml_config(config_path: str = 'config/config.yaml') -> dict:
    """
    Load YAML configuration file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return {}

def save_data(data, file_path):
    """Save data to file (CSV, JSON, etc.)"""
    try:
        # Handle case where file_path is just a filename (no directory)
        dir_path = os.path.dirname(file_path)
        if dir_path:  # Only create directory if there is a directory path
            ensure_dir(dir_path)
        
        if file_path.endswith('.csv'):
            data.to_csv(file_path, index=False)
        elif file_path.endswith('.json'):
            data.to_json(file_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return False

def load_data(file_path):
    """Load data from file (CSV, JSON, etc.)"""
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        raise FileNotFoundError(f"Could not load data from {file_path}") 