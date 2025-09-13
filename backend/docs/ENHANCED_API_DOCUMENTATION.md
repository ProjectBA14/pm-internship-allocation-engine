# Enhanced Internship API Documentation

## Overview
The Enhanced Internship API provides advanced internship discovery and matching capabilities with live scraping from multiple sources and intelligent AI-powered matching.

## Base URL
```
http://localhost:5000/api/smart-internships
```

## Authentication
Most endpoints require authentication. Include the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Smart Internship Search
**POST** `/search`

Performs intelligent internship search with live scraping and AI-powered matching.

#### Request Body
```json
{
  "candidate_profile": {
    "name": "John Doe",
    "skills": {
      "technical": ["Python", "Machine Learning", "TensorFlow"],
      "soft": ["Communication", "Problem Solving"]
    },
    "experience": ["AI Project", "Data Analysis"],
    "education": "B.Tech Computer Science",
    "location": "Bangalore",
    "category": "Artificial Intelligence"
  },
  "categories": ["Software Development", "Data Science", "AI/ML"],
  "locations": ["Bangalore", "Mumbai", "Remote"],
  "salary_min": 15000,
  "remote_preferred": true,
  "limit": 20
}
```

#### Response
```json
{
  "message": "Smart internship search completed",
  "search_summary": {
    "total_scraped": 150,
    "total_matched": 42,
    "returned": 20,
    "avg_match_score": 0.78,
    "top_categories": [
      ["Artificial Intelligence", 8],
      ["Software Development", 6],
      ["Data Science", 4]
    ],
    "salary_range": {
      "min": 15000,
      "max": 50000,
      "avg": 32500
    },
    "location_distribution": [
      ["Bangalore", 12],
      ["Mumbai", 5],
      ["Remote", 3]
    ]
  },
  "internships": [
    {
      "id": "intern_001",
      "title": "AI/ML Engineering Internship",
      "company": "TechCorp AI",
      "location": "Bangalore, Karnataka",
      "category": "Artificial Intelligence",
      "salary": "₹30,000 - ₹45,000/month",
      "salary_min": 30000,
      "salary_max": 45000,
      "description": "Join our AI team to work on cutting-edge machine learning projects...",
      "skills_required": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
      "apply_link": "https://techcorp.com/careers/ai-intern",
      "posted_date": "2025-01-10",
      "deadline": "2025-02-15",
      "remote_option": true,
      "match_analysis": {
        "overall_score": 0.89,
        "percentage": 89,
        "compatibility_level": "Excellent",
        "skill_match": {
          "score": 0.92,
          "matched_skills": ["Python", "Machine Learning", "TensorFlow"],
          "missing_skills": ["PyTorch"],
          "explanation": "Strong technical skill alignment with 3/4 required skills"
        },
        "location_match": {
          "score": 1.0,
          "preferred_location": "Bangalore",
          "explanation": "Perfect location match"
        },
        "experience_match": {
          "score": 0.85,
          "relevant_experience": ["AI Project"],
          "explanation": "Good relevant project experience"
        },
        "category_match": {
          "score": 1.0,
          "explanation": "Perfect category alignment - AI/ML"
        },
        "salary_attractiveness": {
          "score": 0.8,
          "explanation": "Competitive salary range"
        }
      },
      "match_score": 0.89,
      "match_percentage": 89,
      "compatibility_level": "Excellent"
    }
  ]
}
```

### 2. Internship Details
**GET** `/{internship_id}`

Get comprehensive details about a specific internship.

#### Response
```json
{
  "internship": {
    "id": "intern_001",
    "title": "AI/ML Engineering Internship",
    "company": "InnovateTech AI",
    "location": "Hyderabad, Telangana",
    "category": "Artificial Intelligence",
    "salary": "₹25,000 - ₹40,000/month",
    "salary_min": 25000,
    "salary_max": 40000,
    "duration": "6 months",
    "description": "Detailed HTML description with formatting...",
    "requirements": [
      "Strong Python programming skills (2+ years)",
      "Experience with TensorFlow or PyTorch",
      "Understanding of ML algorithms and deep learning"
    ],
    "skills_required": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
    "nice_to_have": ["MLOps", "Docker", "Kubernetes", "AWS/GCP"],
    "apply_link": "https://innovatetech.ai/careers/ai-ml-internship",
    "posted_date": "2025-01-11",
    "deadline": "2025-02-25",
    "source": "Company Career Page",
    "company_info": {
      "name": "InnovateTech AI",
      "logo": "https://innovatetech.ai/logo.png",
      "size": "100-500 employees",
      "founded": "2019",
      "industry": "Artificial Intelligence",
      "website": "https://innovatetech.ai",
      "description": "Leading AI research and development company...",
      "rating": 4.8,
      "reviews_count": 127,
      "culture_highlights": [
        "Innovation-driven environment",
        "Flexible working hours"
      ]
    },
    "job_type": "Internship",
    "remote_option": true,
    "work_arrangement": "Hybrid (3 days office, 2 days remote)",
    "perks": [
      "High stipend (₹25,000 - ₹40,000/month)",
      "Mentorship by industry experts",
      "Pre-placement offer (PPO) opportunity"
    ],
    "application_process": [
      "Online application with resume",
      "Technical assessment (coding + ML concepts)",
      "Technical interview with team lead"
    ],
    "team_info": {
      "team_size": 15,
      "reporting_to": "Senior ML Engineer",
      "collaboration_with": ["Data Engineers", "Product Managers"]
    },
    "technologies_used": [
      "Python", "TensorFlow", "PyTorch", "Docker", "Kubernetes"
    ]
  },
  "fetched_at": "2025-01-13T10:30:00Z"
}
```

