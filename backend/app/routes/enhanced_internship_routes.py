"""
Enhanced Internship Routes with Live Scraping and Intelligent Matching
"""

from flask import request, jsonify
from flask_restful import Resource
import logging

from services.firebase_service import FirebaseService
from services.internship_scraper_service import InternshipScraperService

logger = logging.getLogger(__name__)

class SmartInternshipSearchAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.scraper_service = InternshipScraperService()
    
    def post(self):
        """
        Smart internship search with live scraping and AI matching
        
        Request body:
        {
            "candidate_profile": {...},  // User's profile from CV parsing
            "categories": ["Software Development", "Data Science"],
            "locations": ["Bangalore", "Mumbai"],
            "salary_min": 15000,
            "remote_preferred": true,
            "limit": 20
        }
        """
        try:
            data = request.get_json()
            
            # Extract search parameters
            candidate_profile = data.get('candidate_profile', {})
            categories = data.get('categories', [])
            locations = data.get('locations', [])
            salary_min = data.get('salary_min', 0)
            remote_preferred = data.get('remote_preferred', False)
            limit = data.get('limit', 20)
            
            logger.info(f"Smart search request: categories={categories}, locations={locations}")
            
            # Scrape live internships
            live_internships = self.scraper_service.scrape_live_internships(
                categories=categories,
                locations=locations,
                limit=limit * 2  # Get more to filter and rank
            )
            
            # Calculate match scores for each internship
            matched_internships = []
            for internship in live_internships:
                # Calculate detailed match score
                match_analysis = self.scraper_service.calculate_match_score(
                    candidate_profile, internship
                )
                
                # Add match analysis to internship data
                internship['match_analysis'] = match_analysis
                internship['match_score'] = match_analysis.get('overall_score', 0)
                internship['match_percentage'] = match_analysis.get('percentage', 0)
                internship['compatibility_level'] = match_analysis.get('compatibility_level', 'Unknown')
                
                # Apply filters
                if salary_min > 0 and internship.get('salary_max', 0) < salary_min:
                    continue
                    
                if remote_preferred and not internship.get('remote_option', False):
                    # Lower priority but don't exclude
                    internship['match_score'] *= 0.9
                
                matched_internships.append(internship)
            
            # Sort by match score (descending)
            matched_internships.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # Limit final results
            final_results = matched_internships[:limit]
            
            # Generate search summary
            search_summary = {
                'total_scraped': len(live_internships),
                'total_matched': len(matched_internships),
                'returned': len(final_results),
                'avg_match_score': sum(i.get('match_score', 0) for i in final_results) / len(final_results) if final_results else 0,
                'top_categories': self._get_top_categories(final_results),
                'salary_range': self._get_salary_range_summary(final_results),
                'location_distribution': self._get_location_distribution(final_results)
            }
            
            return {
                'message': 'Smart internship search completed',
                'search_summary': search_summary,
                'internships': final_results
            }, 200
            
        except Exception as e:
            logger.error(f"Smart search error: {str(e)}")
            return {
                'error': 'Failed to perform smart search',
                'details': str(e)
            }, 500
    
    def _get_top_categories(self, internships):
        """Get top categories from results"""
        categories = {}
        for internship in internships:
            cat = internship.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _get_salary_range_summary(self, internships):
        """Get salary range summary"""
        if not internships:
            return {}
        
        salaries = []
        for internship in internships:
            if internship.get('salary_max'):
                salaries.append(internship['salary_max'])
        
        if not salaries:
            return {}
        
        return {
            'min': min(salaries),
            'max': max(salaries),
            'avg': sum(salaries) // len(salaries)
        }
    
    def _get_location_distribution(self, internships):
        """Get location distribution"""
        locations = {}
        for internship in internships:
            loc = internship.get('location', 'Unknown')
            city = loc.split(',')[0].strip()  # Extract city name
            locations[city] = locations.get(city, 0) + 1
        return sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]

