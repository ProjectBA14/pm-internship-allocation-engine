"""
Enhanced Matching Algorithm Service
Sophisticated matching that considers candidate background, company data, and historical performance
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import math
from datetime import datetime
from .company_enrichment_service import CompanyEnrichmentService

logger = logging.getLogger(__name__)

class EnhancedMatchingService:
    def __init__(self):
        """Initialize the enhanced matching service"""
        self.company_enrichment = CompanyEnrichmentService()
        
        # Weights for different matching factors
        self.matching_weights = {
            'skills_match': 0.35,
            'experience_relevance': 0.20,
            'company_rating': 0.15,
            'location_preference': 0.12,
            'salary_expectation': 0.08,
            'career_goals_alignment': 0.10
        }
        
        # Historical success patterns (would be loaded from database in production)
        self.historical_patterns = {
            'high_gpa_tech_success': 0.85,
            'project_experience_boost': 0.15,
            'location_mismatch_penalty': 0.20,
            'skill_exact_match_bonus': 0.25
        }
    
    def calculate_enhanced_match_score(self, candidate_profile: Dict[str, Any], 
                                     internship: Dict[str, Any],
                                     historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Calculate enhanced match score using multiple factors including company data
        
        Args:
            candidate_profile: Complete candidate information
            internship: Internship with company enrichment data
            historical_data: Historical matching performance data
        
        Returns:
            Comprehensive match analysis with score and recommendations
        """
        try:
            logger.info(f"Computing enhanced match for {internship.get('title')} at {internship.get('company')}")
            
            # Calculate individual match components
            skills_score = self._calculate_skills_match(candidate_profile, internship)
            experience_score = self._calculate_experience_relevance(candidate_profile, internship)
            company_score = self._calculate_company_compatibility(candidate_profile, internship)
            location_score = self._calculate_location_preference(candidate_profile, internship)
            salary_score = self._calculate_salary_alignment(candidate_profile, internship)
            career_score = self._calculate_career_goals_alignment(candidate_profile, internship)
            
            # Apply historical patterns if available
            historical_adjustments = self._apply_historical_patterns(
                candidate_profile, internship, historical_data
            )
            
            # Calculate weighted final score
            base_score = (
                skills_score * self.matching_weights['skills_match'] +
                experience_score * self.matching_weights['experience_relevance'] +
                company_score * self.matching_weights['company_rating'] +
                location_score * self.matching_weights['location_preference'] +
                salary_score * self.matching_weights['salary_expectation'] +
                career_score * self.matching_weights['career_goals_alignment']
            )
            
            # Apply historical adjustments
            final_score = min(1.0, max(0.0, base_score + historical_adjustments))
            
            # Generate detailed breakdown
            match_breakdown = {
                'skills_match': {
                    'score': skills_score,
                    'percentage': round(skills_score * 100, 1),
                    'details': self._get_skills_details(candidate_profile, internship)
                },
                'experience_relevance': {
                    'score': experience_score,
                    'percentage': round(experience_score * 100, 1),
                    'details': self._get_experience_details(candidate_profile, internship)
                },
                'company_compatibility': {
                    'score': company_score,
                    'percentage': round(company_score * 100, 1),
                    'details': self._get_company_details(internship)
                },
                'location_preference': {
                    'score': location_score,
                    'percentage': round(location_score * 100, 1),
                    'details': self._get_location_details(candidate_profile, internship)
                },
                'salary_alignment': {
                    'score': salary_score,
                    'percentage': round(salary_score * 100, 1),
                    'details': self._get_salary_details(candidate_profile, internship)
                },
                'career_alignment': {
                    'score': career_score,
                    'percentage': round(career_score * 100, 1),
                    'details': self._get_career_details(candidate_profile, internship)
                }
            }
            
            # Generate recommendations
            recommendations = self._generate_enhanced_recommendations(
                match_breakdown, internship, candidate_profile
            )
            
            # Determine match confidence
            confidence_level = self._calculate_match_confidence(final_score, match_breakdown)
            
            return {
                'overall_score': final_score,
                'percentage': round(final_score * 100, 1),
                'match_breakdown': match_breakdown,
                'recommendations': recommendations,
                'confidence_level': confidence_level,
                'historical_adjustments': historical_adjustments,
                'success_probability': self._estimate_success_probability(final_score, match_breakdown),
                'internship_id': internship.get('id'),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced match score: {str(e)}")
            return self._get_fallback_match_result(candidate_profile, internship)
    
    def _calculate_skills_match(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate advanced skills matching score"""
        required_skills = [skill.lower() for skill in internship.get('skills_required', [])]
        candidate_skills = self._extract_all_candidate_skills(candidate)
        
        if not required_skills:
            return 0.7  # Neutral score when no skills specified
        
        # Exact matches
        exact_matches = len(set(candidate_skills) & set(required_skills))
        exact_match_ratio = exact_matches / len(required_skills)
        
        # Partial matches (similar skills)
        partial_matches = self._find_partial_skill_matches(candidate_skills, required_skills)
        partial_match_ratio = partial_matches / len(required_skills)
        
        # Experience level bonus for skills
        experience_bonus = self._calculate_skills_experience_bonus(candidate, required_skills)
        
        # Combine scores
        skills_score = min(1.0, exact_match_ratio * 1.0 + partial_match_ratio * 0.6 + experience_bonus)
        return skills_score
    
    def _calculate_experience_relevance(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate experience relevance score"""
        candidate_experience = candidate.get('experience', [])
        internship_category = internship.get('category', '').lower()
        
        if not candidate_experience:
            return 0.3  # Low score for no experience
        
        relevance_scores = []
        for exp in candidate_experience:
            exp_title = exp.get('title', '').lower()
            exp_description = exp.get('description', '').lower()
            
            # Category relevance
            category_relevance = self._calculate_category_relevance(
                exp_title + ' ' + exp_description, internship_category
            )
            
            # Duration weight (longer experience gets more weight)
            duration = exp.get('duration', '')
            duration_weight = self._parse_duration_weight(duration)
            
            relevance_scores.append(category_relevance * duration_weight)
        
        return min(1.0, max(relevance_scores) if relevance_scores else 0.3)
    
    def _calculate_company_compatibility(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate compatibility with company culture and ratings"""
        company_data = internship.get('company_data', {})
        
        # Company rating factor
        company_rating = company_data.get('rating', 4.0)
        rating_score = min(1.0, company_rating / 5.0)
        
        # Work-life balance preference
        wlb_rating = company_data.get('work_life_balance_rating', 4.0)
        wlb_score = min(1.0, wlb_rating / 5.0)
        
        # Career opportunities
        career_rating = company_data.get('career_opportunities_rating', 4.0)
        career_score = min(1.0, career_rating / 5.0)
        
        # Interview difficulty vs candidate confidence
        interview_difficulty = company_data.get('interview_difficulty', 3.0)
        candidate_confidence = self._assess_candidate_confidence(candidate)
        difficulty_match = 1.0 - abs(interview_difficulty/5.0 - candidate_confidence) * 0.5
        
        # Combine factors
        compatibility_score = (rating_score * 0.4 + wlb_score * 0.3 + 
                             career_score * 0.2 + difficulty_match * 0.1)
        
        return min(1.0, compatibility_score)
    
    def _calculate_location_preference(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate location preference match"""
        candidate_location = candidate.get('location', '').lower()
        internship_location = internship.get('location', '').lower()
        
        # Remote work preference
        if internship.get('remote_option') and self._prefers_remote_work(candidate):
            return 1.0
        
        # Exact location match
        if candidate_location in internship_location or internship_location in candidate_location:
            return 1.0
        
        # Same city/state
        if self._same_region(candidate_location, internship_location):
            return 0.8
        
        # Relocation willingness (would be in candidate profile)
        relocation_willingness = candidate.get('relocation_willingness', 0.5)
        return min(1.0, relocation_willingness)
    
    def _calculate_salary_alignment(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate salary expectation alignment"""
        expected_salary = candidate.get('expected_salary', {})
        internship_min = internship.get('salary_min', 0)
        internship_max = internship.get('salary_max', 0)
        
        if not internship_min and not internship_max:
            return 0.7  # Neutral score when salary not disclosed
        
        candidate_min = expected_salary.get('min', internship_min * 0.8)
        candidate_max = expected_salary.get('max', internship_max * 1.2)
        
        # Check for overlap in salary ranges
        if internship_max >= candidate_min and internship_min <= candidate_max:
            # Calculate alignment quality
            overlap_start = max(internship_min, candidate_min)
            overlap_end = min(internship_max, candidate_max)
            overlap_size = overlap_end - overlap_start
            
            candidate_range = candidate_max - candidate_min
            internship_range = internship_max - internship_min
            
            alignment = overlap_size / min(candidate_range, internship_range)
            return min(1.0, alignment)
        
        return 0.2  # Low score for no overlap
    
    def _calculate_career_goals_alignment(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate career goals alignment"""
        candidate_goals = candidate.get('career_goals', [])
        internship_category = internship.get('category', '')
        company_data = internship.get('company_data', {})
        
        # Category alignment with goals
        category_alignment = 0.0
        for goal in candidate_goals:
            if internship_category.lower() in goal.lower():
                category_alignment = 1.0
                break
            elif any(word in goal.lower() for word in internship_category.lower().split()):
                category_alignment = max(category_alignment, 0.7)
        
        # Growth opportunities
        growth_potential = company_data.get('match_factors', {}).get('growth_potential', 'Medium')
        growth_score = {'High': 1.0, 'Medium': 0.7, 'Moderate': 0.5, 'Low': 0.3}.get(growth_potential, 0.7)
        
        # Learning opportunities
        learning_opportunities = internship.get('learning_opportunities', 'Good')
        learning_score = {'Excellent': 1.0, 'Good': 0.8, 'Average': 0.6, 'Basic': 0.4}.get(learning_opportunities, 0.8)
        
        return (category_alignment * 0.5 + growth_score * 0.3 + learning_score * 0.2)
    
    def _apply_historical_patterns(self, candidate: Dict[str, Any], internship: Dict[str, Any], 
                                  historical_data: Optional[List[Dict]]) -> float:
        """Apply historical success patterns to adjust match score"""
        adjustments = 0.0
        
        # GPA-based adjustment for tech roles
        if 'technology' in internship.get('category', '').lower():
            gpa = candidate.get('gpa', 0)
            if gpa >= 3.7:
                adjustments += 0.05
            elif gpa <= 3.0:
                adjustments -= 0.05
        
        # Project experience boost
        projects = candidate.get('projects', [])
        if len(projects) >= 2:
            adjustments += 0.03
        
        # Exact skill match bonus
        if self._has_exact_skill_matches(candidate, internship):
            adjustments += 0.08
        
        # Location mismatch penalty
        if not self._location_compatible(candidate, internship):
            adjustments -= 0.05
        
        return adjustments
    
    def _generate_enhanced_recommendations(self, match_breakdown: Dict[str, Any], 
                                         internship: Dict[str, Any], 
                                         candidate: Dict[str, Any]) -> List[str]:
        """Generate enhanced recommendations based on detailed analysis"""
        recommendations = []
        
        # Skills-based recommendations
        skills_score = match_breakdown['skills_match']['score']
        if skills_score < 0.6:
            missing_skills = match_breakdown['skills_match']['details'].get('missing_skills', [])
            if missing_skills:
                recommendations.append(f"Consider learning: {', '.join(missing_skills[:3])}")
        elif skills_score > 0.85:
            recommendations.append("🎯 Excellent skills match - you're highly qualified!")
        
        # Company-specific recommendations
        company_score = match_breakdown['company_compatibility']['score']
        company_data = internship.get('company_data', {})
        
        if company_score > 0.8:
            company_rating = company_data.get('rating', 4.0)
            if company_rating >= 4.5:
                recommendations.append("⭐ Top-rated company with excellent culture")
        
        interview_difficulty = company_data.get('interview_difficulty', 3.0)
        if interview_difficulty >= 4.0:
            recommendations.append("💪 Prepare thoroughly - competitive interview process")
        elif interview_difficulty <= 2.5:
            recommendations.append("😊 Standard interview process - good opportunity to shine")
        
        # Experience-based recommendations
        exp_score = match_breakdown['experience_relevance']['score']
        if exp_score < 0.4:
            recommendations.append("📚 Consider highlighting relevant coursework and projects")
        
        # Salary recommendations
        salary_score = match_breakdown['salary_alignment']['score']
        if salary_score > 0.8:
            recommendations.append("💰 Competitive compensation package")
        
        # Career growth recommendations
        career_score = match_breakdown['career_alignment']['score']
        if career_score > 0.8:
            recommendations.append("🚀 Great fit for your career goals")
        
        # Learning opportunities
        learning = internship.get('learning_opportunities', '')
        if learning == 'Excellent':
            recommendations.append("🎓 Exceptional learning and development opportunities")
        
        # Conversion rate
        conversion_rate = internship.get('conversion_rate', '')
        if conversion_rate and int(conversion_rate.replace('%', '')) > 70:
            recommendations.append("🔄 High full-time conversion rate")
        
        if not recommendations:
            recommendations.append("✅ Solid overall match - worth considering!")
        
        return recommendations
    
    def _calculate_match_confidence(self, final_score: float, match_breakdown: Dict[str, Any]) -> str:
        """Calculate confidence level in the match"""
        # Check consistency across different factors
        scores = [component['score'] for component in match_breakdown.values()]
        score_variance = sum((s - final_score) ** 2 for s in scores) / len(scores)
        
        if final_score >= 0.85 and score_variance < 0.02:
            return "Very High"
        elif final_score >= 0.75 and score_variance < 0.05:
            return "High"
        elif final_score >= 0.6 and score_variance < 0.1:
            return "Medium"
        elif final_score >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _estimate_success_probability(self, final_score: float, match_breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate probability of successful internship outcome"""
        base_probability = final_score * 0.85  # Base success rate
        
        # Adjust based on specific factors
        skills_weight = match_breakdown['skills_match']['score'] * 0.15
        company_weight = match_breakdown['company_compatibility']['score'] * 0.10
        
        total_probability = min(0.95, base_probability + skills_weight + company_weight)
        
        return {
            'overall_success': round(total_probability * 100, 1),
            'learning_success': round(min(0.95, total_probability + 0.05) * 100, 1),
            'conversion_probability': round(total_probability * 0.6 * 100, 1),
            'satisfaction_probability': round(min(0.98, total_probability + 0.08) * 100, 1)
        }
    
    # Helper methods (simplified implementations)
    def _extract_all_candidate_skills(self, candidate: Dict[str, Any]) -> List[str]:
        """Extract all skills from candidate profile"""
        all_skills = []
        skills_dict = candidate.get('skills', {})
        
        for skill_type, skills in skills_dict.items():
            if isinstance(skills, list):
                all_skills.extend([skill.lower() for skill in skills])
        
        return list(set(all_skills))
    
    def _find_partial_skill_matches(self, candidate_skills: List[str], required_skills: List[str]) -> int:
        """Find partial skill matches"""
        partial_matches = 0
        skill_synonyms = {
            'javascript': ['js', 'node', 'react', 'angular'],
            'python': ['django', 'flask', 'pandas'],
            'java': ['spring', 'hibernate'],
            'sql': ['mysql', 'postgresql', 'database']
        }
        
        for required in required_skills:
            if required not in candidate_skills:
                # Check for synonyms or related skills
                for candidate_skill in candidate_skills:
                    if (required in skill_synonyms.get(candidate_skill, []) or
                        candidate_skill in skill_synonyms.get(required, [])):
                        partial_matches += 1
                        break
        
        return partial_matches
    
    def _calculate_skills_experience_bonus(self, candidate: Dict[str, Any], required_skills: List[str]) -> float:
        """Calculate bonus for experience with required skills"""
        experience = candidate.get('experience', [])
        bonus = 0.0
        
        for exp in experience:
            description = exp.get('description', '').lower()
            for skill in required_skills:
                if skill in description:
                    bonus += 0.05
        
        return min(0.2, bonus)
    
    def _calculate_category_relevance(self, experience_text: str, internship_category: str) -> float:
        """Calculate relevance of experience to internship category"""
        category_keywords = {
            'software development': ['programming', 'coding', 'development', 'software', 'web', 'app'],
            'data science': ['data', 'analytics', 'machine learning', 'statistics', 'python'],
            'digital marketing': ['marketing', 'social media', 'seo', 'content', 'campaign'],
            'design': ['design', 'ui', 'ux', 'creative', 'graphics', 'visual']
        }
        
        keywords = category_keywords.get(internship_category, [])
        matches = sum(1 for keyword in keywords if keyword in experience_text)
        
        return min(1.0, matches / len(keywords) if keywords else 0.5)
    
    def _parse_duration_weight(self, duration: str) -> float:
        """Parse experience duration and return weight"""
        if not duration:
            return 0.5
        
        duration_lower = duration.lower()
        if 'year' in duration_lower:
            return 1.0
        elif 'month' in duration_lower:
            months = sum(int(word) for word in duration.split() if word.isdigit())
            return min(1.0, months / 12)
        else:
            return 0.5
    
    def _assess_candidate_confidence(self, candidate: Dict[str, Any]) -> float:
        """Assess candidate's confidence level based on profile"""
        confidence_factors = []
        
        # Experience factor
        experience_count = len(candidate.get('experience', []))
        experience_factor = min(1.0, experience_count / 3)
        confidence_factors.append(experience_factor)
        
        # Education factor
        education = candidate.get('education', [])
        if education:
            degree_level = education[0].get('degree', '').lower()
            if 'master' in degree_level or 'mtech' in degree_level:
                confidence_factors.append(0.9)
            elif 'bachelor' in degree_level or 'btech' in degree_level:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
        
        # Projects factor
        projects_count = len(candidate.get('projects', []))
        projects_factor = min(1.0, projects_count / 4)
        confidence_factors.append(projects_factor)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _prefers_remote_work(self, candidate: Dict[str, Any]) -> bool:
        """Check if candidate prefers remote work"""
        preferences = candidate.get('work_preferences', {})
        return preferences.get('remote_preferred', False)
    
    def _same_region(self, location1: str, location2: str) -> bool:
        """Check if two locations are in the same region"""
        # Simplified implementation
        return any(city in location1 for city in location2.split()) or \
               any(city in location2 for city in location1.split())
    
    def _has_exact_skill_matches(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> bool:
        """Check if candidate has exact matches for key skills"""
        candidate_skills = self._extract_all_candidate_skills(candidate)
        required_skills = [skill.lower() for skill in internship.get('skills_required', [])]
        
        exact_matches = len(set(candidate_skills) & set(required_skills))
        return exact_matches >= len(required_skills) * 0.6
    
    def _location_compatible(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> bool:
        """Check if location is compatible"""
        candidate_location = candidate.get('location', '').lower()
        internship_location = internship.get('location', '').lower()
        
        return (candidate_location in internship_location or 
                internship_location in candidate_location or
                internship.get('remote_option', False))
    
    def _get_skills_details(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed skills matching information"""
        candidate_skills = self._extract_all_candidate_skills(candidate)
        required_skills = [skill.lower() for skill in internship.get('skills_required', [])]
        
        matched_skills = list(set(candidate_skills) & set(required_skills))
        missing_skills = list(set(required_skills) - set(candidate_skills))
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_ratio': len(matched_skills) / len(required_skills) if required_skills else 0
        }
    
    def _get_experience_details(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed experience matching information"""
        experience = candidate.get('experience', [])
        return {
            'total_experience_count': len(experience),
            'relevant_experience': sum(1 for exp in experience 
                                     if internship.get('category', '').lower() in 
                                     (exp.get('title', '') + ' ' + exp.get('description', '')).lower()),
            'experience_level': 'Senior' if len(experience) >= 3 else 'Mid' if len(experience) >= 2 else 'Entry'
        }
    
    def _get_company_details(self, internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get company compatibility details"""
        company_data = internship.get('company_data', {})
        return {
            'company_rating': company_data.get('rating', 0),
            'work_life_balance': company_data.get('work_life_balance_rating', 0),
            'career_opportunities': company_data.get('career_opportunities_rating', 0),
            'interview_difficulty': company_data.get('interview_difficulty', 0)
        }
    
    def _get_location_details(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get location preference details"""
        return {
            'candidate_location': candidate.get('location', ''),
            'internship_location': internship.get('location', ''),
            'remote_option': internship.get('remote_option', False),
            'match_type': 'exact' if candidate.get('location', '').lower() in internship.get('location', '').lower() else 'different'
        }
    
    def _get_salary_details(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get salary alignment details"""
        return {
            'internship_range': f"₹{internship.get('salary_min', 0)} - ₹{internship.get('salary_max', 0)}",
            'candidate_expectation': candidate.get('expected_salary', {}),
            'alignment': 'good' if internship.get('salary_max', 0) > 0 else 'unknown'
        }
    
    def _get_career_details(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Get career goals alignment details"""
        return {
            'candidate_goals': candidate.get('career_goals', []),
            'internship_category': internship.get('category', ''),
            'growth_potential': internship.get('company_data', {}).get('match_factors', {}).get('growth_potential', 'Medium'),
            'learning_opportunities': internship.get('learning_opportunities', 'Good')
        }
    
    def _get_fallback_match_result(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Return fallback match result when calculation fails"""
        return {
            'overall_score': 0.6,
            'percentage': 60.0,
            'match_breakdown': {},
            'recommendations': ['Error in detailed analysis - basic match calculated'],
            'confidence_level': 'Low',
            'historical_adjustments': 0.0,
            'success_probability': {'overall_success': 60.0},
            'internship_id': internship.get('id'),
            'calculated_at': datetime.now().isoformat(),
            'error': 'Fallback calculation used'
        }
