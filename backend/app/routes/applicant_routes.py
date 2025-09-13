"""
Applicant Management API Routes
Handles applicant profiles, CV parsing, and registration
"""

from flask import request, jsonify
from flask_restful import Resource
import logging
from werkzeug.utils import secure_filename
import os

from services.firebase_service import FirebaseService
from services.gemini_service import GeminiService
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class ApplicantAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self, applicant_id):
        """Get applicant profile by ID"""
        try:
            applicant = self.firebase_service.get_document('applicants', applicant_id)
            if not applicant:
                return {'error': 'Applicant not found'}, 404
            
            return {'applicant': applicant}, 200
            
        except Exception as e:
            logger.error(f"Error retrieving applicant: {str(e)}")
            return {'error': 'Failed to retrieve applicant'}, 500
    
    def put(self, applicant_id):
        """Update applicant profile"""
        try:
            data = request.get_json()
            
            # Update timestamp
            data['updated_at'] = self.firebase_service.get_timestamp()
            
            # Update document
            self.firebase_service.update_document('applicants', applicant_id, data)
            
            return {'message': 'Applicant profile updated successfully'}, 200
            
        except Exception as e:
            logger.error(f"Error updating applicant: {str(e)}")
            return {'error': 'Failed to update applicant'}, 500
    
    def delete(self, applicant_id):
        """Delete applicant profile"""
        try:
            self.firebase_service.delete_document('applicants', applicant_id)
            return {'message': 'Applicant deleted successfully'}, 200
            
        except Exception as e:
            logger.error(f"Error deleting applicant: {str(e)}")
            return {'error': 'Failed to delete applicant'}, 500

class ApplicantListAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self):
        """Get list of all applicants with filtering"""
        try:
            # Get query parameters
            location = request.args.get('location')
            category = request.args.get('category')
            skill = request.args.get('skill')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # Build query
            query = self.firebase_service.get_collection('applicants')
            
            # Apply filters
            if location:
                query = query.where('location', '==', location)
            if category:
                query = query.where('category', '==', category)
            if skill:
                query = query.where('skills', 'array_contains', skill)
            
            # Execute query
            applicants = []
            docs = query.limit(per_page).offset((page - 1) * per_page).get()
            
            for doc in docs:
                applicant_data = doc.to_dict()
                applicant_data['id'] = doc.id
                applicants.append(applicant_data)
            
            return {
                'applicants': applicants,
                'page': page,
                'per_page': per_page,
                'total': len(applicants)
            }, 200
            
        except Exception as e:
            logger.error(f"Error retrieving applicants: {str(e)}")
            return {'error': 'Failed to retrieve applicants'}, 500
    
    def post(self):
        """Create new applicant profile"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'location', 'category']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Add metadata
            data['created_at'] = self.firebase_service.get_timestamp()
            data['updated_at'] = data['created_at']
            data['profile_complete'] = True
            
            # Create applicant document
            doc_ref = self.firebase_service.create_document('applicants', None, data)
            
            return {
                'message': 'Applicant profile created successfully',
                'applicant_id': doc_ref.id
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating applicant: {str(e)}")
            return {'error': 'Failed to create applicant'}, 500

class CVParseAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.gemini_service = GeminiService()
        self.file_handler = FileHandler()
    
    def post(self):
        """Parse uploaded CV and extract information"""
        try:
            # Check if file was uploaded
            if 'cv_file' not in request.files:
                return {'error': 'No CV file uploaded'}, 400
            
            file = request.files['cv_file']
            
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Validate file type
            if not self.file_handler.allowed_file(file.filename):
                return {'error': 'File type not allowed. Please upload PDF, DOC, or DOCX files'}, 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_path = self.file_handler.save_file(file, filename)
            
            try:
                # Extract text from file
                text_content = self.file_handler.extract_text(file_path)
                
                # Parse CV using Gemini
                parsed_data = self.gemini_service.parse_cv(text_content)
                
                # Clean up uploaded file
                self.file_handler.cleanup_file(file_path)
                
                return {
                    'message': 'CV parsed successfully',
                    'parsed_data': parsed_data,
                    'confidence_score': parsed_data.get('confidence_score', 0.8),
                    'missing_fields': self._identify_missing_fields(parsed_data)
                }, 200
                
            except Exception as parse_error:
                # Clean up file on error
                self.file_handler.cleanup_file(file_path)
                raise parse_error
                
        except Exception as e:
            logger.error(f"CV parsing error: {str(e)}")
            return {'error': 'Failed to parse CV', 'details': str(e)}, 500
    
    def _identify_missing_fields(self, parsed_data):
        """Identify missing or incomplete fields in parsed data"""
        required_fields = [
            'name', 'email', 'phone', 'location', 'education', 
            'experience', 'skills', 'category'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in parsed_data or not parsed_data[field]:
                missing_fields.append(field)
        
        return missing_fields