class InternshipDetailsAPI(Resource):
    def __init__(self):
        self.scraper_service = InternshipScraperService()
    
    def get(self, internship_id):
        """Get detailed information about a specific internship"""
        try:
            # In a real implementation, this would fetch from database or re-scrape
            # For demo, return enhanced mock data
            
            internship_details = {
                'id': internship_id,
                'title': 'AI/ML Engineering Internship',
                'company': 'InnovateTech AI',
                'location': 'Hyderabad, Telangana',
                'category': 'Artificial Intelligence',
                'salary': '₹25,000 - ₹40,000/month',
                'salary_min': 25000,
                'salary_max': 40000,
                'duration': '6 months',
                'description': '''
                <h3>About the Role</h3>
                <p>Join our cutting-edge AI/ML team and work on revolutionary projects that will shape the future of artificial intelligence. You'll be involved in developing production-ready machine learning models, contributing to open-source projects, and collaborating with top-tier engineers and researchers.</p>
                
                <h3>What You'll Do</h3>
                <ul>
                    <li>Develop and deploy machine learning models using TensorFlow and PyTorch</li>
                    <li>Work on computer vision and natural language processing projects</li>
                    <li>Participate in research and development of new AI algorithms</li>
                    <li>Collaborate with cross-functional teams on product development</li>
                    <li>Contribute to technical documentation and best practices</li>
                </ul>
                
                <h3>Learning Opportunities</h3>
                <ul>
                    <li>Mentorship from industry experts and PhD researchers</li>
                    <li>Access to latest AI/ML tools and cloud computing resources</li>
                    <li>Opportunity to publish research papers and present at conferences</li>
                    <li>Hands-on experience with production ML systems</li>
                </ul>
                ''',
                'requirements': [
                    'Strong Python programming skills (2+ years)',
                    'Experience with TensorFlow or PyTorch',
                    'Understanding of ML algorithms and deep learning',
                    'Experience with data preprocessing and feature engineering',
                    'Knowledge of computer vision or NLP (preferred)',
                    'Strong mathematical and statistical background'
                ],
                'skills_required': ['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'Computer Vision', 'NumPy', 'Pandas'],
                'nice_to_have': ['MLOps', 'Docker', 'Kubernetes', 'AWS/GCP', 'Research Experience'],
                'apply_link': 'https://innovatetech.ai/careers/ai-ml-internship',
                'posted_date': '2025-01-11',
                'deadline': '2025-02-25',
                'source': 'Company Career Page',
                'company_info': {
                    'name': 'InnovateTech AI',
                    'logo': 'https://innovatetech.ai/logo.png',
                    'size': '100-500 employees',
                    'founded': '2019',
                    'industry': 'Artificial Intelligence',
                    'website': 'https://innovatetech.ai',
                    'description': 'Leading AI research and development company focused on computer vision, NLP, and autonomous systems.',
                    'rating': 4.8,
                    'reviews_count': 127,
                    'culture_highlights': [
                        'Innovation-driven environment',
                        'Flexible working hours',
                        'Learning and development focus',
                        'Diverse and inclusive team'
                    ]
                },
                'job_type': 'Internship',
                'remote_option': True,
                'work_arrangement': 'Hybrid (3 days office, 2 days remote)',
                'perks': [
                    'High stipend (₹25,000 - ₹40,000/month)',
                    'Mentorship by industry experts',
                    'Pre-placement offer (PPO) opportunity',
                    'Conference attendance and networking',
                    'Health insurance coverage',
                    'Learning and development budget',
                    'Free meals and snacks',
                    'Flexible working hours'
                ],
                'application_process': [
                    'Online application with resume',
                    'Technical assessment (coding + ML concepts)',
                    'Technical interview with team lead',
                    'HR interview and cultural fit assessment',
                    'Final decision within 2 weeks'
                ],
                'team_info': {
                    'team_size': 15,
                    'reporting_to': 'Senior ML Engineer',
                    'collaboration_with': ['Data Engineers', 'Product Managers', 'Research Scientists']
                },
                'technologies_used': [
                    'Python', 'TensorFlow', 'PyTorch', 'Docker', 'Kubernetes',
                    'AWS', 'Git', 'Jupyter', 'MLflow', 'Apache Spark'
                ],
                'similar_companies': [
                    'NVIDIA AI', 'OpenAI', 'DeepMind', 'Microsoft Research India'
                ]
            }
            
            return {
                'internship': internship_details,
                'fetched_at': '2025-01-13T10:30:00Z'
            }, 200
            
        except Exception as e:
            logger.error(f"Error fetching internship details: {str(e)}")
            return {
                'error': 'Failed to fetch internship details',
                'details': str(e)
            }, 500

class RecommendedInternshipsAPI(Resource):
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.scraper_service = InternshipScraperService()
    
    def post(self):
        """Get personalized internship recommendations based on candidate profile"""
        try:
            data = request.get_json()
            candidate_profile = data.get('candidate_profile', {})
            
            if not candidate_profile:
                return {'error': 'Candidate profile is required'}, 400
            
            # Get live internships
            live_internships = self.scraper_service.scrape_live_internships(limit=50)
            
            # Calculate match scores and get recommendations
            recommendations = []
            for internship in live_internships:
                match_analysis = self.scraper_service.calculate_match_score(
                    candidate_profile, internship
                )
                
                if match_analysis.get('overall_score', 0) >= 0.4:  # Only good matches
                    internship['match_analysis'] = match_analysis
                    internship['match_score'] = match_analysis.get('overall_score', 0)
                    internship['match_percentage'] = match_analysis.get('percentage', 0)
                    recommendations.append(internship)
            
            # Sort by match score
            recommendations.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # Take top recommendations
            top_recommendations = recommendations[:10]
            
            # Generate insights
            insights = {
                'total_analyzed': len(live_internships),
                'qualified_matches': len(recommendations),
                'top_recommendations': len(top_recommendations),
                'best_match_score': top_recommendations[0].get('match_percentage', 0) if top_recommendations else 0,
                'avg_match_score': sum(r.get('match_score', 0) for r in top_recommendations) / len(top_recommendations) if top_recommendations else 0,
                'categories_matched': list(set(r.get('category') for r in top_recommendations)),
                'skills_in_demand': self._get_skills_in_demand(recommendations),
                'career_advice': self._generate_career_advice(candidate_profile, recommendations)
            }
            
            return {
                'recommendations': top_recommendations,
                'insights': insights,
                'candidate_strengths': candidate_profile.get('key_strengths', []),
                'generated_at': '2025-01-13T10:30:00Z'
            }, 200
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                'error': 'Failed to generate recommendations',
                'details': str(e)
            }, 500
    
    def _get_skills_in_demand(self, internships):
        """Extract most in-demand skills from internships"""
        skill_count = {}
        for internship in internships:
            for skill in internship.get('skills_required', []):
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        # Return top 10 skills
        return sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _generate_career_advice(self, candidate_profile, internships):
        """Generate personalized career advice"""
        advice = []
        
        candidate_skills = set()
        skills_dict = candidate_profile.get('skills', {})
        for skill_list in skills_dict.values():
            if isinstance(skill_list, list):
                candidate_skills.update([s.lower() for s in skill_list])
        
        # Find common missing skills
        missing_skills = {}
        for internship in internships[:5]:  # Top 5 matches
            for skill in internship.get('skills_required', []):
                if skill.lower() not in candidate_skills:
                    missing_skills[skill] = missing_skills.get(skill, 0) + 1
        
        if missing_skills:
            top_missing = sorted(missing_skills.items(), key=lambda x: x[1], reverse=True)[:3]
            advice.append(f"Consider learning these in-demand skills: {', '.join([s[0] for s in top_missing])}")
        
        # Category advice
        candidate_category = candidate_profile.get('category', '').lower()
        category_matches = [i for i in internships if candidate_category in i.get('category', '').lower()]
        
        if len(category_matches) >= 3:
            advice.append(f"Great opportunities in {candidate_category} - you're in a growing field!")
        else:
            advice.append("Consider exploring related fields to increase your opportunities")
        
        return advice
