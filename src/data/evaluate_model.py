import joblib
import yaml
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
from src.utils.logging import get_logger

logger = get_logger('evaluate_model')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def evaluate_model(model, X_test, y_test, config, task='regression'):
    """Evaluate model performance on test data"""
    logger.info(f"Evaluating model for {task} task")
    
    try:
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics based on task type
        if task == 'regression':
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = mse ** 0.5
            
            metrics = {
                'mse': mse,
                'r2': r2,
                'rmse': rmse,
                'mae': abs(y_test - y_pred).mean()
            }
            
            logger.info(f"Regression Metrics: MSE={mse:.4f}, R²={r2:.4f}, RMSE={rmse:.4f}")
            
        else:  # classification
            accuracy = accuracy_score(y_test, y_pred)
            
            metrics = {
                'accuracy': accuracy,
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
            logger.info(f"Classification Accuracy: {accuracy:.4f}")
        
        # Add predictions to metrics
        metrics['predictions'] = y_pred.tolist()
        metrics['actual'] = y_test.tolist()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error evaluating model: {e}")
        return None

def compare_models(model_results, X_test, y_test, config):
    """Compare multiple models"""
    logger.info("Comparing multiple models")
    
    comparison_results = {}
    
    for model_name, model_data in model_results.items():
        model = model_data['model']
        task = model_data.get('task', 'regression')
        
        evaluation = evaluate_model(model, X_test, y_test, config, task)
        if evaluation:
            comparison_results[model_name] = evaluation
    
    return comparison_results

def generate_evaluation_report(evaluation_results, output_path='data/processed/evaluation_report.txt'):
    """Generate a detailed evaluation report"""
    logger.info("Generating evaluation report")
    
    try:
        with open(output_path, 'w') as f:
            f.write("MODEL EVALUATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            for metric, value in evaluation_results.items():
                if metric not in ['predictions', 'actual']:
                    f.write(f"{metric.upper()}: {value}\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("Report generated successfully\n")
        
        logger.info(f"Evaluation report saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating evaluation report: {e}")
        return False 