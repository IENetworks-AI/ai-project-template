import os
import yaml
import json
import pandas as pd

def ensure_dir(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

def load_yaml_config(config_path):
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return None

def save_yaml_config(config, config_path):
    """Save configuration to YAML file"""
    try:
        ensure_dir(os.path.dirname(config_path))
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")
        return False

def load_json_config(config_path):
    """Load JSON configuration file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON config from {config_path}: {e}")
        return None

def save_json_config(config, config_path):
    """Save configuration to JSON file"""
    try:
        ensure_dir(os.path.dirname(config_path))
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON config to {config_path}: {e}")
        return False

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