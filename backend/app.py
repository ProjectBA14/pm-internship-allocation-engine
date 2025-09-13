#!/usr/bin/env python3
"""
PM Internship Allocation Engine - Main Flask Application
Smart India Hackathon 2025

This is the main entry point for the Flask backend API that handles:
- CV parsing and information extraction
- Candidate-internship matching using AI
- User registration and authentication
- Admin dashboard functionality
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import application modules
from app import create_app
from app.routes import register_routes
from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

def main():
    """Main application entry point"""
    try:
        # Create Flask application
        app = create_app()
        
        # Configure CORS for frontend integration
        CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])
        
        # Initialize Flask-RESTful
        api = Api(app)
        
        # Register all routes
        register_routes(api)
        
        # Health check endpoint
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint for monitoring"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'PM Internship Allocation Engine',
                'version': '1.0.0'
            }), 200
        
        # Global error handlers
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Endpoint not found',
                'message': 'The requested resource does not exist',
                'status_code': 404
            }), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        
        # Start the application
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        print(f"🚀 Starting PM Internship Allocation Engine on port {port}")
        print(f"📊 Debug mode: {debug}")
        print(f"🌐 API endpoints available at http://localhost:{port}")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == '__main__':
    main()
