/**
 * CV-Integrated Internship API Service
 * Handles API calls for CV-based internship matching with live scraping
 */

const API_BASE_URL = 'http://localhost:5000';

// Types for API requests and responses
export interface CandidateData {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  category?: string;
  skills?: {
    technical?: string[];
    soft?: string[];
    languages?: string[];
    tools?: string[];
  };
  experience?: Array<{
    title?: string;
    company?: string;
    duration?: string;
    description?: string;
  }>;
  education?: Array<{
    degree?: string;
    institution?: string;
    year?: string;
    field_of_study?: string;
  }>;
  key_strengths?: string[];
}

export interface SearchPreferences {
  categories?: string[];
  locations?: string[];
  salary_min?: number;
  remote_preferred?: boolean;
}

export interface CVIntegratedSearchRequest {
  candidate_id?: string;
  candidate_data?: CandidateData;
  search_preferences?: SearchPreferences;
  limit?: number;
}

export interface InternshipMatch {
  id: string;
  title: string;
  company: string;
  location: string;
  category: string;
  description: string;
  skills_required: string[];
  salary_min?: number;
  salary_max?: number;
  remote_option?: boolean;
  application_deadline?: string;
  apply_link?: string;
  source?: string;
  match_score?: number;
  match_percentage?: number;
  compatibility_level?: string;
  // Company enrichment data
  company_rating?: number;
  company_reviews_count?: number;
  glassdoor_rating?: number;
  work_life_balance_rating?: number;
  career_opportunities_rating?: number;
  interview_difficulty?: number;
  mentorship_quality?: string;
  learning_opportunities?: string;
  conversion_rate?: string;
  typical_projects?: string[];
  company_data?: any;
  match_analysis?: {
    breakdown: {
      skills_match: {
        percentage: number;
        matched_skills: string[];
        missing_skills: string[];
        score: number;
      };
      location_match: {
        percentage: number;
        score: number;
      };
      category_match: {
        percentage: number;
        score: number;
      };
      experience_match: {
        percentage: number;
        score: number;
      };
    };
  };
}

export interface CVIntegratedSearchResponse {
  message: string;
  candidate_insights: {
    name: string;
    top_skills: string[];
    experience_level: number;
    preferred_category: string;
    location: string;
  };
  search_results: {
    total_found: number;
    after_filtering: number;
    avg_match_percentage: number;
    best_match_percentage: number;
    excellent_matches: number;
    good_matches: number;
  };
  internships: InternshipMatch[];
  matching_powered_by: string;
}

export interface PersonalizedRecommendationsRequest {
  candidate_data: CandidateData;
  recommendation_type?: 'skills_based' | 'location_based' | 'category_based';
  limit?: number;
}

export interface PersonalizedRecommendationsResponse {
  recommendations: InternshipMatch[];
  recommendation_insights: {
    type: string;
    based_on_skills: string[];
    skills_gap_analysis: {
      missing_skills: string[];
      skill_match_percentage: number;
    };
    career_advice: string[];
    market_insights: {
      total_opportunities: number;
      avg_match_percentage: number;
      top_companies: string[];
      trending_skills: string[];
    };
  };
  powered_by: string;
}

export interface CVMatchAnalysisRequest {
  candidate_data: CandidateData;
  internship: {
    title: string;
    company: string;
    skills_required: string[];
    location: string;
    category: string;
    salary_max?: number;
  };
}

export interface CVMatchAnalysisResponse {
  match_analysis: {
    percentage: number;
    compatibility_level: string;
    breakdown: any;
  };
  detailed_feedback: {
    overall_assessment: string;
    match_percentage: number;
    strengths: string[];
    areas_for_improvement: string[];
    specific_recommendations: Array<{
      type: string;
      priority: string;
      action: string;
      impact: string;
    }>;
  };
  score_breakdown: {
    skills: {
      score: number;
      matched_skills: string[];
      missing_skills: string[];
    };
    category: {
      score: number;
      alignment: string;
    };
    location: {
      score: number;
      compatibility: string;
    };
  };
  application_readiness: {
    ready_to_apply: boolean;
    confidence_level: string;
    estimated_success_rate: string;
  };
}

export interface LiveInternshipFeedResponse {
  internships: Array<{
    id: string;
    title: string;
    company: string;
    location: string;
    category: string;
    description: string;
    skills_required: string[];
    salary_min?: number;
    salary_max?: number;
    remote_option?: boolean;
    application_deadline?: string;
  }>;
  feed_info: {
    total_found: number;
    category_filter: string;
    location_filter: string;
    last_updated: string;
    data_sources: string[];
  };
  note: string;
}

class CVIntegratedApiService {
  private baseUrl = API_BASE_URL;

  /**
   * Search internships using uploaded CV data for real matching
   */
  async searchInternshipsWithCV(request: CVIntegratedSearchRequest): Promise<CVIntegratedSearchResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cv-integrated/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search internships with CV');
      }

      return await response.json();
    } catch (error) {
      console.error('Error in CV-integrated search:', error);
      throw error;
    }
  }

  /**
   * Get personalized recommendations based on uploaded CV
   */
  async getPersonalizedRecommendations(request: PersonalizedRecommendationsRequest): Promise<PersonalizedRecommendationsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cv-integrated/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get personalized recommendations');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting personalized recommendations:', error);
      throw error;
    }
  }

  /**
   * Analyze how well a specific internship matches the candidate's CV
   */
  async analyzeCVMatch(request: CVMatchAnalysisRequest): Promise<CVMatchAnalysisResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/cv-integrated/match-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze CV match');
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing CV match:', error);
      throw error;
    }
  }

  /**
   * Get live internship feed with real-time scraping
   */
  async getLiveInternshipFeed(
    category?: string,
    location?: string,
    limit?: number
  ): Promise<LiveInternshipFeedResponse> {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (location) params.append('location', location);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/cv-integrated/live-feed?${params.toString()}`, {
        method: 'GET',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get live internship feed');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting live internship feed:', error);
      throw error;
    }
  }

  /**
   * Helper method to convert legacy parsed data to candidate data format
   */
  static convertParsedDataToCandidateData(parsedData: any): CandidateData {
    return {
      name: parsedData.name,
      email: parsedData.email,
      phone: parsedData.phone,
      location: parsedData.location,
      category: parsedData.category,
      skills: {
        technical: parsedData.skills?.technical || [],
        soft: parsedData.skills?.soft || [],
        languages: parsedData.skills?.languages || [],
        tools: parsedData.skills?.tools || [],
      },
      experience: parsedData.experience?.map((exp: any) => ({
        title: exp.job_title || exp.title,
        company: exp.company,
        duration: exp.duration,
        description: exp.description,
      })) || [],
      education: parsedData.education?.map((edu: any) => ({
        degree: edu.degree,
        institution: edu.institution,
        year: edu.year,
        field_of_study: edu.field_of_study || edu.field,
      })) || [],
      key_strengths: parsedData.key_strengths || [],
    };
  }
}

// Export singleton instance
export const cvIntegratedApiService = new CVIntegratedApiService();
export default cvIntegratedApiService;
