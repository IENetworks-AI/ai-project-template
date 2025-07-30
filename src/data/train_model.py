import joblib
import os
import yaml
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from src.utils.logging import get_logger

logger = get_logger('train_model')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_model(model_type='random_forest', task='regression'):
    """Get model based on type and task"""
    if task == 'regression':
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'linear': LinearRegression(),
            'svr': SVR()
        }
    else:  # classification
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'logistic': LogisticRegression(random_state=42),
            'svc': SVC(random_state=42)
        }
    
    return models.get(model_type, models['random_forest'])

def train_model(X_train, y_train, config, model_type='random_forest', task='regression'):
    """Train model with given data"""
    logger.info(f"Training {model_type} model for {task} task")
    
    try:
        # Get model
        model = get_model(model_type, task)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions on training data
        y_pred = model.predict(X_train)
        
        # Calculate training metrics
        if task == 'regression':
            train_mse = mean_squared_error(y_train, y_pred)
            train_r2 = r2_score(y_train, y_pred)
            train_metrics = {
                'mse': train_mse,
                'r2': train_r2,
                'rmse': train_mse ** 0.5
            }
        else:
            train_accuracy = accuracy_score(y_train, y_pred)
            train_metrics = {
                'accuracy': train_accuracy
            }
        
        logger.info(f"Training completed. Metrics: {train_metrics}")
        
        return {
            'model': model,
            'model_type': model_type,
            'task': task,
            'train_metrics': train_metrics,
            'feature_importance': getattr(model, 'feature_importances_', None)
        }
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return None

def train_multiple_models(X_train, y_train, config, task='regression'):
    """Train multiple models and compare performance"""
    logger.info("Training multiple models for comparison")
    
    models_to_train = ['random_forest', 'linear'] if task == 'regression' else ['random_forest', 'logistic']
    results = {}
    
    for model_type in models_to_train:
        logger.info(f"Training {model_type} model")
        result = train_model(X_train, y_train, config, model_type, task)
        if result:
            results[model_type] = result
    
    # Find best model
    if task == 'regression':
        best_model = max(results.keys(), key=lambda x: results[x]['train_metrics']['r2'])
    else:
        best_model = max(results.keys(), key=lambda x: results[x]['train_metrics']['accuracy'])
    
    logger.info(f"Best model: {best_model}")
    
    return results[best_model] 