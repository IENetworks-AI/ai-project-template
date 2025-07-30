import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle missing dependencies gracefully
try:
    import yaml
    import joblib
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from src.data.evaluate_model import evaluate_model
    from src.utils.logging import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

logger = get_logger('evaluate_script')

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
    """Main evaluation script"""
    logger.info("Starting evaluation script")
    
    try:
        # Load configuration
        config = load_config()
        
        # For demonstration, we'll use a simple example
        # In practice, this would load a trained model and test data
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
        
        # Load model (or train a simple one for demo)
        model_path = "data/processed/models/trained_model.joblib"
        if os.path.exists(model_path):
            logger.info("Loading trained model...")
            model = joblib.load(model_path)
        else:
            logger.info("No trained model found, training a simple one for demo...")
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
        
        logger.info("Evaluating model...")
        result = evaluate_model(model, X_test, y_test, config, task='classification')
        
        if result:
            logger.info("Evaluation completed successfully!")
            logger.info(f"Test accuracy: {result.get('accuracy', 'N/A')}")
        else:
            logger.error("Evaluation failed!")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Evaluation script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
