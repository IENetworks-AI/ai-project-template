"""
Flask Application for Retail Sales Insight API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.utils.logging import get_logger
from src.utils.file_io import load_yaml_config

# Import routes
from api.routes import api_bp

logger = get_logger('flask_app')

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = load_yaml_config()
    if config:
        app.config['API_CONFIG'] = config.get('api', {})
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    logger.info("Flask application created successfully")
    return app

app = create_app()

if __name__ == "__main__":
    config = load_yaml_config()
    api_config = config.get('api', {})
    
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 5000)
    debug = api_config.get('debug', False)
    
    logger.info(f"Starting Flask app on {host}:{port}")
    app.run(host=host, port=port, debug=debug) 