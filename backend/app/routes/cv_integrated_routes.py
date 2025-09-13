"""
CV-Integrated Internship Routes
Routes that connect uploaded CV data to internship matching with real web scraping
"""

from flask import request, jsonify
from flask_restful import Resource
import logging
import json

from services.enhanced_internship_service import EnhancedInternshipService
from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

class CVIntegratedInternshipSearchAPI(Resource):
    """Search internships using uploaded CV data for real matching"""
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.enhanced_service = EnhancedInternshipService()
    
    def post(self):
        """
        Search internships using candidate's CV data
        
        Request body:
        {
            "candidate_id": "user123",  // Optional: fetch from Firebase
            "candidate_data": {         // Or provide directly
                "name": "John Doe",
                "skills": {
                    "technical": ["Python", "React", "SQL"],
                    "soft": ["Communication", "Leadership"]
                },
                "experience": [
                    {
                        "title": "Software Developer Intern",
                        "company": "Tech Corp",
                        "description": "Worked on React and Node.js projects"
                    }
                ],
                "education": [
                    {
                        "degree": "B.Tech",
                        "field": "Computer Science",
                        "institution": "ABC University"
                    }
                ],
                "location": "Bangalore, Karnataka",
                "category": "Software Development"
            },
            "search_preferences": {
                "categories": ["Software Development", "Data Science"],
                "locations": ["Bangalore", "Mumbai"],
                "salary_min": 20000,
                "remote_preferred": true
            },
            "limit": 15
        }
        """
        try:
            data = request.get_json()
            
            # Get candidate data
            candidate_data = data.get('candidate_data', {})
            candidate_id = data.get('candidate_id')
            
            # If candidate_id provided, try to fetch from Firebase
            if candidate_id and not candidate_data:
                try:
                    stored_data = self.firebase_service.get_user_data(candidate_id)
                    if stored_data:
                        candidate_data = stored_data.get('profile', {})
                        logger.info(f"Loaded candidate data for {candidate_id}")
                except Exception as e:
                    logger.warning(f"Could not load candidate data: {str(e)}")
            
            if not candidate_data:
                return {
                    'error': 'Candidate data is required',
                    'message': 'Please provide candidate_data or a valid candidate_id'
                }, 400
            
            # Extract search preferences
            search_prefs = data.get('search_preferences', {})
            categories = search_prefs.get('categories', [])
            locations = search_prefs.get('locations', [])
            salary_min = search_prefs.get('salary_min', 0)
            remote_preferred = search_prefs.get('remote_preferred', False)
            limit = data.get('limit', 15)
            
            logger.info(f"CV-integrated search for {candidate_data.get('name', 'candidate')} - skills: {candidate_data.get('skills', {}).get('technical', [])}")
            
            # Use enhanced service for real scraping and matching
            results = self.enhanced_service.search_internships_for_candidate(
                candidate_data=candidate_data,
                categories=categories,
                locations=locations,
                limit=limit
            )
            
            # Apply additional filters
            filtered_internships = []
            for internship in results['internships']:
                # Salary filter
                if salary_min > 0 and internship.get('salary_max', 0) < salary_min:
                    continue
                
                # Remote preference
                if remote_preferred and not internship.get('remote_option', False):
                    # Lower the match score but don't exclude
                    internship['match_score'] *= 0.85
                    internship['match_percentage'] *= 0.85
                
                filtered_internships.append(internship)
            
            # Re-sort after filtering
            filtered_internships.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # Enhanced response with candidate insights
            response = {
                'message': 'CV-integrated internship search completed',
                'candidate_insights': {
                    'name': candidate_data.get('name', 'Unknown'),
                    'top_skills': candidate_data.get('skills', {}).get('technical', [])[:5],
                    'experience_level': len(candidate_data.get('experience', [])),
                    'preferred_category': candidate_data.get('category', 'General'),
                    'location': candidate_data.get('location', 'Flexible')
                },
                'search_results': {
                    'total_found': results['search_summary']['total_found'],
                    'after_filtering': len(filtered_internships),
                    'avg_match_percentage': sum(i.get('match_percentage', 0) for i in filtered_internships) / len(filtered_internships) if filtered_internships else 0,
                    'best_match_percentage': filtered_internships[0].get('match_percentage', 0) if filtered_internships else 0,
                    'excellent_matches': len([i for i in filtered_internships if i.get('match_percentage', 0) >= 80]),
                    'good_matches': len([i for i in filtered_internships if i.get('match_percentage', 0) >= 60])
                },
                'internships': filtered_internships,
                'matching_powered_by': 'Real CV Data + Live Web Scraping'
            }
            
            return response, 200
            
        except Exception as e:
            logger.error(f"CV-integrated search error: {str(e)}")
            return {
                'error': 'Failed to perform CV-integrated search',
                'details': str(e),
                'suggestion': 'Please check your CV data format and try again'
            }, 500

