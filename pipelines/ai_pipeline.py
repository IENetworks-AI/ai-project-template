import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import pandas as pd
from etl.extract.extract_data import extract_data
from etl.transform.transform_data import transform_data
from etl.load.load_data import save_to_csv, save_model, save_scaler
from src.data.train_model import train_model
from src.data.evaluate_model import evaluate_model
from src.utils.logging import get_logger

logger = get_logger('ai_pipeline')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    """Main AI pipeline orchestration"""
    logger.info("Starting AI Pipeline")
    
    # Load configuration
    config = load_config()
    
    try:
        # Step 1: Extract data
        logger.info("Step 1: Extracting data")
        df = extract_data(source_type='csv', file_path='data/Sales Dataset.csv')
        
        if df is None or df.empty:
            logger.error("No data extracted. Pipeline failed.")
            return False
        
        # Step 2: Transform data
        logger.info("Step 2: Transforming data")
        transformed_data = transform_data(df, target_column='Total Amount')
        
        if transformed_data is None:
            logger.error("Data transformation failed. Pipeline failed.")
            return False
        
        # Step 3: Train model
        logger.info("Step 3: Training model")
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
        features_df['target'] = transformed_data['y_train']
        save_to_csv(features_df, config['features_path'])
        
        # Save model
        save_model(model_results['model'], 'trained_model', config)
        
        # Save scaler
        save_scaler(transformed_data['scaler'], 'feature_scaler', config)
        
        # Save evaluation results
        evaluation_df = pd.DataFrame([evaluation_results])
        save_to_csv(evaluation_df, 'data/processed/evaluation_results.csv')
        
        logger.info("AI Pipeline completed successfully!")
        logger.info(f"Model Performance: {evaluation_results}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 