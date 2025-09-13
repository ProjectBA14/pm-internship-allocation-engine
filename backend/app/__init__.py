"""
Flask Application Factory
Creates and configures the Flask application instance
"""

from flask import Flask
from config.settings import Config
import logging

def create_app(config_class=Config):
    """
    Create Flask application using the application factory pattern
    
    Args:
        config_class: Configuration class to use
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Register application context
    with app.app_context():
        # Initialize extensions here if needed
        pass
    
    return app