class PersonalizedRecommendationsAPI(Resource):
    """Get personalized recommendations based on uploaded CV"""
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.enhanced_service = EnhancedInternshipService()
    
    def post(self):
        """
        Get personalized recommendations using CV data
        
        Request body:
        {
            "candidate_data": {...},  // CV data
            "recommendation_type": "skills_based",  // or "location_based", "category_based"
            "limit": 10
        }
        """
        try:
            data = request.get_json()
            candidate_data = data.get('candidate_data', {})
            recommendation_type = data.get('recommendation_type', 'skills_based')
            limit = data.get('limit', 10)
            
            if not candidate_data:
                return {'error': 'Candidate data is required'}, 400
            
            # Get recommendations based on type
            if recommendation_type == 'skills_based':
                # Focus on skills matching
                categories = [candidate_data.get('category', 'Software Development')]
                locations = []
            elif recommendation_type == 'location_based':
                # Focus on location matching
                categories = []
                locations = [candidate_data.get('location', 'Remote')]
            else:
                # Balanced approach
                categories = [candidate_data.get('category', '')]
                locations = [candidate_data.get('location', '')]
            
            # Get recommendations
            results = self.enhanced_service.search_internships_for_candidate(
                candidate_data=candidate_data,
                categories=categories,
                locations=locations,
                limit=limit
            )
            
            # Generate insights and advice
            candidate_skills = results['candidate_profile']['skills']
            internships = results['internships']
            
            # Analyze skills gap
            all_required_skills = set()
            for internship in internships[:5]:  # Top 5 matches
                all_required_skills.update(internship.get('skills_required', []))
            
            candidate_skills_lower = [skill.lower() for skill in candidate_skills]
            missing_skills = [skill for skill in all_required_skills if skill.lower() not in candidate_skills_lower]
            
            # Generate career advice
            career_advice = []
            if missing_skills:
                top_missing = list(missing_skills)[:3]
                career_advice.append(f"Consider learning: {', '.join(top_missing)}")
            
            if internships:
                avg_salary = sum(i.get('salary_max', 0) for i in internships) / len(internships)
                career_advice.append(f"Expected salary range: ₹{int(avg_salary*0.8):,} - ₹{int(avg_salary):,}/month")
            
            if recommendation_type == 'skills_based':
                career_advice.append("Recommendations optimized for your technical skills")
            elif recommendation_type == 'location_based':
                career_advice.append("Recommendations focused on your preferred location")
            
            response = {
                'recommendations': internships,
                'recommendation_insights': {
                    'type': recommendation_type,
                    'based_on_skills': candidate_skills,
                    'skills_gap_analysis': {
                        'missing_skills': missing_skills[:5],
                        'skill_match_percentage': sum(i.get('match_analysis', {}).get('breakdown', {}).get('skills_match', {}).get('percentage', 0) for i in internships) / len(internships) if internships else 0
                    },
                    'career_advice': career_advice,
                    'market_insights': {
                        'total_opportunities': len(internships),
                        'avg_match_percentage': sum(i.get('match_percentage', 0) for i in internships) / len(internships) if internships else 0,
                        'top_companies': [i['company'] for i in internships[:3]],
                        'trending_skills': list(all_required_skills)[:5]
                    }
                },
                'powered_by': 'AI + Real CV Analysis + Live Market Data'
            }
            
            return response, 200
            
        except Exception as e:
            logger.error(f"Personalized recommendations error: {str(e)}")
            return {
                'error': 'Failed to generate personalized recommendations',
                'details': str(e)
            }, 500

