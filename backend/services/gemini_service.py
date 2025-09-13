"""
Gemini AI Service
Handles Google Gemini API integration for CV parsing and information extraction
"""

import google.generativeai as genai
import os
import logging
import json
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = 'gemini-1.5-flash'
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            if not self.api_key:
                raise Exception("Google API key not found in environment variables")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("Gemini AI initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            self.model = None
    
    def parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Parse CV text and extract structured information
        
        Args:
            cv_text: Raw text content from CV
            
        Returns:
            Dictionary containing extracted information
        """
        if not self.model:
            raise Exception("Gemini AI not initialized")
        
        try:
            prompt = self._create_cv_parsing_prompt(cv_text)
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            parsed_data = self._parse_gemini_response(response.text)
            
            # Validate and clean the data
            cleaned_data = self._validate_and_clean_data(parsed_data)
            
            # Add confidence score based on completeness
            cleaned_data['confidence_score'] = self._calculate_confidence_score(cleaned_data)
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"CV parsing error: {str(e)}")
            return self._create_fallback_response(cv_text)
    
    def _create_cv_parsing_prompt(self, cv_text: str) -> str:
        """Create a structured prompt for CV parsing"""
        prompt = f"""You are an AI assistant specialized in parsing CVs/resumes. Extract the following information from the given CV text and return it as a valid JSON object.

        CV Text:
        {cv_text}

        Please extract and structure the following information in JSON format:

        {{
            "personal_info": {{
                "name": "Full name of the candidate",
                "email": "Email address",
                "phone": "Phone number",
                "location": "City, State/Region, Country",
                "address": "Full address if available"
            }},
            "education": [
                {{
                    "degree": "Degree name",
                    "institution": "Institution name",
                    "year": "Graduation year or expected year",
                    "grade": "Grade/CGPA if mentioned",
                    "field_of_study": "Field of study"
                }}
            ],
            "experience": [
                {{
                    "job_title": "Job title/position",
                    "company": "Company name",
                    "duration": "Employment duration",
                    "description": "Job description or key responsibilities",
                    "location": "Job location if mentioned"
                }}
            ],
            "skills": {{
                "technical": ["List of technical skills"],
                "soft": ["List of soft skills"],
                "languages": ["Programming languages"],
                "tools": ["Software tools and technologies"]
            }},
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"],
                    "duration": "Project duration if mentioned"
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification name",
                    "issuer": "Issuing organization",
                    "date": "Date obtained"
                }}
            ],
            "category": "Determine the most suitable internship category based on education and experience (e.g., 'Software Development', 'Data Science', 'Digital Marketing', 'Finance', 'HR', 'Design', 'Engineering', 'Research')",
            "social_category": "Extract if mentioned (General, SC, ST, OBC)",
            "rural_background": "Determine if candidate has rural background based on location or mentions (true/false)",
            "key_strengths": ["3-5 key strengths based on the CV"],
            "experience_level": "Entry Level, Mid Level, or Senior Level based on experience"
        }}

        Important instructions:
        1. Return ONLY the JSON object, no additional text
        2. If information is not available, use null or empty array as appropriate
        3. Ensure all strings are properly escaped for JSON
        4. For category, choose the most relevant internship category based on the candidate's background
        5. Be accurate and don't hallucinate information not present in the CV
        6. For rural background, look for indicators like rural district names, village mentions, or agricultural background
        """
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response and extract JSON"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text)
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            # Try to extract JSON from the response using regex
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise Exception("Could not parse JSON from Gemini response")
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        cleaned_data = {}
        
        # Extract personal information
        personal_info = data.get('personal_info', {})
        cleaned_data.update({
            'name': self._clean_string(personal_info.get('name')),
            'email': self._clean_email(personal_info.get('email')),
            'phone': self._clean_phone(personal_info.get('phone')),
            'location': self._clean_string(personal_info.get('location')),
            'address': self._clean_string(personal_info.get('address'))
        })
        
        # Education
        education = data.get('education', [])
        cleaned_data['education'] = [
            {
                'degree': self._clean_string(edu.get('degree')),
                'institution': self._clean_string(edu.get('institution')),
                'year': self._clean_year(edu.get('year')),
                'grade': self._clean_string(edu.get('grade')),
                'field_of_study': self._clean_string(edu.get('field_of_study'))
            }
            for edu in education if isinstance(edu, dict)
        ]
        
        # Experience
        experience = data.get('experience', [])
        cleaned_data['experience'] = [
            {
                'job_title': self._clean_string(exp.get('job_title')),
                'company': self._clean_string(exp.get('company')),
                'duration': self._clean_string(exp.get('duration')),
                'description': self._clean_string(exp.get('description')),
                'location': self._clean_string(exp.get('location'))
            }
            for exp in experience if isinstance(exp, dict)
        ]
        
        # Skills
        skills = data.get('skills', {})
        cleaned_data['skills'] = {
            'technical': self._clean_list(skills.get('technical', [])),
            'soft': self._clean_list(skills.get('soft', [])),
            'languages': self._clean_list(skills.get('languages', [])),
            'tools': self._clean_list(skills.get('tools', []))
        }
        
        # Projects
        projects = data.get('projects', [])
        cleaned_data['projects'] = [
            {
                'name': self._clean_string(proj.get('name')),
                'description': self._clean_string(proj.get('description')),
                'technologies': self._clean_list(proj.get('technologies', [])),
                'duration': self._clean_string(proj.get('duration'))
            }
            for proj in projects if isinstance(proj, dict)
        ]
        
        # Certifications
        certifications = data.get('certifications', [])
        cleaned_data['certifications'] = [
            {
                'name': self._clean_string(cert.get('name')),
                'issuer': self._clean_string(cert.get('issuer')),
                'date': self._clean_string(cert.get('date'))
            }
            for cert in certifications if isinstance(cert, dict)
        ]
        
        # Other fields
        cleaned_data.update({
            'category': self._clean_string(data.get('category')),
            'social_category': self._clean_string(data.get('social_category')),
            'rural_background': data.get('rural_background', False),
            'key_strengths': self._clean_list(data.get('key_strengths', [])),
            'experience_level': self._clean_string(data.get('experience_level'))
        })
        
        return cleaned_data
    
    def _clean_string(self, value) -> str:
        """Clean and validate string values"""
        if not value or value == 'null':
            return ''
        return str(value).strip()
    
    def _clean_email(self, email) -> str:
        """Clean and validate email"""
        if not email:
            return ''
        email = str(email).strip().lower()
        # Basic email validation
        if '@' in email and '.' in email.split('@')[1]:
            return email
        return ''
    
    def _clean_phone(self, phone) -> str:
        """Clean and validate phone number"""
        if not phone:
            return ''
        # Remove non-digit characters except +
        phone = re.sub(r'[^\d+]', '', str(phone))
        return phone
    
    def _clean_year(self, year) -> str:
        """Clean and validate year"""
        if not year:
            return ''
        year_str = str(year).strip()
        # Extract 4-digit year
        year_match = re.search(r'\d{4}', year_str)
        return year_match.group() if year_match else year_str
    
    def _clean_list(self, items) -> List[str]:
        """Clean and validate list of strings"""
        if not isinstance(items, list):
            return []
        return [self._clean_string(item) for item in items if item and item != 'null']
    
    def _calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness"""
        required_fields = ['name', 'email', 'phone', 'location', 'category']
        optional_fields = ['education', 'experience', 'skills', 'projects']
        
        score = 0.0
        
        # Required fields (60% of score)
        for field in required_fields:
            if data.get(field) and data[field]:
                score += 0.12  # 60% / 5 fields
        
        # Optional fields (40% of score)
        for field in optional_fields:
            field_data = data.get(field)
            if field_data:
                if isinstance(field_data, list) and len(field_data) > 0:
                    score += 0.1  # 40% / 4 fields
                elif isinstance(field_data, dict) and any(field_data.values()):
                    score += 0.1
        
        return min(score, 1.0)
    
    def _create_fallback_response(self, cv_text: str) -> Dict[str, Any]:
        """Create fallback response when parsing fails"""
        logger.warning("Using fallback CV parsing")
        
        # Basic text extraction using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\+?\d[\d -]{8,12}\d'
        
        email_match = re.search(email_pattern, cv_text)
        phone_match = re.search(phone_pattern, cv_text)
        
        return {
            'name': '',
            'email': email_match.group() if email_match else '',
            'phone': phone_match.group() if phone_match else '',
            'location': '',
            'address': '',
            'education': [],
            'experience': [],
            'skills': {'technical': [], 'soft': [], 'languages': [], 'tools': []},
            'projects': [],
            'certifications': [],
            'category': '',
            'social_category': '',
            'rural_background': False,
            'key_strengths': [],
            'experience_level': '',
            'confidence_score': 0.2  # Low confidence for fallback
        }
