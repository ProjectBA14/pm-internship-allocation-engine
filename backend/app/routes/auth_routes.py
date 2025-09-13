"""
Authentication API Routes
Handles user authentication and authorization
"""

from flask import request, jsonify
from flask_restful import Resource
import logging
from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class AuthAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def post(self, action):
        """
        Handle authentication actions
        
        Args:
            action: Authentication action (login, register, logout, verify)
        """
        try:
            data = request.get_json()
            
            if action == 'register':
                return self._register_user(data)
            elif action == 'login':
                return self._login_user(data)
            elif action == 'verify':
                return self._verify_token(data)
            elif action == 'logout':
                return self._logout_user(data)
            else:
                return {'error': 'Invalid action'}, 400
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'error': 'Authentication failed'}, 500
    
    def _register_user(self, data):
        """Register a new user"""
        required_fields = ['email', 'password', 'name', 'user_type']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return {'error': f'Missing required field: {field}'}, 400
        
        # Validate user type
        if data['user_type'] not in ['applicant', 'admin', 'company']:
            return {'error': 'Invalid user type'}, 400
        
        try:
            # Create user in Firebase Auth
            user_record = self.firebase_service.create_user(
                email=data['email'],
                password=data['password'],
                display_name=data['name']
            )
            
            # Store user profile in Firestore
            user_profile = {
                'uid': user_record.uid,
                'email': data['email'],
                'name': data['name'],
                'user_type': data['user_type'],
                'created_at': self.firebase_service.get_timestamp(),
                'profile_complete': False
            }
            
            self.firebase_service.create_document('users', user_record.uid, user_profile)
            
            return {
                'message': 'User registered successfully',
                'uid': user_record.uid,
                'user_type': data['user_type']
            }, 201
            
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return {'error': 'Failed to register user'}, 500
    
    def _login_user(self, data):
        """Login user and return session info"""
        if 'id_token' not in data:
            return {'error': 'Missing ID token'}, 400
        
        try:
            # Verify the ID token
            decoded_token = self.firebase_service.verify_id_token(data['id_token'])
            uid = decoded_token['uid']
            
            # Get user profile
            user_profile = self.firebase_service.get_document('users', uid)
            
            if not user_profile:
                return {'error': 'User profile not found'}, 404
            
            return {
                'message': 'Login successful',
                'user': user_profile,
                'token_valid': True
            }, 200
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return {'error': 'Invalid credentials'}, 401
    
    def _verify_token(self, data):
        """Verify user token"""
        if 'id_token' not in data:
            return {'error': 'Missing ID token'}, 400
        
        try:
            decoded_token = self.firebase_service.verify_id_token(data['id_token'])
            return {
                'valid': True,
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email')
            }, 200
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return {'valid': False, 'error': 'Invalid token'}, 401
    
    def _logout_user(self, data):
        """Logout user (client-side token invalidation)"""
        return {'message': 'Logout successful'}, 200
