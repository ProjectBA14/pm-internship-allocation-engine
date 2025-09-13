"""
Company Data Enrichment Service
Provides company ratings, reviews, and additional insights for better matching
"""

import requests
import logging
from typing import Dict, List, Any, Optional
import json
import time

logger = logging.getLogger(__name__)

class CompanyEnrichmentService:
    def __init__(self):
        """Initialize the company enrichment service"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for company data to avoid repeated API calls
        self.company_cache = {}
        
        # Mock Glassdoor-style data for demo purposes
        self.company_database = {
            'Google': {
                'rating': 4.5,
                'reviews_count': 15000,
                'culture_values_rating': 4.6,
                'diversity_inclusion_rating': 4.3,
                'work_life_balance_rating': 4.2,
                'compensation_benefits_rating': 4.7,
                'career_opportunities_rating': 4.4,
                'interview_difficulty': 3.8,
                'ceo_approval': 95,
                'recommend_to_friend': 89,
                'company_size': '100,000+ employees',
                'industry': 'Technology',
                'headquarters': 'Mountain View, CA',
                'founded': 1998,
                'revenue': '$280B+',
                'top_skills': ['Software Engineering', 'Data Analysis', 'Product Management'],
                'recent_reviews': [
                    {'rating': 5, 'title': 'Great learning opportunities', 'pros': 'Excellent mentorship and growth'},
                    {'rating': 4, 'title': 'Innovative environment', 'pros': 'Cutting-edge technology and smart colleagues'},
                    {'rating': 4, 'title': 'Work-life balance', 'pros': 'Flexible hours and remote work options'}
                ]
            },
            'Microsoft': {
                'rating': 4.4,
                'reviews_count': 12000,
                'culture_values_rating': 4.5,
                'diversity_inclusion_rating': 4.4,
                'work_life_balance_rating': 4.3,
                'compensation_benefits_rating': 4.6,
                'career_opportunities_rating': 4.5,
                'interview_difficulty': 3.5,
                'ceo_approval': 93,
                'recommend_to_friend': 87,
                'company_size': '200,000+ employees',
                'industry': 'Technology',
                'headquarters': 'Redmond, WA',
                'founded': 1975,
                'revenue': '$200B+',
                'top_skills': ['C#', 'Azure', 'Software Development'],
                'recent_reviews': [
                    {'rating': 5, 'title': 'Supportive culture', 'pros': 'Great manager support and career growth'},
                    {'rating': 4, 'title': 'Good benefits', 'pros': 'Excellent healthcare and retirement plans'},
                    {'rating': 4, 'title': 'Collaborative environment', 'pros': 'Team-oriented culture'}
                ]
            },
            'Amazon': {
                'rating': 3.9,
                'reviews_count': 18000,
                'culture_values_rating': 3.8,
                'diversity_inclusion_rating': 4.0,
                'work_life_balance_rating': 3.2,
                'compensation_benefits_rating': 4.2,
                'career_opportunities_rating': 4.3,
                'interview_difficulty': 4.2,
                'ceo_approval': 78,
                'recommend_to_friend': 74,
                'company_size': '1,500,000+ employees',
                'industry': 'E-commerce/Technology',
                'headquarters': 'Seattle, WA',
                'founded': 1994,
                'revenue': '$500B+',
                'top_skills': ['AWS', 'Java', 'Leadership Principles'],
                'recent_reviews': [
                    {'rating': 4, 'title': 'Fast-paced learning', 'pros': 'Rapid skill development and ownership'},
                    {'rating': 3, 'title': 'High expectations', 'pros': 'Challenging work but demanding pace'},
                    {'rating': 4, 'title': 'Career growth', 'pros': 'Many internal opportunities'}
                ]
            }
        }
    
    def enrich_company_data(self, company_name: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrich company data with ratings, reviews, and insights
        
        Args:
            company_name: Name of the company
            industry: Industry category for better matching
            
        Returns:
            Dictionary containing enriched company information
        """
        try:
            # Check cache first
            cache_key = company_name.lower()
            if cache_key in self.company_cache:
                logger.info(f"Using cached data for {company_name}")
                return self.company_cache[cache_key]
            
            # Try to get data from mock database first
            company_data = self._get_mock_company_data(company_name)
            
            if not company_data:
                # If not in mock database, try to fetch from web or generate synthetic data
                company_data = self._generate_company_data(company_name, industry)
            
            # Add additional insights
            company_data['internship_insights'] = self._generate_internship_insights(company_data)
            company_data['match_factors'] = self._generate_match_factors(company_data)
            
            # Cache the result
            self.company_cache[cache_key] = company_data
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error enriching company data for {company_name}: {str(e)}")
            return self._get_default_company_data(company_name)
    
    def _get_mock_company_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get company data from mock database"""
        # Try exact match first
        if company_name in self.company_database:
            return self.company_database[company_name].copy()
        
        # Try fuzzy matching
        company_lower = company_name.lower()
        for db_company, data in self.company_database.items():
            if company_lower in db_company.lower() or db_company.lower() in company_lower:
                return data.copy()
        
        return None
    
    def _generate_company_data(self, company_name: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """Generate synthetic company data based on company name and industry"""
        import random
        import hashlib
        
        # Use company name as seed for consistent data generation
        seed = int(hashlib.md5(company_name.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate ratings based on industry patterns
        base_rating = 3.5 + (random.random() * 1.5)  # 3.5 to 5.0
        
        industry_adjustments = {
            'technology': 0.3,
            'finance': 0.1,
            'healthcare': 0.2,
            'consulting': 0.0,
            'startup': -0.2,
            'manufacturing': -0.1
        }
        
        industry_key = industry.lower() if industry else 'general'
        adjustment = industry_adjustments.get(industry_key, 0)
        rating = max(3.0, min(5.0, base_rating + adjustment))
        
        return {
            'rating': round(rating, 1),
            'reviews_count': random.randint(50, 5000),
            'culture_values_rating': round(rating + random.uniform(-0.3, 0.3), 1),
            'diversity_inclusion_rating': round(rating + random.uniform(-0.2, 0.2), 1),
            'work_life_balance_rating': round(rating + random.uniform(-0.4, 0.2), 1),
            'compensation_benefits_rating': round(rating + random.uniform(-0.2, 0.4), 1),
            'career_opportunities_rating': round(rating + random.uniform(-0.1, 0.3), 1),
            'interview_difficulty': round(2.5 + random.random() * 2, 1),
            'ceo_approval': random.randint(60, 95),
            'recommend_to_friend': random.randint(65, 90),
            'company_size': random.choice(['1-50 employees', '51-200 employees', '201-1000 employees', '1000+ employees']),
            'industry': industry or 'General',
            'headquarters': 'India',
            'founded': random.randint(1990, 2020),
            'revenue': random.choice(['$1M-10M', '$10M-50M', '$50M-200M', '$200M+']),
            'top_skills': self._generate_skills_for_industry(industry),
            'recent_reviews': [
                {'rating': random.randint(3, 5), 'title': 'Good experience overall', 'pros': 'Learning opportunities and growth'},
                {'rating': random.randint(3, 5), 'title': 'Decent workplace', 'pros': 'Supportive team environment'},
                {'rating': random.randint(3, 5), 'title': 'Professional growth', 'pros': 'Skill development opportunities'}
            ]
        }
    
    def _generate_skills_for_industry(self, industry: Optional[str]) -> List[str]:
        """Generate relevant skills based on industry"""
        skill_mapping = {
            'technology': ['Programming', 'Software Development', 'Problem Solving', 'System Design'],
            'finance': ['Financial Analysis', 'Excel', 'Risk Management', 'Accounting'],
            'marketing': ['Digital Marketing', 'Analytics', 'Content Creation', 'SEO'],
            'design': ['UI/UX Design', 'Creative Thinking', 'Adobe Suite', 'Prototyping'],
            'data science': ['Python', 'Machine Learning', 'Statistics', 'Data Visualization'],
            'consulting': ['Problem Solving', 'Communication', 'Project Management', 'Analysis']
        }
        
        industry_key = industry.lower() if industry else 'general'
        return skill_mapping.get(industry_key, ['Communication', 'Problem Solving', 'Team Work', 'Leadership'])
    
    def _generate_internship_insights(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights specific to internship experience"""
        rating = company_data.get('rating', 4.0)
        
        return {
            'internship_rating': round(rating - 0.1, 1),  # Slightly lower than overall
            'mentorship_quality': 'High' if rating >= 4.3 else 'Medium' if rating >= 3.8 else 'Basic',
            'learning_opportunities': 'Excellent' if rating >= 4.5 else 'Good' if rating >= 4.0 else 'Average',
            'conversion_rate': f"{min(85, max(15, int(rating * 15)))}%",  # Conversion to full-time
            'intern_satisfaction': f"{min(95, max(60, int(rating * 20)))}%",
            'typical_projects': self._generate_typical_projects(company_data.get('industry', 'General')),
            'perks_for_interns': ['Mentorship program', 'Learning stipend', 'Flexible hours', 'Certificate'],
            'interview_process': self._describe_interview_process(company_data.get('interview_difficulty', 3.0))
        }
    
    def _generate_typical_projects(self, industry: str) -> List[str]:
        """Generate typical internship projects based on industry"""
        project_mapping = {
            'Technology': ['Web application development', 'API integration', 'Database optimization', 'UI/UX improvements'],
            'Finance': ['Financial modeling', 'Risk analysis', 'Process improvement', 'Data analysis'],
            'Marketing': ['Campaign analysis', 'Content creation', 'Social media strategy', 'Market research'],
            'General': ['Process improvement', 'Data analysis', 'Project support', 'Research tasks']
        }
        
        return project_mapping.get(industry, project_mapping['General'])
    
    def _describe_interview_process(self, difficulty: float) -> Dict[str, Any]:
        """Describe interview process based on difficulty"""
        if difficulty >= 4.0:
            return {
                'difficulty_level': 'High',
                'typical_rounds': 4,
                'description': 'Multiple rounds including technical assessment, coding challenges, and panel interviews',
                'preparation_time': '2-3 weeks recommended'
            }
        elif difficulty >= 3.5:
            return {
                'difficulty_level': 'Medium',
                'typical_rounds': 3,
                'description': 'Technical and HR rounds with practical assignments',
                'preparation_time': '1-2 weeks recommended'
            }
        else:
            return {
                'difficulty_level': 'Easy',
                'typical_rounds': 2,
                'description': 'HR screening and basic technical discussion',
                'preparation_time': '3-5 days recommended'
            }
    
    def _generate_match_factors(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate factors that influence candidate matching"""
        rating = company_data.get('rating', 4.0)
        
        return {
            'company_attractiveness': min(10, max(1, int(rating * 2))),
            'growth_potential': 'High' if rating >= 4.3 else 'Medium' if rating >= 3.8 else 'Moderate',
            'culture_fit_importance': 'Critical' if rating >= 4.5 else 'Important' if rating >= 4.0 else 'Moderate',
            'skill_development_score': min(10, max(5, int(rating * 2.1))),
            'networking_opportunities': 'Excellent' if rating >= 4.4 else 'Good' if rating >= 4.0 else 'Average',
            'recommended_for': self._get_candidate_recommendations(company_data)
        }
    
    def _get_candidate_recommendations(self, company_data: Dict[str, Any]) -> List[str]:
        """Get recommendations for what type of candidates should apply"""
        rating = company_data.get('rating', 4.0)
        wlb_rating = company_data.get('work_life_balance_rating', 4.0)
        career_rating = company_data.get('career_opportunities_rating', 4.0)
        
        recommendations = []
        
        if rating >= 4.5:
            recommendations.append('High achievers seeking prestigious experience')
        if career_rating >= 4.3:
            recommendations.append('Students planning long-term career growth')
        if wlb_rating >= 4.2:
            recommendations.append('Candidates valuing work-life balance')
        if company_data.get('compensation_benefits_rating', 4.0) >= 4.3:
            recommendations.append('Students seeking competitive compensation')
        
        if not recommendations:
            recommendations.append('Students seeking general industry experience')
        
        return recommendations
    
    def _get_default_company_data(self, company_name: str) -> Dict[str, Any]:
        """Return default company data when enrichment fails"""
        return {
            'rating': 4.0,
            'reviews_count': 100,
            'culture_values_rating': 4.0,
            'diversity_inclusion_rating': 4.0,
            'work_life_balance_rating': 4.0,
            'compensation_benefits_rating': 4.0,
            'career_opportunities_rating': 4.0,
            'interview_difficulty': 3.0,
            'ceo_approval': 80,
            'recommend_to_friend': 75,
            'company_size': 'Unknown',
            'industry': 'General',
            'headquarters': 'India',
            'founded': 2000,
            'revenue': 'Not disclosed',
            'top_skills': ['Communication', 'Problem Solving', 'Team Work'],
            'recent_reviews': [],
            'internship_insights': {
                'internship_rating': 4.0,
                'mentorship_quality': 'Medium',
                'learning_opportunities': 'Good',
                'conversion_rate': '60%',
                'intern_satisfaction': '80%',
                'typical_projects': ['General projects', 'Learning assignments'],
                'perks_for_interns': ['Certificate', 'Experience'],
                'interview_process': {
                    'difficulty_level': 'Medium',
                    'typical_rounds': 2,
                    'description': 'Standard interview process',
                    'preparation_time': '1 week recommended'
                }
            },
            'match_factors': {
                'company_attractiveness': 8,
                'growth_potential': 'Medium',
                'culture_fit_importance': 'Important',
                'skill_development_score': 8,
                'networking_opportunities': 'Good',
                'recommended_for': ['Students seeking industry experience']
            }
        }
    
    def get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """Get insights about specific industry for internships"""
        industry_data = {
            'Technology': {
                'avg_rating': 4.3,
                'growth_rate': 'Very High',
                'skill_demand': ['Programming', 'AI/ML', 'Cloud Computing'],
                'salary_range': '₹15,000 - ₹40,000/month',
                'job_security': 'Excellent',
                'remote_friendly': True
            },
            'Finance': {
                'avg_rating': 4.1,
                'growth_rate': 'Steady',
                'skill_demand': ['Financial Analysis', 'Risk Management', 'Fintech'],
                'salary_range': '₹20,000 - ₹35,000/month',
                'job_security': 'Very Good',
                'remote_friendly': False
            },
            'Marketing': {
                'avg_rating': 3.9,
                'growth_rate': 'High',
                'skill_demand': ['Digital Marketing', 'Analytics', 'Content Strategy'],
                'salary_range': '₹12,000 - ₹25,000/month',
                'job_security': 'Good',
                'remote_friendly': True
            }
        }
        
        return industry_data.get(industry, {
            'avg_rating': 4.0,
            'growth_rate': 'Moderate',
            'skill_demand': ['Communication', 'Problem Solving'],
            'salary_range': '₹10,000 - ₹20,000/month',
            'job_security': 'Good',
            'remote_friendly': False
        })
