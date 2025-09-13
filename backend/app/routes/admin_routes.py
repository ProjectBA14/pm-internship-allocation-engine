"""
Admin Dashboard API Routes
Handles admin analytics, reporting, and dashboard functionality
"""

from flask import request, jsonify
from flask_restful import Resource
import logging
from collections import defaultdict
from datetime import datetime, timedelta

from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class AdminDashboardAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self):
        """Get admin dashboard data and statistics"""
        try:
            # Get overall statistics
            stats = self._get_overall_statistics()
            
            # Get recent activity
            recent_activity = self._get_recent_activity()
            
            # Get allocation status
            allocation_status = self._get_allocation_status()
            
            # Get diversity metrics
            diversity_metrics = self._get_diversity_metrics()
            
            return {
                'statistics': stats,
                'recent_activity': recent_activity,
                'allocation_status': allocation_status,
                'diversity_metrics': diversity_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            logger.error(f"Admin dashboard error: {str(e)}")
            return {'error': 'Failed to load dashboard data'}, 500
    
    def _get_overall_statistics(self):
        """Get overall system statistics"""
        try:
            # Count documents in each collection
            applicants = self.firebase_service.query_documents('applicants', limit=1000)
            internships = self.firebase_service.query_documents('internships', limit=100)
            matches = self.firebase_service.query_documents('matches', limit=500)
            allocations = self.firebase_service.query_documents('allocation_items', limit=500)
            
            # Calculate statistics
            total_applicants = len(applicants)
            complete_profiles = len([a for a in applicants if a.get('profile_complete')])
            active_internships = len([i for i in internships if i.get('active')])
            total_capacity = sum(i.get('capacity', 1) for i in internships if i.get('active'))
            total_allocated = len(allocations)
            
            return {
                'total_applicants': total_applicants,
                'complete_profiles': complete_profiles,
                'profile_completion_rate': (complete_profiles / total_applicants * 100) if total_applicants > 0 else 0,
                'active_internships': active_internships,
                'total_capacity': total_capacity,
                'total_allocated': total_allocated,
                'allocation_rate': (total_allocated / total_capacity * 100) if total_capacity > 0 else 0,
                'total_matches': len(matches)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def _get_recent_activity(self):
        """Get recent system activity"""
        try:
            activities = []
            
            # Recent applicant registrations
            recent_applicants = self.firebase_service.query_documents('applicants', limit=5)
            for applicant in recent_applicants:
                if applicant.get('created_at'):
                    activities.append({
                        'type': 'applicant_registration',
                        'message': f"New applicant registered: {applicant.get('name', 'Unknown')}",
                        'timestamp': applicant.get('created_at'),
                        'data': {'applicant_id': applicant.get('id')}
                    })
            
            # Recent internship postings
            recent_internships = self.firebase_service.query_documents('internships', limit=5)
            for internship in recent_internships:
                if internship.get('created_at'):
                    activities.append({
                        'type': 'internship_posted',
                        'message': f"New internship posted: {internship.get('title', 'Unknown')} at {internship.get('company', 'Unknown')}",
                        'timestamp': internship.get('created_at'),
                        'data': {'internship_id': internship.get('id')}
                    })
            
            # Recent allocations
            recent_allocations = self.firebase_service.query_documents('allocation_items', limit=10)
            for allocation in recent_allocations:
                if allocation.get('timestamp'):
                    activities.append({
                        'type': 'allocation_completed',
                        'message': f"Candidate allocated: {allocation.get('candidate_name', 'Unknown')} → {allocation.get('internship_title', 'Unknown')}",
                        'timestamp': allocation.get('timestamp'),
                        'data': {
                            'candidate_id': allocation.get('candidate_id'),
                            'internship_id': allocation.get('internship_id')
                        }
                    })
            
            # Sort by timestamp (most recent first)
            activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return activities[:20]  # Return top 20 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            return []
    
    def _get_allocation_status(self):
        """Get current allocation status"""
        try:
            # Get latest allocation batch
            recent_allocations = self.firebase_service.query_documents('allocations', limit=1)
            
            if not recent_allocations:
                return {
                    'status': 'no_allocations',
                    'message': 'No allocations have been performed yet'
                }
            
            latest_allocation = recent_allocations[0]
            
            return {
                'status': 'completed',
                'allocation_id': latest_allocation.get('allocation_id'),
                'timestamp': latest_allocation.get('timestamp'),
                'total_allocated': latest_allocation.get('total_allocated', 0),
                'diversity_report': latest_allocation.get('diversity_report', {}),
                'quota_fulfillment': latest_allocation.get('quota_fulfillment', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting allocation status: {str(e)}")
            return {'status': 'error', 'message': 'Unable to fetch allocation status'}
    
    def _get_diversity_metrics(self):
        """Get diversity and representation metrics"""
        try:
            # Get all applicants
            applicants = self.firebase_service.query_documents('applicants', limit=1000)
            
            # Get allocation items
            allocations = self.firebase_service.query_documents('allocation_items', limit=500)
            
            # Calculate applicant diversity
            applicant_metrics = self._calculate_diversity_breakdown(applicants, 'applicants')
            
            # Calculate allocation diversity  
            allocation_metrics = self._calculate_diversity_breakdown(allocations, 'allocations')
            
            return {
                'applicant_pool': applicant_metrics,
                'allocated_candidates': allocation_metrics,
                'representation_analysis': self._compare_representation(applicant_metrics, allocation_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting diversity metrics: {str(e)}")
            return {}
    
    def _calculate_diversity_breakdown(self, data, data_type):
        """Calculate diversity breakdown for given data"""
        if not data:
            return {}
        
        total = len(data)
        
        # Category breakdown
        categories = defaultdict(int)
        locations = defaultdict(int)
        rural_count = 0
        
        for item in data:
            # Category analysis
            if data_type == 'applicants':
                category = item.get('category', 'Unknown')
                location = item.get('location', 'Unknown')
                rural_background = item.get('rural_background', False)
            else:  # allocations
                category = item.get('category', 'Unknown')  # This would be quota category
                location = item.get('location', 'Unknown')
                rural_background = item.get('rural_background', False)
            
            categories[category] += 1
            locations[location] += 1
            
            if rural_background:
                rural_count += 1
        
        # Convert to percentages
        category_percentages = {cat: (count/total)*100 for cat, count in categories.items()}
        location_percentages = {loc: (count/total)*100 for loc, count in locations.items()}
        
        return {
            'total': total,
            'categories': dict(categories),
            'category_percentages': category_percentages,
            'locations': dict(locations),
            'location_percentages': location_percentages,
            'rural_representation': {
                'count': rural_count,
                'percentage': (rural_count/total)*100 if total > 0 else 0
            }
        }
    
    def _compare_representation(self, applicant_metrics, allocation_metrics):
        """Compare representation between applicant pool and allocations"""
        if not applicant_metrics or not allocation_metrics:
            return {}
        
        analysis = {}
        
        # Compare category representation
        applicant_categories = applicant_metrics.get('category_percentages', {})
        allocation_categories = allocation_metrics.get('category_percentages', {})
        
        category_analysis = {}
        for category in set(list(applicant_categories.keys()) + list(allocation_categories.keys())):
            applicant_pct = applicant_categories.get(category, 0)
            allocation_pct = allocation_categories.get(category, 0)
            
            category_analysis[category] = {
                'applicant_percentage': applicant_pct,
                'allocation_percentage': allocation_pct,
                'difference': allocation_pct - applicant_pct,
                'representation_ratio': allocation_pct / applicant_pct if applicant_pct > 0 else 0
            }
        
        # Compare rural representation
        applicant_rural = applicant_metrics.get('rural_representation', {}).get('percentage', 0)
        allocation_rural = allocation_metrics.get('rural_representation', {}).get('percentage', 0)
        
        rural_analysis = {
            'applicant_percentage': applicant_rural,
            'allocation_percentage': allocation_rural,
            'difference': allocation_rural - applicant_rural,
            'representation_ratio': allocation_rural / applicant_rural if applicant_rural > 0 else 0
        }
        
        return {
            'category_analysis': category_analysis,
            'rural_analysis': rural_analysis
        }

class AdminAnalyticsAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
    
    def get(self):
        """Get detailed analytics and reports"""
        try:
            analytics_type = request.args.get('type', 'overview')
            
            if analytics_type == 'matching':
                return self._get_matching_analytics()
            elif analytics_type == 'allocation':
                return self._get_allocation_analytics()
            elif analytics_type == 'diversity':
                return self._get_diversity_analytics()
            elif analytics_type == 'performance':
                return self._get_performance_analytics()
            else:
                return self._get_overview_analytics()
                
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return {'error': 'Failed to generate analytics'}, 500
    
    def _get_overview_analytics(self):
        """Get overview analytics"""
        return {
            'message': 'Analytics overview',
            'available_reports': [
                'matching', 'allocation', 'diversity', 'performance'
            ]
        }
    
    def _get_matching_analytics(self):
        """Get matching performance analytics"""
        matches = self.firebase_service.query_documents('matches', limit=1000)
        
        if not matches:
            return {'message': 'No matching data available'}
        
        # Analyze match scores
        scores = [match.get('score', 0) for match in matches]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        score_distribution = {
            'high_score': len([s for s in scores if s >= 0.7]),
            'medium_score': len([s for s in scores if 0.4 <= s < 0.7]),
            'low_score': len([s for s in scores if s < 0.4])
        }
        
        return {
            'total_matches': len(matches),
            'average_score': avg_score,
            'score_distribution': score_distribution,
            'high_quality_matches': score_distribution['high_score']
        }
    
    def _get_allocation_analytics(self):
        """Get allocation analytics"""
        allocations = self.firebase_service.query_documents('allocation_items', limit=1000)
        
        if not allocations:
            return {'message': 'No allocation data available'}
        
        # Analyze allocations
        categories = defaultdict(int)
        allocation_types = defaultdict(int)
        
        for allocation in allocations:
            categories[allocation.get('category', 'Unknown')] += 1
            allocation_types[allocation.get('allocation_type', 'Unknown')] += 1
        
        return {
            'total_allocations': len(allocations),
            'category_distribution': dict(categories),
            'allocation_type_distribution': dict(allocation_types)
        }
    
    def _get_diversity_analytics(self):
        """Get detailed diversity analytics"""
        return {
            'message': 'Diversity analytics - detailed implementation would go here',
            'features': [
                'Category-wise representation',
                'Rural vs Urban distribution',
                'Gender diversity metrics',
                'Regional representation'
            ]
        }
    
    def _get_performance_analytics(self):
        """Get system performance analytics"""
        return {
            'message': 'Performance analytics - detailed implementation would go here',
            'metrics': [
                'API response times',
                'Matching algorithm performance',
                'Database query optimization',
                'User engagement metrics'
            ]
        }