### 3. Recommended Internships
**POST** `/recommendations`

Get personalized internship recommendations with career insights.

#### Request Body
```json
{
  "candidate_profile": {
    "name": "Jane Smith",
    "skills": {
      "technical": ["Java", "Spring Boot", "React"],
      "soft": ["Leadership", "Communication"]
    },
    "experience": ["Full-stack Project", "Backend Development"],
    "education": "B.Tech Information Technology",
    "location": "Mumbai",
    "category": "Software Development"
  }
}
```

#### Response
```json
{
  "recommendations": [
    {
      "id": "intern_002",
      "title": "Full Stack Development Internship",
      "company": "WebTech Solutions",
      "match_analysis": {
        "overall_score": 0.87,
        "percentage": 87,
        "compatibility_level": "Excellent"
      },
      "match_score": 0.87,
      "match_percentage": 87
      // ... other internship fields
    }
  ],
  "insights": {
    "total_analyzed": 50,
    "qualified_matches": 15,
    "top_recommendations": 10,
    "best_match_score": 87,
    "avg_match_score": 0.76,
    "categories_matched": ["Software Development", "Web Development"],
    "skills_in_demand": [
      ["React", 8],
      ["Node.js", 7],
      ["Python", 6]
    ],
    "career_advice": [
      "Consider learning these in-demand skills: Node.js, Python, Docker",
      "Great opportunities in software development - you're in a growing field!"
    ]
  },
  "candidate_strengths": ["Java", "Spring Boot", "Full-stack Development"],
  "generated_at": "2025-01-13T10:30:00Z"
}
```

---

## Match Analysis Scoring

The AI matching system evaluates candidates across multiple dimensions:

### 1. Skill Match (Weight: 35%)
- **Exact matches**: Perfect skill name alignment
- **Semantic matches**: Related skills (e.g., "ML" matches "Machine Learning")
- **Missing critical skills**: Penalties for missing required skills

### 2. Location Match (Weight: 20%)
- **Perfect match**: Same city/state
- **Regional match**: Same state/region
- **Remote compatibility**: Remote work preference alignment

### 3. Experience Match (Weight: 20%)
- **Direct experience**: Relevant project/work experience
- **Transferable skills**: Related experience that applies
- **Academic projects**: University/personal projects

### 4. Category Match (Weight: 15%)
- **Primary category**: Direct field alignment
- **Related categories**: Adjacent or overlapping fields
- **Career transition**: Different but related paths

### 5. Salary Attractiveness (Weight: 10%)
- **Competitive range**: Above-market compensation
- **Fair compensation**: Market-rate salary
- **Growth potential**: Learning vs. immediate compensation

## Compatibility Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 0.85 - 1.0  | Excellent | Perfect or near-perfect match |
| 0.70 - 0.84 | Very Good | Strong match with minor gaps |
| 0.55 - 0.69 | Good | Decent match, some skill development needed |
| 0.40 - 0.54 | Fair | Moderate match, significant learning required |
| 0.0 - 0.39  | Poor | Limited compatibility |

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "details": "Candidate profile is required",
  "status_code": 400
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to perform smart search",
  "details": "Service temporarily unavailable",
  "status_code": 500
}
```

---

## Rate Limits

- **Search**: 10 requests per minute per user
- **Details**: 50 requests per minute per user  
- **Recommendations**: 5 requests per minute per user

## Data Sources

The system scrapes live data from:
- **Internshala**: Primary internship marketplace
- **Indeed**: Job and internship listings
- **LinkedIn**: Professional opportunities
- **Naukri**: Career portal
- **Company career pages**: Direct postings

## Caching

- **Search results**: Cached for 5 minutes
- **Company data**: Cached for 1 hour
- **Match scores**: Computed fresh each time

---

## Usage Examples

### Python Example
```python
import requests

# Smart search
search_data = {
    "candidate_profile": {
        "skills": {"technical": ["Python", "Django"]},
        "category": "Software Development"
    },
    "categories": ["Software Development"],
    "limit": 10
}

response = requests.post(
    "http://localhost:5000/api/smart-internships/search",
    json=search_data,
    headers={"Authorization": "Bearer your_token"}
)

internships = response.json()["internships"]
```

### JavaScript Example
```javascript
const searchInternships = async () => {
  const response = await fetch('/api/smart-internships/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
      candidate_profile: {
        skills: { technical: ['React', 'Node.js'] },
        category: 'Web Development'
      },
      categories: ['Software Development'],
      limit: 15
    })
  });
  
  const data = await response.json();
  return data.internships;
};
```