class CVMatchAnalysisAPI(Resource):
    """Analyze how well a specific internship matches the candidate's CV"""
    
    def __init__(self):
        self.enhanced_service = EnhancedInternshipService()
    
    def post(self):
        """
        Analyze match between CV and specific internship
        
        Request body:
        {
            "candidate_data": {...},
            "internship": {
                "title": "Software Developer Intern",
                "company": "TechCorp",
                "skills_required": ["Python", "React", "SQL"],
                "location": "Bangalore",
                "category": "Software Development",
                "salary_max": 25000
            }
        }
        """
        try:
            data = request.get_json()
            candidate_data = data.get('candidate_data', {})
            internship = data.get('internship', {})
            
            if not candidate_data or not internship:
                return {
                    'error': 'Both candidate_data and internship are required'
                }, 400
            
            # Calculate detailed match analysis
            match_analysis = self.enhanced_service._calculate_real_match_score(candidate_data, internship)
            
            # Extract detailed breakdown
            breakdown = match_analysis.get('breakdown', {})
            
            # Generate specific recommendations
            recommendations = []
            
            # Skills recommendations
            skills_match = breakdown.get('skills_match', {})
            missing_skills = skills_match.get('missing_skills', [])
            if missing_skills:
                recommendations.append({
                    'type': 'skills_improvement',
                    'priority': 'high',
                    'action': f"Learn these required skills: {', '.join(missing_skills[:3])}",
                    'impact': 'Could increase match score by 15-25%'
                })
            
            # Location recommendations
            location_match = breakdown.get('location_match', {})
            if location_match.get('score', 0) < 0.8:
                recommendations.append({
                    'type': 'location_flexibility',
                    'priority': 'medium',
                    'action': 'Consider remote work options or relocation',
                    'impact': 'Could improve location compatibility'
                })
            
            # Experience recommendations
            experience_match = breakdown.get('experience_match', {})
            if experience_match.get('score', 0) < 0.7:
                recommendations.append({
                    'type': 'experience_building',
                    'priority': 'medium',
                    'action': 'Build relevant project experience or take on freelance work',
                    'impact': 'Demonstrates practical application of skills'
                })
            
            response = {
                'match_analysis': match_analysis,
                'detailed_feedback': {
                    'overall_assessment': match_analysis.get('compatibility_level', 'Unknown'),
                    'match_percentage': match_analysis.get('percentage', 0),
                    'strengths': [],
                    'areas_for_improvement': [],
                    'specific_recommendations': recommendations
                },
                'score_breakdown': {
                    'skills': {
                        'score': breakdown.get('skills_match', {}).get('percentage', 0),
                        'matched_skills': breakdown.get('skills_match', {}).get('matched_skills', []),
                        'missing_skills': breakdown.get('skills_match', {}).get('missing_skills', [])
                    },
                    'category': {
                        'score': breakdown.get('category_match', {}).get('percentage', 0),
                        'alignment': 'Perfect' if breakdown.get('category_match', {}).get('score', 0) == 1.0 else 'Partial'
                    },
                    'location': {
                        'score': breakdown.get('location_match', {}).get('percentage', 0),
                        'compatibility': 'High' if breakdown.get('location_match', {}).get('score', 0) >= 0.8 else 'Medium'
                    }
                },
                'application_readiness': {
                    'ready_to_apply': match_analysis.get('percentage', 0) >= 60,
                    'confidence_level': 'High' if match_analysis.get('percentage', 0) >= 75 else 'Medium' if match_analysis.get('percentage', 0) >= 50 else 'Low',
                    'estimated_success_rate': f"{min(match_analysis.get('percentage', 0) + 10, 90):.0f}%"
                }
            }
            
            return response, 200
            
        except Exception as e:
            logger.error(f"CV match analysis error: {str(e)}")
            return {
                'error': 'Failed to analyze CV match',
                'details': str(e)
            }, 500

class LiveInternshipFeedAPI(Resource):
    """Get live internship feed with real-time scraping"""
    
    def __init__(self):
        self.enhanced_service = EnhancedInternshipService()
    
    def get(self):
        """
        Get live internship feed
        Query parameters:
        ?category=software-development&location=bangalore&limit=10
        """
        try:
            # Get query parameters
            category = request.args.get('category', '')
            location = request.args.get('location', '')
            limit = min(int(request.args.get('limit', 20)), 50)  # Max 50
            
            categories = [category] if category else []
            locations = [location] if location else []
            
            # Create dummy candidate data for scraping
            dummy_candidate = {
                'skills': {'technical': ['Python', 'JavaScript', 'SQL']},
                'category': category or 'General',
                'location': location or 'India'
            }
            
            # Get live internships
            results = self.enhanced_service.search_internships_for_candidate(
                candidate_data=dummy_candidate,
                categories=categories,
                locations=locations,
                limit=limit
            )
            
            # Remove match analysis for general feed (not personalized)
            clean_internships = []
            for internship in results['internships']:
                clean_internship = internship.copy()
                # Remove personalized match data
                clean_internship.pop('match_analysis', None)
                clean_internship.pop('match_score', None)
                clean_internship.pop('match_percentage', None)
                clean_internship.pop('compatibility_level', None)
                clean_internships.append(clean_internship)
            
            return {
                'internships': clean_internships,
                'feed_info': {
                    'total_found': len(clean_internships),
                    'category_filter': category or 'All',
                    'location_filter': location or 'All',
                    'last_updated': results['search_summary'].get('generated_at', 'Now'),
                    'data_sources': ['Internshala', 'Indeed', 'Live Web Scraping']
                },
                'note': 'This is a live feed. Upload your CV for personalized match scores!'
            }, 200
            
        except Exception as e:
            logger.error(f"Live feed error: {str(e)}")
            return {
                'error': 'Failed to fetch live internships',
                'details': str(e)
            }, 500
