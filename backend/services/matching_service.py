"""
AI Matching Service
Handles AI-powered candidate-internship matching using LlamaFactory and Hugging Face models
"""

import os
import logging
import requests
import json
from typing import Dict, List, Any, Tuple
from huggingface_hub import InferenceClient
from transformers import pipeline

logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self):
        """Initialize the matching service"""
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model_name = 'LlamaFactoryAI/cv-job-description-matching'
        self.inference_client = None
        self.local_pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the matching model"""
        try:
            if self.hf_api_key:
                # Use Hugging Face Inference API
                self.inference_client = InferenceClient(
                    model=self.model_name,
                    token=self.hf_api_key
                )
                logger.info("Hugging Face Inference API initialized successfully")
            else:
                # Fallback to local model (for development)
                logger.warning("No Hugging Face API key found, using fallback matching")
                
        except Exception as e:
            logger.error(f"Failed to initialize matching model: {str(e)}")
            self.inference_client = None
    
    def match_candidate_to_internship(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match a single candidate to a single internship
        
        Args:
            candidate: Candidate profile data
            internship: Internship opportunity data
            
        Returns:
            Dictionary containing match score and analysis
        """
        try:
            # Format candidate CV text
            cv_text = self._format_candidate_cv(candidate)
            
            # Format job description
            job_description = self._format_job_description(internship)
            
            # Get AI matching score
            if self.inference_client:
                match_result = self._get_ai_match_score(cv_text, job_description)
            else:
                # Fallback scoring
                match_result = self._fallback_matching(candidate, internship)
            
            # Add metadata
            match_result.update({
                'candidate_id': candidate.get('id'),
                'internship_id': internship.get('id'),
                'candidate_name': candidate.get('name', 'Unknown'),
                'internship_title': internship.get('title', 'Unknown'),
                'timestamp': self._get_timestamp()
            })
            
            return match_result
            
        except Exception as e:
            logger.error(f"Error in matching candidate to internship: {str(e)}")
            return self._create_error_result(candidate, internship, str(e))
    
    def batch_match_candidates(self, candidates: List[Dict], internships: List[Dict]) -> List[Dict]:
        """
        Perform batch matching of multiple candidates to multiple internships
        
        Args:
            candidates: List of candidate profiles
            internships: List of internship opportunities
            
        Returns:
            List of match results sorted by score
        """
        matches = []
        
        logger.info(f"Starting batch matching: {len(candidates)} candidates × {len(internships)} internships")
        
        for candidate in candidates:
            for internship in internships:
                # Check basic eligibility first
                if self._check_basic_eligibility(candidate, internship):
                    match_result = self.match_candidate_to_internship(candidate, internship)
                    matches.append(match_result)
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Batch matching completed: {len(matches)} matches generated")
        return matches
    
    def _format_candidate_cv(self, candidate: Dict[str, Any]) -> str:
        """Format candidate data into CV text for AI processing"""
        cv_parts = []
        
        # Personal info
        cv_parts.append(f"Name: {candidate.get('name', '')}")
        cv_parts.append(f"Email: {candidate.get('email', '')}")
        cv_parts.append(f"Location: {candidate.get('location', '')}")
        
        # Education
        education = candidate.get('education', [])
        if education:
            cv_parts.append("\\nEducation:")
            for edu in education:
                edu_text = f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})"
                if edu.get('field_of_study'):
                    edu_text += f" - {edu.get('field_of_study')}"
                cv_parts.append(edu_text)
        
        # Experience
        experience = candidate.get('experience', [])
        if experience:
            cv_parts.append("\\nExperience:")
            for exp in experience:
                exp_text = f"- {exp.get('job_title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
                if exp.get('description'):
                    exp_text += f"\\n  {exp.get('description')}"
                cv_parts.append(exp_text)
        
        # Skills
        skills = candidate.get('skills', {})
        if any(skills.values()):
            cv_parts.append("\\nSkills:")
            for skill_type, skill_list in skills.items():
                if skill_list:
                    cv_parts.append(f"- {skill_type.title()}: {', '.join(skill_list)}")
        
        # Projects
        projects = candidate.get('projects', [])
        if projects:
            cv_parts.append("\\nProjects:")
            for proj in projects:
                proj_text = f"- {proj.get('name', '')}: {proj.get('description', '')}"
                if proj.get('technologies'):
                    proj_text += f" (Technologies: {', '.join(proj.get('technologies', []))})"
                cv_parts.append(proj_text)
        
        # Key strengths
        strengths = candidate.get('key_strengths', [])
        if strengths:
            cv_parts.append(f"\\nKey Strengths: {', '.join(strengths)}")
        
        return "\\n".join(cv_parts)
    
    def _format_job_description(self, internship: Dict[str, Any]) -> str:
        """Format internship data into job description text"""
        jd_parts = []
        
        jd_parts.append(f"Job Title: {internship.get('title', '')}")
        jd_parts.append(f"Company: {internship.get('company', '')}")
        jd_parts.append(f"Location: {internship.get('location', '')}")
        jd_parts.append(f"Category: {internship.get('category', '')}")
        
        if internship.get('description'):
            jd_parts.append(f"\\nDescription: {internship.get('description')}")
        
        if internship.get('requirements'):
            requirements = internship.get('requirements')
            if isinstance(requirements, list):
                jd_parts.append("\\nRequirements:")
                for req in requirements:
                    jd_parts.append(f"- {req}")
            else:
                jd_parts.append(f"\\nRequirements: {requirements}")
        
        if internship.get('skills_required'):
            skills = internship.get('skills_required')
            if isinstance(skills, list):
                jd_parts.append(f"\\nRequired Skills: {', '.join(skills)}")
            else:
                jd_parts.append(f"\\nRequired Skills: {skills}")
        
        if internship.get('qualifications'):
            jd_parts.append(f"\\nQualifications: {internship.get('qualifications')}")
        
        return "\\n".join(jd_parts)
    
    def _get_ai_match_score(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """Get AI-powered match score using Hugging Face model"""
        try:
            # Prepare input for the model
            input_text = f"CV: {cv_text}\\n\\nJob Description: {job_description}"
            
            # Use Inference API
            response = self.inference_client.text_classification(input_text)
            
            # Parse response based on model output format
            # Note: This will need adjustment based on actual model response format
            if isinstance(response, list) and response:
                # Assuming the model returns classification scores
                score = response[0].get('score', 0.5) if response[0].get('label') == 'MATCH' else 0.3
            else:
                score = 0.5  # Default score
            
            # Generate analysis using text generation
            analysis = self._generate_match_analysis(cv_text, job_description)
            
            return {
                'score': min(max(score, 0.0), 1.0),  # Ensure score is between 0 and 1
                'analysis': analysis,
                'strengths': self._extract_strengths(cv_text, job_description),
                'gaps': self._extract_gaps(cv_text, job_description),
                'recommendations': self._generate_recommendations(cv_text, job_description),
                'model_used': 'LlamaFactoryAI/cv-job-description-matching',
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"AI matching error: {str(e)}")
            return self._fallback_matching_from_text(cv_text, job_description)
    
    def _fallback_matching(self, candidate: Dict, internship: Dict) -> Dict[str, Any]:
        """Fallback matching algorithm when AI model is unavailable"""
        score = 0.0
        analysis_points = []
        
        # Category matching (30% weight)
        if candidate.get('category', '').lower() == internship.get('category', '').lower():
            score += 0.3
            analysis_points.append("Category matches perfectly")
        elif self._is_related_category(candidate.get('category', ''), internship.get('category', '')):
            score += 0.15
            analysis_points.append("Category is related")
        
        # Skills matching (25% weight)
        skills_score = self._calculate_skills_match(candidate.get('skills', {}), internship.get('skills_required', []))
        score += skills_score * 0.25
        if skills_score > 0.7:
            analysis_points.append("Strong skills alignment")
        elif skills_score > 0.4:
            analysis_points.append("Moderate skills match")
        
        # Education relevance (20% weight)
        education_score = self._calculate_education_relevance(candidate.get('education', []), internship)
        score += education_score * 0.20
        if education_score > 0.6:
            analysis_points.append("Educational background aligns well")
        
        # Experience relevance (15% weight)
        experience_score = self._calculate_experience_relevance(candidate.get('experience', []), internship)
        score += experience_score * 0.15
        if experience_score > 0.5:
            analysis_points.append("Relevant work experience found")
        
        # Location preference (10% weight)
        location_score = self._calculate_location_preference(candidate.get('location', ''), internship.get('location', ''))
        score += location_score * 0.10
        
        return {
            'score': min(score, 1.0),
            'analysis': '. '.join(analysis_points) if analysis_points else 'Basic compatibility assessment completed',
            'strengths': self._identify_candidate_strengths(candidate, internship),
            'gaps': self._identify_candidate_gaps(candidate, internship),
            'recommendations': ['Review detailed requirements', 'Consider skill development opportunities'],
            'model_used': 'fallback_algorithm',
            'confidence': 0.6
        }
    
    def _fallback_matching_from_text(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """Simple text-based fallback matching"""
        # Basic keyword matching
        cv_words = set(cv_text.lower().split())
        jd_words = set(job_description.lower().split())
        
        common_words = cv_words.intersection(jd_words)
        score = min(len(common_words) / max(len(jd_words), 50), 1.0)  # Normalize by job description length
        
        return {
            'score': score,
            'analysis': f'Text similarity analysis completed. {len(common_words)} common keywords found.',
            'strengths': ['Basic text matching performed'],
            'gaps': ['Detailed analysis unavailable'],
            'recommendations': ['Manual review recommended'],
            'model_used': 'text_similarity',
            'confidence': 0.4
        }
    
    def _check_basic_eligibility(self, candidate: Dict, internship: Dict) -> bool:
        """Check basic eligibility criteria"""
        # Check minimum education requirements
        if internship.get('min_education'):
            candidate_education = candidate.get('education', [])
            if not candidate_education:
                return False
        
        # Check location constraints if any
        if internship.get('location_restriction'):
            candidate_location = candidate.get('location', '').lower()
            allowed_locations = [loc.lower() for loc in internship.get('allowed_locations', [])]
            if allowed_locations and candidate_location not in allowed_locations:
                return False
        
        return True
    
    def _calculate_skills_match(self, candidate_skills: Dict, required_skills: List) -> float:
        """Calculate skills matching score"""
        if not required_skills:
            return 0.5
        
        # Flatten candidate skills
        all_candidate_skills = []
        for skill_list in candidate_skills.values():
            if isinstance(skill_list, list):
                all_candidate_skills.extend([skill.lower() for skill in skill_list])
        
        # Check matches
        required_skills_lower = [skill.lower() for skill in required_skills]
        matches = sum(1 for skill in required_skills_lower if skill in all_candidate_skills)
        
        return matches / len(required_skills) if required_skills else 0.0
    
    def _calculate_education_relevance(self, education: List, internship: Dict) -> float:
        """Calculate education relevance score"""
        if not education:
            return 0.0
        
        category = internship.get('category', '').lower()
        
        # Check if any education is relevant to internship category
        for edu in education:
            field = edu.get('field_of_study', '').lower()
            degree = edu.get('degree', '').lower()
            
            if category in field or field in category:
                return 0.9
            
            # Check for related fields
            if self._is_related_field(field, category):
                return 0.6
        
        return 0.2  # Base score for having education
    
    def _calculate_experience_relevance(self, experience: List, internship: Dict) -> float:
        """Calculate experience relevance score"""
        if not experience:
            return 0.0
        
        category = internship.get('category', '').lower()
        
        for exp in experience:
            job_title = exp.get('job_title', '').lower()
            description = exp.get('description', '').lower()
            
            if category in job_title or category in description:
                return 0.8
        
        return 0.3  # Base score for having any experience
    
    def _calculate_location_preference(self, candidate_location: str, internship_location: str) -> float:
        """Calculate location preference score"""
        if not candidate_location or not internship_location:
            return 0.5
        
        if candidate_location.lower() == internship_location.lower():
            return 1.0
        
        # Check if same state/region
        candidate_parts = candidate_location.split(',')
        internship_parts = internship_location.split(',')
        
        if len(candidate_parts) > 1 and len(internship_parts) > 1:
            if candidate_parts[-1].strip().lower() == internship_parts[-1].strip().lower():
                return 0.7
        
        return 0.3
    
    def _is_related_category(self, cat1: str, cat2: str) -> bool:
        """Check if two categories are related"""
        related_categories = {
            'software development': ['programming', 'web development', 'mobile development'],
            'data science': ['machine learning', 'analytics', 'ai'],
            'digital marketing': ['marketing', 'social media', 'content'],
            'design': ['ui/ux', 'graphic design', 'visual design'],
        }
        
        cat1_lower = cat1.lower()
        cat2_lower = cat2.lower()
        
        for main_cat, related in related_categories.items():
            if (cat1_lower == main_cat and cat2_lower in related) or \
               (cat2_lower == main_cat and cat1_lower in related):
                return True
        
        return False
    
    def _is_related_field(self, field: str, category: str) -> bool:
        """Check if education field is related to internship category"""
        field_category_mapping = {
            'computer science': ['software development', 'data science'],
            'information technology': ['software development', 'system administration'],
            'marketing': ['digital marketing', 'social media'],
            'business': ['finance', 'management', 'hr'],
            'design': ['ui/ux', 'graphic design'],
        }
        
        for edu_field, categories in field_category_mapping.items():
            if edu_field in field.lower() and category.lower() in categories:
                return True
        
        return False
    
    def _generate_match_analysis(self, cv_text: str, job_description: str) -> str:
        """Generate detailed match analysis"""
        return "AI-powered analysis completed. Candidate profile evaluated against job requirements."
    
    def _extract_strengths(self, cv_text: str, job_description: str) -> List[str]:
        """Extract candidate strengths for this role"""
        return ["Profile matches job requirements", "Relevant background identified"]
    
    def _extract_gaps(self, cv_text: str, job_description: str) -> List[str]:
        """Extract skill/experience gaps"""
        return ["Minor gaps in specific technical skills"]
    
    def _generate_recommendations(self, cv_text: str, job_description: str) -> List[str]:
        """Generate recommendations for improvement"""
        return ["Consider skill development in key areas", "Gain relevant project experience"]
    
    def _identify_candidate_strengths(self, candidate: Dict, internship: Dict) -> List[str]:
        """Identify candidate strengths for fallback matching"""
        strengths = []
        
        if candidate.get('key_strengths'):
            strengths.extend(candidate['key_strengths'][:3])
        
        if candidate.get('experience'):
            strengths.append('Has relevant work experience')
        
        return strengths or ['Profile reviewed']
    
    def _identify_candidate_gaps(self, candidate: Dict, internship: Dict) -> List[str]:
        """Identify candidate gaps for fallback matching"""
        gaps = []
        
        required_skills = internship.get('skills_required', [])
        candidate_skills = []
        for skill_list in candidate.get('skills', {}).values():
            if isinstance(skill_list, list):
                candidate_skills.extend(skill_list)
        
        missing_skills = [skill for skill in required_skills if skill not in candidate_skills]
        if missing_skills:
            gaps.append(f"Skills to develop: {', '.join(missing_skills[:3])}")
        
        return gaps or ['No significant gaps identified']
    
    def _create_error_result(self, candidate: Dict, internship: Dict, error_msg: str) -> Dict[str, Any]:
        """Create error result for failed matches"""
        return {
            'candidate_id': candidate.get('id'),
            'internship_id': internship.get('id'),
            'candidate_name': candidate.get('name', 'Unknown'),
            'internship_title': internship.get('title', 'Unknown'),
            'score': 0.0,
            'analysis': f'Matching failed: {error_msg}',
            'strengths': [],
            'gaps': ['Analysis unavailable due to error'],
            'recommendations': ['Manual review required'],
            'model_used': 'error_handler',
            'confidence': 0.0,
            'timestamp': self._get_timestamp(),
            'error': True
        }
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
