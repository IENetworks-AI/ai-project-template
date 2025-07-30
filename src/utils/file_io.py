import os
import yaml
import json

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