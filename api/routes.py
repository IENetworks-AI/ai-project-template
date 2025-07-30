from flask import jsonify, Blueprint, request
import pandas as pd
import yaml
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging import get_logger

bp = Blueprint('routes', __name__)
logger = get_logger('api_routes')

# Load configuration
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

@bp.route('/', methods=['GET'])
def root():
    """API information endpoint"""
    return jsonify({
        'message': 'Oracle AI Project API',
        'endpoints': ['/health', '/model/info', '/model/predict'],
        'version': '1.0.0'
    })

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Oracle AI API'})

@bp.route('/model/info', methods=['GET'])
def model_info():
    """Get information about trained models"""
    try:
        models_dir = config['models_path']
        models_info = {}
        
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.joblib'):
                    model_path = os.path.join(models_dir, file)
                    model = joblib.load(model_path)
                    models_info[file] = {
                        'type': type(model).__name__,
                        'parameters': getattr(model, 'get_params', lambda: {})()
                    }
        
        return jsonify({
            'models': models_info,
            'models_count': len(models_info)
        })
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/model/predict', methods=['POST'])
def predict():
    """Make predictions using trained model"""
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({'error': 'No features provided'}), 400
        
        # Load model and scaler
        model_path = os.path.join(config['models_path'], 'trained_model.joblib')
        scaler_path = os.path.join(config['models_path'], 'feature_scaler.joblib')
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model not found. Please train the model first.'}), 404
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
        
        # Prepare features
        features = pd.DataFrame([data['features']])
        
        # Scale features if scaler exists
        if scaler:
            features_scaled = scaler.transform(features)
        else:
            features_scaled = features
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        return jsonify({
            'prediction': float(prediction),
            'model_type': type(model).__name__,
            'features_used': len(features.columns)
        })
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/data/features', methods=['GET'])
def get_features():
    """Get processed features data"""
    try:
        features_path = config['features_path']
        if os.path.exists(features_path):
            df = pd.read_csv(features_path)
            return jsonify({
                'features_count': len(df.columns),
                'samples_count': len(df),
                'columns': df.columns.tolist()
            })
        else:
            return jsonify({'error': 'Features file not found'}), 404
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        return jsonify({'error': str(e)}), 500

def register_routes(app):
    app.register_blueprint(bp) 