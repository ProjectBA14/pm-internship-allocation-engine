"""
API Routes Registration
Centralized route registration for all API endpoints
"""

from .auth_routes import AuthAPI
from .applicant_routes import ApplicantAPI, CVParseAPI, ApplicantListAPI
from .internship_routes import InternshipAPI, InternshipListAPI
from .matching_routes import MatchingAPI, AllocationAPI
from .admin_routes import AdminDashboardAPI, AdminAnalyticsAPI
from .enhanced_internship_routes import SmartInternshipSearchAPI, InternshipDetailsAPI, RecommendedInternshipsAPI
from .cv_integrated_routes import CVIntegratedInternshipSearchAPI, PersonalizedRecommendationsAPI, CVMatchAnalysisAPI, LiveInternshipFeedAPI

def register_routes(api):
    """
    Register all API routes with Flask-RESTful
    
    Args:
        api: Flask-RESTful Api instance
    """
    
    # Authentication routes
    api.add_resource(AuthAPI, '/api/auth/<string:action>')
    
    # Applicant management routes
    api.add_resource(ApplicantAPI, '/api/applicants/<string:applicant_id>')
    api.add_resource(ApplicantListAPI, '/api/applicants')
    api.add_resource(CVParseAPI, '/api/cv-parse')
    
    # Internship management routes  
    api.add_resource(InternshipAPI, '/api/internships/<string:internship_id>')
    api.add_resource(InternshipListAPI, '/api/internships')
    
    # Matching and allocation routes
    api.add_resource(MatchingAPI, '/api/matching')
    api.add_resource(AllocationAPI, '/api/allocation')
    
    # Admin dashboard routes
    api.add_resource(AdminDashboardAPI, '/api/admin/dashboard')
    api.add_resource(AdminAnalyticsAPI, '/api/admin/analytics')
    
    # Enhanced internship routes with live scraping and AI matching
    api.add_resource(SmartInternshipSearchAPI, '/api/smart-internships/search')
    api.add_resource(InternshipDetailsAPI, '/api/smart-internships/<string:internship_id>')
    api.add_resource(RecommendedInternshipsAPI, '/api/smart-internships/recommendations')
    
    # CV-integrated internship matching routes
    api.add_resource(CVIntegratedInternshipSearchAPI, '/api/cv-integrated/search')
    api.add_resource(PersonalizedRecommendationsAPI, '/api/cv-integrated/recommendations')
    api.add_resource(CVMatchAnalysisAPI, '/api/cv-integrated/match-analysis')
    api.add_resource(LiveInternshipFeedAPI, '/api/cv-integrated/live-feed')
