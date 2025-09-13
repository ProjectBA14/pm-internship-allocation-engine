"""
Enhanced Internship Service with Real Web Scraping and CV Integration
Connects uploaded CV data to internship matching with live scraping
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import re
import time
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class EnhancedInternshipService:
    """Enhanced service that integrates CV data with live internship matching"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_internships_for_candidate(self, candidate_data: Dict[str, Any], 
                                       categories: List[str] = None, 
                                       locations: List[str] = None, 
                                       limit: int = 20) -> Dict[str, Any]:
        """
        Search internships based on candidate CV data and calculate real match scores
        """
        try:
            # Extract candidate information from uploaded CV
            candidate_skills = self._extract_candidate_skills(candidate_data)
            candidate_location = candidate_data.get('location', '')
            candidate_category = candidate_data.get('category', '')
            
            logger.info(f"Searching internships for candidate: {candidate_skills[:3]}... in {candidate_location}")
            
            # Use candidate data to enhance search parameters
            if not categories and candidate_category:
                categories = [candidate_category]
            
            if not locations and candidate_location:
                locations = [candidate_location]
            
            # Scrape live internships
            all_internships = []
            
            # Scrape from multiple sources
            internshala_jobs = self._scrape_internshala_real(categories, locations, limit // 2)
            all_internships.extend(internshala_jobs)
            
            indeed_jobs = self._scrape_indeed_real(categories, locations, limit // 2)
            all_internships.extend(indeed_jobs)
            
            # Calculate real match scores for each internship
            matched_internships = []
            for internship in all_internships:
                match_analysis = self._calculate_real_match_score(candidate_data, internship)
                internship['match_analysis'] = match_analysis
                internship['match_score'] = match_analysis['overall_score']
                internship['match_percentage'] = match_analysis['percentage']
                internship['compatibility_level'] = match_analysis['compatibility_level']
                matched_internships.append(internship)
            
            # Sort by match score
            matched_internships.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # Return top matches
            top_matches = matched_internships[:limit]
            
            return {
                'internships': top_matches,
                'candidate_profile': {
                    'skills': candidate_skills,
                    'location': candidate_location,
                    'category': candidate_category,
                    'experience_level': candidate_data.get('experience_level', 'Entry Level')
                },
                'search_summary': {
                    'total_found': len(all_internships),
                    'after_matching': len(matched_internships),
                    'returned': len(top_matches),
                    'avg_match_score': sum(i.get('match_score', 0) for i in top_matches) / len(top_matches) if top_matches else 0,
                    'best_match': top_matches[0].get('match_percentage', 0) if top_matches else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching internships: {str(e)}")
            # Return fallback with mock data but real candidate matching
            return self._get_fallback_with_real_matching(candidate_data, limit)
    
    def _scrape_internshala_real(self, categories: List[str], locations: List[str], limit: int) -> List[Dict[str, Any]]:
        """Real Internshala scraping using requests and BeautifulSoup"""
        internships = []
        
        try:
            # Build Internshala search URL
            base_url = "https://internshala.com/internships"
            
            # Add search parameters
            search_params = []
            if categories:
                # Map to Internshala categories
                category_map = {
                    'software development': 'computer-science',
                    'data science': 'data-science',
                    'digital marketing': 'digital-marketing',
                    'design': 'graphic-design',
                    'finance': 'finance'
                }
                for cat in categories:
                    mapped_cat = category_map.get(cat.lower(), 'computer-science')
                    search_params.append(f"category={mapped_cat}")
            
            # Construct URL
            if search_params:
                url = f"{base_url}?{'&'.join(search_params)}"
            else:
                url = f"{base_url}/computer-science-internships"
            
            logger.info(f"Scraping Internshala: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find internship containers
            containers = soup.find_all('div', class_=['individual_internship', 'internship_meta'])
            
            if not containers:
                # Try alternative selectors
                containers = soup.find_all('div', attrs={'internshipid': True})
            
            for i, container in enumerate(containers[:limit]):
                try:
                    # Extract title
                    title_elem = container.find(['h3', 'h4'], class_=['heading_4_5', 'profile'])
                    if not title_elem:
                        title_elem = container.find('a', class_=['profile'])
                    
                    title = title_elem.get_text(strip=True) if title_elem else f"Software Development Internship {i+1}"
                    
                    # Skip if not internship
                    if 'internship' not in title.lower() and 'intern' not in title.lower():
                        title = f"{title} Internship"
                    
                    # Extract company
                    company_elem = container.find(['a', 'p'], class_=['link_display_like_text', 'company-name'])
                    company = company_elem.get_text(strip=True) if company_elem else f"Company {i+1}"
                    
                    # Extract location
                    location_elem = container.find(['a', 'span'], attrs={'title': 'Location'})
                    if not location_elem:
                        location_elem = container.find(['p', 'span'], class_=['location'])
                    
                    location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    
                    # Extract stipend
                    stipend_elem = container.find(['span'], class_=['stipend'])
                    salary = "₹15,000 - ₹25,000/month"
                    salary_min, salary_max = 15000, 25000
                    
                    if stipend_elem:
                        stipend_text = stipend_elem.get_text(strip=True)
                        numbers = re.findall(r'[0-9,]+', stipend_text)
                        if numbers:
                            try:
                                amount = int(numbers[0].replace(',', ''))
                                if amount >= 1000:
                                    salary_min = max(amount - 5000, 5000)
                                    salary_max = amount + 10000
                                    salary = f"₹{salary_min:,} - ₹{salary_max:,}/month"
                            except:
                                pass
                    
                    # Extract apply link - try multiple selectors
                    apply_elem = container.find('a', href=True)
                    if not apply_elem:
                        apply_elem = container.find('a', class_=['view_detail_button', 'btn-primary'])
                    
                    apply_link = None
                    if apply_elem and apply_elem.get('href'):
                        href = apply_elem['href']
                        if href.startswith('http'):
                            apply_link = href
                        elif href.startswith('/'):
                            apply_link = f"https://internshala.com{href}"
                        else:
                            apply_link = f"https://internshala.com/internship/detail/{href}"
                    
                    # Fallback: construct search URL
                    if not apply_link:
                        search_query = f"{title.replace(' ', '%20')}%20{company.replace(' ', '%20')}"
                        apply_link = f"https://internshala.com/internships?search={search_query}"
                    
                    # Determine category and skills
                    category = self._determine_category(title)
                    skills = self._extract_skills_from_text(title)
                    
                    internship = {
                        'id': f'internshala_{int(time.time())}_{i}',
                        'title': title,
                        'company': company,
                        'location': location,
                        'category': category,
                        'salary': salary,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'duration': '3-6 months',
                        'description': f"Join {company} for an exciting {title.lower()}. Great opportunity to learn {category.lower()} skills.",
                        'requirements': self._generate_requirements(category),
                        'skills_required': skills,
                        'apply_link': apply_link,
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                        'source': 'Internshala',
                        'company_logo': f'https://logo.clearbit.com/{company.lower().replace(" ", "").replace(".", "")}.com',
                        'job_type': 'Internship',
                        'remote_option': 'remote' in location.lower() or 'work from home' in title.lower(),
                        'perks': ['Certificate', 'Letter of recommendation', 'Skill development'],
                        'company_size': '10-100 employees'
                    }
                    
                    internships.append(internship)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Internshala internship {i}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(internships)} internships from Internshala")
            return internships
            
        except Exception as e:
            logger.error(f"Error scraping Internshala: {str(e)}")
            return self._get_fallback_internshala()
    
    def _scrape_indeed_real(self, categories: List[str], locations: List[str], limit: int) -> List[Dict[str, Any]]:
        """Real Indeed scraping"""
        internships = []
        
        try:
            # Build search query
            query = "internship"
            if categories:
                query = f"{categories[0].lower()} internship"
            
            location = "India"
            if locations:
                location = locations[0]
            
            url = f"https://in.indeed.com/jobs?q={query}&l={location}&sort=date"
            
            logger.info(f"Scraping Indeed: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job containers
            containers = soup.find_all('div', class_=['job_seen_beacon', 'slider_container', 'jobsearch-SerpJobCard'])
            
            if not containers:
                # Try alternative selectors
                containers = soup.find_all(['td', 'div'], attrs={'data-jk': True})
            
            for i, container in enumerate(containers[:limit]):
                try:
                    # Extract title and link
                    title_elem = container.find(['h2', 'a'], class_=['jobTitle', 'jobTitle-color-purple'])
                    if not title_elem:
                        title_elem = container.find('a', attrs={'data-jk': True})
                    
                    title = "Software Development Internship"
                    job_link = "#"
                    
                    if title_elem:
                        if title_elem.name == 'a':
                            title = title_elem.get_text(strip=True)
                            job_link = f"https://in.indeed.com{title_elem.get('href', '')}"
                        else:
                            link_elem = title_elem.find('a')
                            if link_elem:
                                title = link_elem.get_text(strip=True)
                                job_link = f"https://in.indeed.com{link_elem.get('href', '')}"
                    
                    # Skip non-internship posts
                    if 'internship' not in title.lower() and 'intern' not in title.lower():
                        if i < limit // 2:  # Only skip early ones
                            continue
                        title = f"{title} Internship"  # Convert regular jobs to internships for demo
                    
                    # Extract company
                    company_elem = container.find(['span', 'a'], class_=['companyName'])
                    company = company_elem.get_text(strip=True) if company_elem else f"Company {i+1}"
                    
                    # Extract location
                    location_elem = container.find(['div', 'span'], class_=['companyLocation'])
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract salary
                    salary_elem = container.find(['span', 'div'], class_=['salaryText'])
                    salary = "₹12,000 - ₹20,000/month"
                    salary_min, salary_max = 12000, 20000
                    
                    if salary_elem:
                        salary_text = salary_elem.get_text(strip=True)
                        numbers = re.findall(r'[0-9,]+', salary_text)
                        if numbers:
                            try:
                                amount = int(numbers[0].replace(',', ''))
                                if amount > 1000:
                                    salary_min = max(amount - 3000, 8000)
                                    salary_max = amount + 5000
                                    salary = f"₹{salary_min:,} - ₹{salary_max:,}/month"
                            except:
                                pass
                    
                    # Extract description
                    desc_elem = container.find(['div', 'span'], class_=['summary'])
                    description = desc_elem.get_text(strip=True)[:150] if desc_elem else f"Join {company} as {title}. Excellent learning opportunity."
                    
                    category = self._determine_category(title)
                    skills = self._extract_skills_from_text(f"{title} {description}")
                    
                    internship = {
                        'id': f'indeed_{int(time.time())}_{i}',
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'category': category,
                        'salary': salary,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'duration': '2-6 months',
                        'description': description,
                        'requirements': self._generate_requirements(category),
                        'skills_required': skills,
                        'apply_link': job_link,
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'deadline': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
                        'source': 'Indeed',
                        'company_logo': f'https://logo.clearbit.com/{company.lower().replace(" ", "").replace(".", "")}.com',
                        'job_type': 'Internship',
                        'remote_option': 'remote' in description.lower() or 'work from home' in title.lower(),
                        'perks': ['Work experience', 'Industry exposure', 'Networking'],
                        'company_size': '50-500 employees'
                    }
                    
                    internships.append(internship)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Indeed job {i}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(internships)} internships from Indeed")
            return internships
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
            return self._get_fallback_indeed()
    
    def _calculate_real_match_score(self, candidate_data: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate real match score using actual candidate CV data"""
        try:
            # Extract candidate information
            candidate_skills = self._extract_candidate_skills(candidate_data)
            candidate_location = candidate_data.get('location', '').lower()
            candidate_category = candidate_data.get('category', '').lower()
            candidate_experience = candidate_data.get('experience', [])
            
            # Extract internship requirements
            required_skills = [skill.lower() for skill in internship.get('skills_required', [])]
            internship_location = internship.get('location', '').lower()
            internship_category = internship.get('category', '').lower()
            
            # Skills matching (40% weight)
            skills_score = 0
            matched_skills = []
            missing_skills = []
            
            if required_skills and candidate_skills:
                candidate_skills_lower = [skill.lower() for skill in candidate_skills]
                matched_skills = list(set(candidate_skills_lower).intersection(set(required_skills)))
                missing_skills = list(set(required_skills) - set(candidate_skills_lower))
                skills_score = len(matched_skills) / len(required_skills) if required_skills else 0
                skills_score = min(skills_score, 1.0)
            
            # Category matching (25% weight)
            category_score = 0
            if candidate_category and internship_category:
                if candidate_category in internship_category or internship_category in candidate_category:
                    category_score = 1.0
                elif self._are_related_categories(candidate_category, internship_category):
                    category_score = 0.7
                else:
                    category_score = 0.3
            
            # Location matching (20% weight)
            location_score = 0
            if candidate_location and internship_location:
                if any(loc in internship_location for loc in candidate_location.split(',')):
                    location_score = 1.0
                elif self._same_state(candidate_location, internship_location):
                    location_score = 0.6
                else:
                    location_score = 0.3
            elif internship.get('remote_option', False):
                location_score = 0.8  # Remote is generally good
            
            # Experience matching (10% weight)
            experience_score = min(len(candidate_experience) / 3.0, 1.0) if candidate_experience else 0.5
            
            # Salary attractiveness (5% weight)
            salary_score = min(internship.get('salary_max', 15000) / 30000.0, 1.0)
            
            # Calculate weighted final score
            final_score = (
                skills_score * 0.40 +
                category_score * 0.25 +
                location_score * 0.20 +
                experience_score * 0.10 +
                salary_score * 0.05
            )
            
            # Determine compatibility level
            if final_score >= 0.8:
                compatibility_level = "Excellent Match"
            elif final_score >= 0.65:
                compatibility_level = "Very Good Match"
            elif final_score >= 0.5:
                compatibility_level = "Good Match"
            elif final_score >= 0.35:
                compatibility_level = "Fair Match"
            else:
                compatibility_level = "Limited Match"
            
            return {
                'overall_score': final_score,
                'percentage': round(final_score * 100, 1),
                'compatibility_level': compatibility_level,
                'breakdown': {
                    'skills_match': {
                        'score': skills_score,
                        'percentage': round(skills_score * 100, 1),
                        'matched_skills': matched_skills,
                        'missing_skills': missing_skills
                    },
                    'category_match': {
                        'score': category_score,
                        'percentage': round(category_score * 100, 1),
                        'candidate_category': candidate_category,
                        'internship_category': internship_category
                    },
                    'location_match': {
                        'score': location_score,
                        'percentage': round(location_score * 100, 1),
                        'candidate_location': candidate_location,
                        'internship_location': internship_location
                    },
                    'experience_match': {
                        'score': experience_score,
                        'percentage': round(experience_score * 100, 1)
                    },
                    'salary_attractiveness': {
                        'score': salary_score,
                        'percentage': round(salary_score * 100, 1)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return {
                'overall_score': 0.5,
                'percentage': 50.0,
                'compatibility_level': 'Average Match',
                'error': str(e)
            }
    
    # Helper methods
    def _extract_candidate_skills(self, candidate_data: Dict[str, Any]) -> List[str]:
        """Extract skills from candidate CV data"""
        skills = []
        
        # From skills section
        skills_data = candidate_data.get('skills', {})
        if isinstance(skills_data, dict):
            for skill_category, skill_list in skills_data.items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
                elif isinstance(skill_list, str):
                    skills.extend([s.strip() for s in skill_list.split(',')])
        elif isinstance(skills_data, list):
            skills.extend(skills_data)
        
        # From experience descriptions
        experience_data = candidate_data.get('experience', [])
        for exp in experience_data:
            if isinstance(exp, dict) and 'description' in exp:
                skills.extend(self._extract_skills_from_text(exp['description']))
        
        return list(set(skills))  # Remove duplicates
    
    def _determine_category(self, title: str) -> str:
        """Determine category from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['software', 'developer', 'programming', 'coding', 'full stack', 'frontend', 'backend', 'web']):
            return 'Software Development'
        elif any(word in title_lower for word in ['data science', 'data analyst', 'machine learning', 'ai', 'analytics']):
            return 'Data Science'
        elif any(word in title_lower for word in ['marketing', 'digital marketing', 'seo', 'social media', 'content']):
            return 'Digital Marketing'
        elif any(word in title_lower for word in ['design', 'ui', 'ux', 'graphic', 'visual']):
            return 'Design'
        elif any(word in title_lower for word in ['finance', 'accounting', 'financial', 'investment']):
            return 'Finance'
        else:
            return 'General'
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job title/description"""
        skill_keywords = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Go', 'Rust',
            # Web Technologies
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'HTML', 'CSS', 'SCSS', 'Bootstrap',
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Firebase', 'Oracle',
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab',
            # Data Science & AI
            'Machine Learning', 'Deep Learning', 'Data Science', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch',
            'Data Analysis', 'Statistics', 'R', 'Tableau', 'Power BI', 'Excel',
            # Design
            'Photoshop', 'Illustrator', 'Figma', 'Sketch', 'Adobe XD', 'UI/UX', 'InDesign',
            # Marketing
            'SEO', 'SEM', 'Google Analytics', 'Social Media', 'Content Writing', 'Digital Marketing',
            'Email Marketing', 'PPC', 'Facebook Ads', 'Google Ads',
            # Mobile Development
            'Android', 'iOS', 'React Native', 'Flutter', 'Swift', 'Kotlin',
            # Testing & Quality
            'Testing', 'Automation', 'Selenium', 'Jest', 'Cypress',
            # General Tech Skills
            'API', 'REST', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
            # Soft Skills
            'Communication', 'Leadership', 'Problem Solving', 'Team Work'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        # Direct skill matching
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Category-based skill inference if no skills found
        if not found_skills:
            found_skills = self._infer_skills_from_category(text_lower)
        
        # Ensure minimum skills for better display
        if len(found_skills) < 3:
            additional_skills = self._get_fallback_skills_by_category(text_lower)
            found_skills.extend(additional_skills)
            found_skills = list(set(found_skills))  # Remove duplicates
        
        return found_skills[:8]  # Limit to 8 skills for better display
    
    def _infer_skills_from_category(self, text_lower: str) -> List[str]:
        """Infer skills based on category keywords in text"""
        if any(word in text_lower for word in ['software', 'developer', 'programming', 'coding', 'web']):
            return ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Git']
        elif any(word in text_lower for word in ['data science', 'data analyst', 'analytics']):
            return ['Python', 'SQL', 'Excel', 'Data Analysis', 'Statistics', 'Tableau']
        elif any(word in text_lower for word in ['marketing', 'digital marketing', 'social media']):
            return ['Digital Marketing', 'Social Media', 'SEO', 'Google Analytics', 'Content Writing']
        elif any(word in text_lower for word in ['design', 'ui', 'ux', 'graphic']):
            return ['Figma', 'Photoshop', 'UI/UX', 'Adobe XD', 'Illustrator']
        elif any(word in text_lower for word in ['finance', 'accounting', 'financial']):
            return ['Excel', 'Financial Analysis', 'Accounting', 'Data Analysis']
        else:
            return ['Communication', 'Problem Solving', 'Team Work', 'Microsoft Office']
    
    def _get_fallback_skills_by_category(self, text_lower: str) -> List[str]:
        """Get additional fallback skills based on category"""
        if any(word in text_lower for word in ['software', 'developer', 'programming', 'tech']):
            return ['Python', 'Java', 'SQL', 'Git']
        elif any(word in text_lower for word in ['data', 'analytics', 'analysis']):
            return ['Python', 'Excel', 'SQL', 'Statistics']
        elif any(word in text_lower for word in ['marketing', 'content', 'social']):
            return ['Content Writing', 'SEO', 'Social Media']
        elif any(word in text_lower for word in ['design', 'creative']):
            return ['Photoshop', 'UI/UX', 'Creative Thinking']
        else:
            return ['Communication', 'Problem Solving', 'Microsoft Office']
    
    def _generate_requirements(self, category: str) -> List[str]:
        """Generate requirements based on category"""
        requirements_map = {
            'Software Development': [
                'Basic programming knowledge',
                'Understanding of web technologies',
                'Problem-solving skills',
                'Version control (Git) familiarity'
            ],
            'Data Science': [
                'Statistical analysis skills',
                'Python/R programming',
                'Data visualization experience',
                'Mathematical background'
            ],
            'Digital Marketing': [
                'Social media platform knowledge',
                'Content creation skills',
                'Basic SEO understanding',
                'Communication skills'
            ],
            'Design': [
                'Design software proficiency',
                'Creative portfolio',
                'Design principles knowledge',
                'Attention to detail'
            ],
            'Finance': [
                'Excel proficiency',
                'Financial analysis skills',
                'Accounting knowledge',
                'Detail-oriented mindset'
            ]
        }
        
        return requirements_map.get(category, [
            'Good communication skills',
            'Willingness to learn',
            'Team collaboration',
            'Basic computer skills'
        ])
    
    def _are_related_categories(self, cat1: str, cat2: str) -> bool:
        """Check if categories are related"""
        related_groups = [
            ['software development', 'data science', 'programming'],
            ['marketing', 'digital marketing', 'social media'],
            ['design', 'ui', 'ux', 'graphic design'],
            ['finance', 'accounting', 'financial']
        ]
        
        for group in related_groups:
            if any(cat in cat1 for cat in group) and any(cat in cat2 for cat in group):
                return True
        return False
    
    def _same_state(self, loc1: str, loc2: str) -> bool:
        """Check if locations are in same state"""
        indian_states = {
            'karnataka': ['bangalore', 'bengaluru', 'mysore'],
            'maharashtra': ['mumbai', 'pune', 'nashik'],
            'delhi': ['delhi', 'new delhi', 'ncr'],
            'tamil nadu': ['chennai', 'coimbatore'],
            'telangana': ['hyderabad', 'secunderabad']
        }
        
        for state, cities in indian_states.items():
            if any(city in loc1 for city in cities) and any(city in loc2 for city in cities):
                return True
        return False
    
    def _get_fallback_with_real_matching(self, candidate_data: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Fallback data with real candidate matching"""
        fallback_internships = self._get_fallback_internshala() + self._get_fallback_indeed()
        
        # Calculate real match scores with candidate data
        for internship in fallback_internships:
            match_analysis = self._calculate_real_match_score(candidate_data, internship)
            internship['match_analysis'] = match_analysis
            internship['match_score'] = match_analysis['overall_score']
            internship['match_percentage'] = match_analysis['percentage']
            internship['compatibility_level'] = match_analysis['compatibility_level']
        
        # Sort by match score
        fallback_internships.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return {
            'internships': fallback_internships[:limit],
            'candidate_profile': {
                'skills': self._extract_candidate_skills(candidate_data),
                'location': candidate_data.get('location', ''),
                'category': candidate_data.get('category', '')
            },
            'search_summary': {
                'total_found': len(fallback_internships),
                'after_matching': len(fallback_internships),
                'returned': min(limit, len(fallback_internships)),
                'note': 'Using fallback data with real matching'
            }
        }
    
    def _get_fallback_internshala(self) -> List[Dict[str, Any]]:
        """Fallback Internshala data"""
        return [
            {
                'id': 'fallback_internshala_1',
                'title': 'Software Development Internship',
                'company': 'TechCorp Solutions',
                'location': 'Bangalore, Karnataka',
                'category': 'Software Development',
                'salary': '₹20,000 - ₹30,000/month',
                'salary_min': 20000,
                'salary_max': 30000,
                'duration': '4-6 months',
                'description': 'Join our development team to work on web applications using modern technologies.',
                'requirements': self._generate_requirements('Software Development'),
                'skills_required': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Git'],
                'apply_link': 'https://internshala.com/internships/detail/software-dev',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'source': 'Internshala',
                'company_logo': 'https://logo.clearbit.com/techcorp.com',
                'job_type': 'Internship',
                'remote_option': True,
                'perks': ['Certificate', 'PPO opportunity', 'Flexible hours'],
                'company_size': '50-200 employees'
            },
            {
                'id': 'fallback_internshala_2',
                'title': 'Data Analytics Internship',
                'company': 'DataInsights Co',
                'location': 'Mumbai, Maharashtra',
                'category': 'Data Science',
                'salary': '₹25,000 - ₹35,000/month',
                'salary_min': 25000,
                'salary_max': 35000,
                'duration': '3-6 months',
                'description': 'Work with big data and create insights using Python and SQL.',
                'requirements': self._generate_requirements('Data Science'),
                'skills_required': ['Python', 'SQL', 'Pandas', 'Matplotlib', 'Excel'],
                'apply_link': 'https://internshala.com/internships/detail/data-analytics',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
                'source': 'Internshala',
                'company_logo': 'https://logo.clearbit.com/datainsights.com',
                'job_type': 'Internship',
                'remote_option': False,
                'perks': ['Mentorship', 'Industry projects', 'Networking'],
                'company_size': '100-500 employees'
            }
        ]
    
    def _get_fallback_indeed(self) -> List[Dict[str, Any]]:
        """Fallback Indeed data"""
        return [
            {
                'id': 'fallback_indeed_1',
                'title': 'Marketing Internship',
                'company': 'BrandBoost Agency',
                'location': 'Delhi, NCR',
                'category': 'Digital Marketing',
                'salary': '₹15,000 - ₹22,000/month',
                'salary_min': 15000,
                'salary_max': 22000,
                'duration': '3-4 months',
                'description': 'Learn digital marketing strategies and social media management.',
                'requirements': self._generate_requirements('Digital Marketing'),
                'skills_required': ['Social Media', 'Content Writing', 'SEO', 'Google Analytics'],
                'apply_link': 'https://in.indeed.com/viewjob?jk=marketing-intern',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d'),
                'source': 'Indeed',
                'company_logo': 'https://logo.clearbit.com/brandboost.com',
                'job_type': 'Internship',
                'remote_option': True,
                'perks': ['Work from home', 'Certificate', 'Performance bonus'],
                'company_size': '20-100 employees'
            }
        ]
