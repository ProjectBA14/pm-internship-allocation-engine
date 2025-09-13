"""
Matching and Allocation API Routes
Handles AI-powered matching and final allocation with affirmative action
"""

from flask import request, jsonify
from flask_restful import Resource
import logging

from services.firebase_service import FirebaseService
from services.matching_service import MatchingService
from services.affirmative_action_service import AffirmativeActionService

logger = logging.getLogger(__name__)

class MatchingAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.matching_service = MatchingService()
    
    def post(self):
        """Perform AI-powered candidate-internship matching"""
        try:
            data = request.get_json()
            
            # Get candidates and internships for matching
            candidate_ids = data.get('candidate_ids', [])
            internship_ids = data.get('internship_ids', [])
            
            # If no specific IDs provided, match all active candidates/internships
            if not candidate_ids:
                candidates = self.firebase_service.query_documents('applicants', 
                    filters=[('profile_complete', '==', True)], limit=100)
            else:
                candidates = []
                for candidate_id in candidate_ids:
                    candidate = self.firebase_service.get_document('applicants', candidate_id)
                    if candidate:
                        candidates.append(candidate)
            
            if not internship_ids:
                internships = self.firebase_service.query_documents('internships',
                    filters=[('active', '==', True)], limit=50)
            else:
                internships = []
                for internship_id in internship_ids:
                    internship = self.firebase_service.get_document('internships', internship_id)
                    if internship:
                        internships.append(internship)
            
            if not candidates or not internships:
                return {'error': 'No candidates or internships found for matching'}, 400
            
            logger.info(f"Starting matching: {len(candidates)} candidates × {len(internships)} internships")
            
            # Perform batch matching
            matches = self.matching_service.batch_match_candidates(candidates, internships)
            
            # Store matches in database
            match_batch_id = self._store_matches(matches)
            
            # Return top matches and summary
            top_matches = matches[:50]  # Return top 50 matches
            
            return {
                'message': 'Matching completed successfully',
                'match_batch_id': match_batch_id,
                'total_matches': len(matches),
                'top_matches': top_matches,
                'summary': {
                    'candidates_processed': len(candidates),
                    'internships_processed': len(internships),
                    'total_combinations': len(candidates) * len(internships),
                    'viable_matches': len([m for m in matches if m.get('score', 0) > 0.3])
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Matching error: {str(e)}")
            return {'error': 'Failed to perform matching', 'details': str(e)}, 500
    
    def get(self):
        """Get recent matching results"""
        try:
            # Get recent match results
            matches = self.firebase_service.query_documents('matches', 
                limit=100)
            
            # Group by batch ID if available
            match_batches = {}
            for match in matches:
                batch_id = match.get('batch_id', 'unknown')
                if batch_id not in match_batches:
                    match_batches[batch_id] = []
                match_batches[batch_id].append(match)
            
            return {
                'match_batches': match_batches,
                'total_matches': len(matches)
            }, 200
            
        except Exception as e:
            logger.error(f"Error retrieving matches: {str(e)}")
            return {'error': 'Failed to retrieve matches'}, 500
    
    def _store_matches(self, matches):
        """Store match results in database"""
        try:
            import uuid
            batch_id = str(uuid.uuid4())
            
            # Prepare batch operations
            batch_operations = []
            for i, match in enumerate(matches):
                match_id = f"{batch_id}_{i}"
                match_data = match.copy()
                match_data['batch_id'] = batch_id
                match_data['match_id'] = match_id
                
                batch_operations.append({
                    'type': 'set',
                    'collection': 'matches',
                    'document_id': match_id,
                    'data': match_data
                })
            
            # Execute batch write
            self.firebase_service.batch_write(batch_operations)
            
            logger.info(f"Stored {len(matches)} matches with batch ID: {batch_id}")
            return batch_id
            
        except Exception as e:
            logger.error(f"Error storing matches: {str(e)}")
            raise

class AllocationAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.affirmative_action_service = AffirmativeActionService()
    
    def post(self):
        """Perform final allocation with affirmative action"""
        try:
            data = request.get_json()
            
            # Get match batch ID or use latest matches
            batch_id = data.get('batch_id')
            
            if batch_id:
                matches = self.firebase_service.query_documents('matches',
                    filters=[('batch_id', '==', batch_id)], limit=1000)
            else:
                # Use latest matches
                matches = self.firebase_service.query_documents('matches',
                    limit=500)
            
            if not matches:
                return {'error': 'No matches found for allocation'}, 400
            
            # Get internship details for capacity information
            internship_ids = list(set(match.get('internship_id') for match in matches))
            internships = []
            for internship_id in internship_ids:
                internship = self.firebase_service.get_document('internships', internship_id)
                if internship:
                    internships.append(internship)
            
            logger.info(f"Starting allocation: {len(matches)} matches, {len(internships)} internships")
            
            # Apply affirmative action and create final allocations
            allocation_result = self.affirmative_action_service.apply_affirmative_action(
                matches, internships
            )
            
            # Store allocation results
            allocation_id = self._store_allocations(allocation_result)
            
            return {
                'message': 'Allocation completed successfully',
                'allocation_id': allocation_id,
                'total_allocated': len(allocation_result['final_allocations']),
                'diversity_report': allocation_result['diversity_report'],
                'quota_fulfillment': allocation_result['quota_fulfillment'],
                'allocation_summary': allocation_result['allocation_summary']
            }, 200
            
        except Exception as e:
            logger.error(f"Allocation error: {str(e)}")
            return {'error': 'Failed to perform allocation', 'details': str(e)}, 500
    
    def get(self):
        """Get allocation results and analytics"""
        try:
            allocation_id = request.args.get('allocation_id')
            
            if allocation_id:
                # Get specific allocation
                allocation = self.firebase_service.get_document('allocations', allocation_id)
                if not allocation:
                    return {'error': 'Allocation not found'}, 404
                
                return {'allocation': allocation}, 200
            else:
                # Get recent allocations
                allocations = self.firebase_service.query_documents('allocations', 
                    limit=10)
                
                return {
                    'recent_allocations': allocations,
                    'total': len(allocations)
                }, 200
                
        except Exception as e:
            logger.error(f"Error retrieving allocations: {str(e)}")
            return {'error': 'Failed to retrieve allocations'}, 500
    
    def _store_allocations(self, allocation_result):
        """Store allocation results in database"""
        try:
            import uuid
            allocation_id = str(uuid.uuid4())
            
            # Store main allocation document
            allocation_data = {
                'allocation_id': allocation_id,
                'timestamp': allocation_result['timestamp'],
                'total_allocated': len(allocation_result['final_allocations']),
                'diversity_report': allocation_result['diversity_report'],
                'quota_fulfillment': allocation_result['quota_fulfillment'],
                'allocation_summary': allocation_result['allocation_summary']
            }
            
            self.firebase_service.create_document('allocations', allocation_id, allocation_data)
            
            # Store individual allocations
            batch_operations = []
            for i, allocation in enumerate(allocation_result['final_allocations']):
                allocation_item_id = f"{allocation_id}_item_{i}"
                allocation_item_data = allocation.copy()
                allocation_item_data['allocation_batch_id'] = allocation_id
                allocation_item_data['item_id'] = allocation_item_id
                
                batch_operations.append({
                    'type': 'set',
                    'collection': 'allocation_items',
                    'document_id': allocation_item_id,
                    'data': allocation_item_data
                })
            
            # Execute batch write
            if batch_operations:
                self.firebase_service.batch_write(batch_operations)
            
            logger.info(f"Stored allocation with ID: {allocation_id}")
            return allocation_id
            
        except Exception as e:
            logger.error(f"Error storing allocations: {str(e)}")
            raise
