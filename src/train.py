import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle missing dependencies gracefully
try:
    import yaml
except ImportError:
    print("❌ PyYAML not found. Installing required dependencies...")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from src.data.train_model import train_model
    from src.utils.logging import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

logger = get_logger('train_script')

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config/config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using default configuration")
        return {
            'model': {
                'test_size': 0.2,
                'random_state': 42
            }
        }
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

def main():
    """Main training script"""
    logger.info("Starting training script")
    
    try:
        # Load configuration
        config = load_config()
        
        # For demonstration, we'll use a simple example
        # In practice, this would load preprocessed data
        from sklearn.datasets import load_iris
        from sklearn.model_selection import train_test_split
        import pandas as pd
        
        logger.info("Loading example dataset (Iris)...")
        data = load_iris()
        X = pd.DataFrame(data.data, columns=data.feature_names)
        y = pd.Series(data.target)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info("Training model...")
        result = train_model(X_train, y_train, config, model_type='random_forest', task='classification')
        
        if result:
            logger.info("Training completed successfully!")
            logger.info(f"Training metrics: {result['train_metrics']}")
        else:
            logger.error("Training failed!")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Training script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
