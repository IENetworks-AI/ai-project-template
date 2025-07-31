import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import pandas as pd
from pathlib import Path
from etl.extract.extract_data import extract_data
from etl.transform.transform_data import transform_data
from etl.load.load_data import save_to_csv, save_model, save_scaler
from src.data.train_model import train_model
from src.data.evaluate_model import evaluate_model
from src.utils.logging import get_logger
import joblib

logger = get_logger('ai_pipeline')

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def ensure_directory_structure():
    """Ensure all required directories exist"""
    base_dir = Path(__file__).parent.parent
    
    directories = [
        base_dir / 'models',
        base_dir / 'data' / 'processed',
        base_dir / 'logs'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def main():
    """Main AI pipeline orchestration"""
    logger.info("Starting ML Pipeline with Sample Sales Dataset")
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    logger.info(f"Base directory: {base_dir}")
    
    # Load configuration
    config = load_config()
    
    # Ensure directory structure
    ensure_directory_structure()
    
    try:
        # Step 1: Extract data from sample dataset
        logger.info("Step 1: Extracting data from Sales Dataset")
        data_path = base_dir / 'data' / 'Sales Dataset.csv'
        df = extract_data(source_type='csv', file_path=str(data_path))
        
        if df is None or df.empty:
            logger.error("No data extracted. Pipeline failed.")
            return False
        
        logger.info(f"Extracted {len(df)} records from Sales Dataset")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        # Step 2: Transform data
        logger.info("Step 2: Transforming data")
        transformed_data = transform_data(df, target_column=config['model']['target_column'])
        
        if transformed_data is None:
            logger.error("Data transformation failed. Pipeline failed.")
            return False
        
        # Step 3: Train model
        logger.info("Step 3: Training model")
        logger.info(f"Training data shape: X={transformed_data['X_train_scaled'].shape}, y={transformed_data['y_train'].shape}")
        model_results = train_model(
            X_train=transformed_data['X_train_scaled'],
            y_train=transformed_data['y_train'],
            config=config
        )
        
        if model_results is None:
            logger.error("Model training failed. Pipeline failed.")
            return False
        
        # Step 4: Evaluate model
        logger.info("Step 4: Evaluating model")
        logger.info(f"Test data shape: X={transformed_data['X_test_scaled'].shape}, y={transformed_data['y_test'].shape}")
        evaluation_results = evaluate_model(
            model=model_results['model'],
            X_test=transformed_data['X_test_scaled'],
            y_test=transformed_data['y_test'],
            config=config
        )
        
        # Step 5: Save results
        logger.info("Step 5: Saving results")
        
        # Save processed features
        features_df = transformed_data['X_train'].copy()
        features_path = base_dir / config['features_path']
        save_to_csv(features_df, str(features_path))
        
        # Save target separately
        target_df = pd.DataFrame({'target': transformed_data['y_train']})
        target_path = base_dir / 'data' / 'processed' / 'target.csv'
        save_to_csv(target_df, str(target_path))
        
        # Save model with absolute path
        model_path = base_dir / 'models' / 'sales_prediction_model.joblib'
        try:
            joblib.dump(model_results['model'], str(model_path))
            logger.info(f"Model saved: {model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
        
        # Save scaler with absolute path
        scaler_path = base_dir / 'models' / 'feature_scaler.joblib'
        try:
            joblib.dump(transformed_data['scaler'], str(scaler_path))
            logger.info(f"Scaler saved: {scaler_path}")
        except Exception as e:
            logger.error(f"Error saving scaler: {e}")
            return False
        
        # Save evaluation results
        evaluation_df = pd.DataFrame([evaluation_results])
        eval_path = base_dir / 'data' / 'processed' / 'evaluation_results.csv'
        save_to_csv(evaluation_df, str(eval_path))
        
        # Create evaluation report
        report_path = base_dir / 'data' / 'processed' / 'evaluation_report.txt'
        with open(report_path, 'w') as f:
            f.write("Sales Prediction Model Evaluation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Model Type: {model_results['model_type']}\n")
            f.write(f"Task: {model_results['task']}\n\n")
            f.write("Performance Metrics:\n")
            for metric, value in evaluation_results.items():
                # Skip non-numeric metrics like predictions and actual
                if metric not in ['predictions', 'actual']:
                    if isinstance(value, (int, float)):
                        f.write(f"  {metric}: {value:.4f}\n")
                    else:
                        f.write(f"  {metric}: {value}\n")
            f.write(f"\nTraining Records: {len(transformed_data['y_train'])}\n")
            f.write(f"Test Records: {len(transformed_data['y_test'])}\n")
            f.write(f"Features: {len(transformed_data['feature_names'])}\n")
        
        # Verify files were saved correctly
        logger.info("Verifying saved files:")
        model_files = [
            base_dir / 'models' / 'sales_prediction_model.joblib',
            base_dir / 'models' / 'feature_scaler.joblib',
            base_dir / 'data' / 'processed' / 'features.csv'
        ]
        
        for file_path in model_files:
            if file_path.exists():
                size = file_path.stat().st_size
                logger.info(f"✅ {file_path.name} exists ({size} bytes)")
            else:
                logger.error(f"❌ {file_path.name} not found")
                return False
        
        logger.info("ML Pipeline completed successfully!")
        logger.info(f"Model Performance: {evaluation_results}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 