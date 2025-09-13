"""
Internship Management API Routes
Handles internship posting, management, and querying
"""

from flask import request, jsonify
from flask_restful import Resource
import logging

from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class InternshipAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self, internship_id):
        """Get internship details by ID"""
        try:
            internship = self.firebase_service.get_document('internships', internship_id)
            if not internship:
                return {'error': 'Internship not found'}, 404
            
            return {'internship': internship}, 200
            
        except Exception as e:
            logger.error(f"Error retrieving internship: {str(e)}")
            return {'error': 'Failed to retrieve internship'}, 500
    
    def put(self, internship_id):
        """Update internship details"""
        try:
            data = request.get_json()
            
            # Update timestamp
            data['updated_at'] = self.firebase_service.get_timestamp()
            
            # Update document
            self.firebase_service.update_document('internships', internship_id, data)
            
            return {'message': 'Internship updated successfully'}, 200
            
        except Exception as e:
            logger.error(f"Error updating internship: {str(e)}")
            return {'error': 'Failed to update internship'}, 500
    
    def delete(self, internship_id):
        """Delete internship"""
        try:
            self.firebase_service.delete_document('internships', internship_id)
            return {'message': 'Internship deleted successfully'}, 200
            
        except Exception as e:
            logger.error(f"Error deleting internship: {str(e)}")
            return {'error': 'Failed to delete internship'}, 500

class InternshipListAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self):
        """Get list of internships with filtering"""
        try:
            # Get query parameters
            category = request.args.get('category')
            location = request.args.get('location')
            company = request.args.get('company')
            active = request.args.get('active', 'true').lower() == 'true'
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # Build query
            query = self.firebase_service.get_collection('internships')
            
            # Apply filters
            if category:
                query = query.where('category', '==', category)
            if location:
                query = query.where('location', '==', location)
            if company:
                query = query.where('company', '==', company)
            if active:
                query = query.where('active', '==', True)
            
            # Execute query
            internships = []
            docs = query.limit(per_page).offset((page - 1) * per_page).get()
            
            for doc in docs:
                internship_data = doc.to_dict()
                internship_data['id'] = doc.id
                internships.append(internship_data)
            
            return {
                'internships': internships,
                'page': page,
                'per_page': per_page,
                'total': len(internships)
            }, 200
            
        except Exception as e:
            logger.error(f"Error retrieving internships: {str(e)}")
            return {'error': 'Failed to retrieve internships'}, 500
    
    def post(self):
        """Create new internship posting"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'company', 'location', 'category', 'description']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Set defaults
            data.setdefault('capacity', 1)
            data.setdefault('active', True)
            data.setdefault('skills_required', [])
            data.setdefault('requirements', [])
            data.setdefault('duration', '3 months')
            data.setdefault('stipend', 'As per company policy')
            
            # Add metadata
            data['created_at'] = self.firebase_service.get_timestamp()
            data['updated_at'] = data['created_at']
            data['posted_by'] = 'admin'  # This should come from auth context
            
            # Create internship document
            doc_ref = self.firebase_service.create_document('internships', None, data)
            
            return {
                'message': 'Internship posted successfully',
                'internship_id': doc_ref.id
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating internship: {str(e)}")
            return {'error': 'Failed to create internship'}, 500
