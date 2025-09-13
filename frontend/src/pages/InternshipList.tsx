import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Chip,
  Box,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  AlertTitle,
  LinearProgress,
} from '@mui/material';
import { 
  Search, 
  LocationOn, 
  Business, 
  Category, 
  TrendingUp,
  WorkOutline,
  MonetizationOn,
  Schedule,
  Star,
  Refresh,
  StarBorder,
  Info,
  School,
  Assessment,
} from '@mui/icons-material';
import cvIntegratedApiService, { 
  InternshipMatch, 
  CandidateData
} from '../services/cvIntegratedApi';

// Use InternshipMatch from the API service
type Internship = InternshipMatch;

const InternshipList: React.FC = () => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [cvIntegratedMode, setCvIntegratedMode] = useState(false);
  const [candidateData, setCandidateData] = useState<CandidateData | null>(null);
  const [feedInfo, setFeedInfo] = useState<any>(null);

  // Load CV data from localStorage if available
  useEffect(() => {
    const storedCVData = localStorage.getItem('parsedCVData');
    if (storedCVData) {
      try {
        const cvData = JSON.parse(storedCVData);
        // Convert parsed CV data to candidate format
        const candidateData = {
          name: cvData.name,
          email: cvData.email,
          phone: cvData.phone,
          location: cvData.location,
          category: cvData.category,
          skills: {
            technical: cvData.skills?.technical || [],
            soft: cvData.skills?.soft || [],
            languages: cvData.skills?.languages || [],
            tools: cvData.skills?.tools || [],
          },
          experience: cvData.experience?.map((exp: any) => ({
            title: exp.job_title || exp.title,
            company: exp.company,
            duration: exp.duration,
            description: exp.description,
          })) || [],
          education: cvData.education?.map((edu: any) => ({
            degree: edu.degree,
            institution: edu.institution,
            year: edu.year,
            field_of_study: edu.field_of_study || edu.field,
          })) || [],
          key_strengths: cvData.key_strengths || [],
        };
        setCandidateData(candidateData);
        setCvIntegratedMode(true);
      } catch (error) {
        console.error('Error loading CV data:', error);
      }
    }
  }, []);

  // Load internships (live feed or CV-integrated)
  const loadInternships = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (cvIntegratedMode && candidateData) {
        // Use CV-integrated search
        const response = await cvIntegratedApiService.searchInternshipsWithCV({
          candidate_data: candidateData,
          search_preferences: {
            categories: categoryFilter ? [categoryFilter] : [],
            locations: locationFilter ? [locationFilter] : [],
          },
          limit: 20
        });
        
        setInternships(response.internships);
        setFeedInfo({
          powered_by: response.matching_powered_by,
          candidate_insights: response.candidate_insights,
          search_results: response.search_results
        });
      } else {
        // Use live feed
        const response = await cvIntegratedApiService.getLiveInternshipFeed(
          categoryFilter,
          locationFilter,
          20
        );
        
        setInternships(response.internships);
        setFeedInfo({
          powered_by: 'Live Web Scraping',
          feed_info: response.feed_info,
          note: response.note
        });
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load internships');
      console.error('Error loading internships:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load internships on component mount and when filters change
  useEffect(() => {
    loadInternships();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cvIntegratedMode, categoryFilter, locationFilter, candidateData]);

  // Filter internships by search term (API already handles category and location filters)
  const filteredInternships = internships.filter((internship) => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      internship.title.toLowerCase().includes(searchLower) ||
      internship.company.toLowerCase().includes(searchLower) ||
      internship.description.toLowerCase().includes(searchLower) ||
      internship.skills_required.some(skill => 
        skill.toLowerCase().includes(searchLower)
      )
    );
  });

  // Get available categories and locations from current internships
  const categories = Array.from(new Set(internships.map(i => i.category)));
  const locations = Array.from(new Set(internships.map(i => i.location)));
  
  // Helper function to get match percentage color
  const getMatchColor = (percentage?: number) => {
    if (!percentage) return 'default';
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };
  
  // Helper function to format salary
  const formatSalary = (min?: number, max?: number) => {
    if (max) {
      return min ? `₹${min.toLocaleString()} - ₹${max.toLocaleString()}` : `Up to ₹${max.toLocaleString()}`;
    }
    if (min) {
      return `From ₹${min.toLocaleString()}`;
    }
    return 'Salary not specified';
  };
  
  // Helper function to get fallback skills by category
  const getFallbackSkills = (category: string): string[] => {
    const categoryLower = category.toLowerCase();
    
    if (categoryLower.includes('software') || categoryLower.includes('development')) {
      return ['JavaScript', 'HTML', 'CSS', 'React'];
    } else if (categoryLower.includes('data')) {
      return ['Python', 'SQL', 'Excel', 'Analytics'];
    } else if (categoryLower.includes('marketing')) {
      return ['SEO', 'Social Media', 'Content Writing'];
    } else if (categoryLower.includes('design')) {
      return ['Figma', 'Photoshop', 'UI/UX'];
    } else if (categoryLower.includes('finance')) {
      return ['Excel', 'Accounting', 'Analysis'];
    } else {
      return ['Communication', 'Problem Solving', 'Team Work'];
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        {cvIntegratedMode ? 'Personalized Internship Matches' : 'Live Internship Feed'}
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 2 }}>
        {cvIntegratedMode 
          ? 'Smart matching based on your uploaded CV and real-time job market data'
          : 'Live internship opportunities from top companies across India'
        }
      </Typography>
      
      {/* CV Integration Toggle and Info */}
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mb: 3, gap: 2 }}>
        {candidateData && (
          <FormControlLabel
            control={
              <Switch
                checked={cvIntegratedMode}
                onChange={(e) => setCvIntegratedMode(e.target.checked)}
                color="primary"
              />
            }
            label={cvIntegratedMode ? 'CV-Matched Results' : 'General Feed'}
          />
        )}
        
        <Button
          startIcon={<Refresh />}
          onClick={loadInternships}
          disabled={loading}
          size="small"
        >
          Refresh
        </Button>
      </Box>
      
      {/* Loading Progress */}
      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" textAlign="center" sx={{ mt: 1 }}>
            {cvIntegratedMode ? 'Finding personalized matches...' : 'Loading live internships...'}
          </Typography>
        </Box>
      )}
      
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}
      
      {/* Feed Information */}
      {feedInfo && !loading && (
        <Alert 
          severity={cvIntegratedMode ? 'success' : 'info'} 
          sx={{ mb: 3 }}
          icon={cvIntegratedMode ? <TrendingUp /> : <WorkOutline />}
        >
          <AlertTitle>
            {cvIntegratedMode ? 
              `Hey ${feedInfo.candidate_insights?.name}! We found ${feedInfo.search_results?.total_found} matches` :
              `Live Feed • ${feedInfo.feed_info?.total_found} internships found`
            }
          </AlertTitle>
          {cvIntegratedMode ? (
            <Typography variant="body2">
              {feedInfo.search_results?.excellent_matches} excellent matches (80%+) • 
              {feedInfo.search_results?.good_matches} good matches (60%+) • 
              Avg match: {Math.round(feedInfo.search_results?.avg_match_percentage || 0)}%
            </Typography>
          ) : (
            <Typography variant="body2">
              {feedInfo.note} • Sources: {feedInfo.feed_info?.data_sources?.join(', ')}
            </Typography>
          )}
        </Alert>
      )}

      {/* Filters */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '2fr 1fr 1fr' },
        gap: 2,
        mb: 4
      }}>
        <Box>
          <TextField
            fullWidth
            placeholder="Search internships..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Box>
        <Box>
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              label="Category"
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
        <Box>
          <FormControl fullWidth>
            <InputLabel>Location</InputLabel>
            <Select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              label="Location"
            >
              <MenuItem value="">All Locations</MenuItem>
              {locations.map((location) => (
                <MenuItem key={location} value={location}>
                  {location}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Internship Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr', lg: '1fr 1fr 1fr' },
        gap: 3
      }}>
        {filteredInternships.map((internship) => (
          <Box key={internship.id}>
            <Card 
              sx={{ 
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}
            >
              <CardContent>
                {/* Header with Match Score */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h2" sx={{ flex: 1, pr: 1 }}>
                    {internship.title}
                  </Typography>
                  {cvIntegratedMode && internship.match_percentage && (
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 0.5,
                      bgcolor: getMatchColor(internship.match_percentage) === 'success' ? 'success.main' :
                               getMatchColor(internship.match_percentage) === 'warning' ? 'warning.main' : 'error.main',
                      color: 'white',
                      px: 1.5,
                      py: 0.5,
                      borderRadius: 2,
                      fontWeight: 'bold'
                    }}>
                      <Star sx={{ fontSize: 16 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {Math.round(internship.match_percentage)}% Match
                      </Typography>
                    </Box>
                  )}
                </Box>
                
                {/* Company and Location */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Business sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {internship.company}
                    </Typography>
                    {/* Company Rating */}
                    {internship.company_rating && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                        <Star sx={{ fontSize: 12, color: 'warning.main' }} />
                        <Typography variant="caption" color="text.secondary">
                          {internship.company_rating}/5.0
                        </Typography>
                        {internship.company_reviews_count && (
                          <Typography variant="caption" color="text.secondary">
                            ({internship.company_reviews_count.toLocaleString()} reviews)
                          </Typography>
                        )}
                      </Box>
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    {internship.source && (
                      <Chip 
                        label={internship.source} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ fontSize: '0.7rem', height: 20 }}
                      />
                    )}
                    {internship.remote_option && (
                      <Chip label="Remote" size="small" color="success" variant="outlined" />
                    )}
                    {internship.mentorship_quality && internship.mentorship_quality === 'High' && (
                      <Chip label="Great Mentorship" size="small" color="info" variant="outlined" />
                    )}
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LocationOn sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    {internship.location}
                  </Typography>
                </Box>

                {/* Category and Salary */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Category sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
                    {internship.category}
                  </Typography>
                </Box>
                
                {(internship.salary_min || internship.salary_max) && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <MonetizationOn sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {formatSalary(internship.salary_min, internship.salary_max)}/month
                    </Typography>
                  </Box>
                )}

                {/* Description */}
                <Typography variant="body2" sx={{ mb: 2, fontSize: '0.875rem' }}>
                  {internship.description.length > 120 
                    ? `${internship.description.substring(0, 120)}...`
                    : internship.description
                  }
                </Typography>

                {/* Skills */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" display="block" gutterBottom fontWeight="medium">
                    Required Skills:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(internship.skills_required && internship.skills_required.length > 0) ? (
                      <>
                        {internship.skills_required.slice(0, 4).map((skill, index) => {
                          // Highlight matched skills in CV mode
                          const isMatched = cvIntegratedMode && 
                            candidateData?.skills?.technical?.some(candidateSkill => 
                              candidateSkill.toLowerCase().includes(skill.toLowerCase())
                            );
                          
                          return (
                            <Chip 
                              key={index} 
                              label={skill} 
                              size="small" 
                              variant={isMatched ? "filled" : "outlined"}
                              color={isMatched ? "primary" : "default"}
                              sx={{ fontSize: '0.75rem' }}
                            />
                          );
                        })}
                        {internship.skills_required.length > 4 && (
                          <Chip
                            label={`+${internship.skills_required.length - 4} more`}
                            size="small"
                            variant="outlined"
                            color="default"
                            sx={{ fontSize: '0.75rem' }}
                          />
                        )}
                      </>
                    ) : (
                      // Fallback skills based on category
                      <>
                        {getFallbackSkills(internship.category).map((skill, index) => (
                          <Chip 
                            key={index} 
                            label={skill} 
                            size="small" 
                            variant="outlined"
                            color="default"
                            sx={{ fontSize: '0.75rem', opacity: 0.7 }}
                          />
                        ))}
                      </>
                    )}
                  </Box>
                </Box>

                {/* Application Deadline */}
                {internship.application_deadline && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Schedule sx={{ fontSize: 16, mr: 1, color: 'warning.main' }} />
                    <Typography variant="caption" color="warning.main" fontWeight="medium">
                      Apply by: {new Date(internship.application_deadline).toLocaleDateString()}
                    </Typography>
                  </Box>
                )}

                {/* Match Analysis Preview (CV Mode Only) */}
                {cvIntegratedMode && internship.match_analysis && (
                  <Box sx={{ mb: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="caption" fontWeight="bold" display="block" gutterBottom>
                      Match Breakdown:
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, fontSize: '0.75rem' }}>
                      <Typography variant="caption">
                        Skills: {Math.round(internship.match_analysis.breakdown.skills_match.percentage)}%
                      </Typography>
                      <Typography variant="caption">
                        Location: {Math.round(internship.match_analysis.breakdown.location_match.percentage)}%
                      </Typography>
                    </Box>
                  </Box>
                )}
                
                {/* Company Insights */}
                {internship.learning_opportunities && (
                  <Box sx={{ mb: 2, p: 1.5, bgcolor: 'info.50', borderRadius: 1 }}>
                    <Typography variant="caption" fontWeight="bold" display="block" gutterBottom>
                      🎓 Internship Insights:
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      {internship.learning_opportunities && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <School sx={{ fontSize: 12 }} />
                          <Typography variant="caption">
                            Learning: {internship.learning_opportunities}
                          </Typography>
                        </Box>
                      )}
                      {internship.conversion_rate && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <TrendingUp sx={{ fontSize: 12 }} />
                          <Typography variant="caption">
                            Full-time conversion: {internship.conversion_rate}
                          </Typography>
                        </Box>
                      )}
                      {internship.interview_difficulty && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Assessment sx={{ fontSize: 12 }} />
                          <Typography variant="caption">
                            Interview difficulty: {internship.interview_difficulty}/5.0
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>
                )}

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 'auto' }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {cvIntegratedMode && internship.compatibility_level && (
                      <Chip 
                        label={internship.compatibility_level} 
                        size="small"
                        color={internship.compatibility_level === 'Excellent' ? 'success' : 
                               internship.compatibility_level === 'Good' ? 'warning' : 'default'}
                        variant="filled"
                      />
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {internship.apply_link && internship.apply_link !== '#' && (
                      <Button 
                        variant="outlined" 
                        size="small"
                        onClick={() => {
                          window.open(internship.apply_link, '_blank', 'noopener,noreferrer');
                        }}
                      >
                        View Details
                      </Button>
                    )}
                    <Button 
                      variant="contained" 
                      size="small"
                      sx={{ minWidth: 80 }}
                      onClick={() => {
                        if (internship.apply_link && internship.apply_link !== '#') {
                          window.open(internship.apply_link, '_blank', 'noopener,noreferrer');
                        } else {
                          // Fallback: search for the job on the source site
                          const searchQuery = encodeURIComponent(`${internship.title} ${internship.company} internship`);
                          const fallbackUrl = internship.source === 'Internshala' 
                            ? `https://internshala.com/internships?search=${searchQuery}`
                            : `https://indeed.com/jobs?q=${searchQuery}`;
                          window.open(fallbackUrl, '_blank', 'noopener,noreferrer');
                        }
                      }}
                    >
                      Apply
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {filteredInternships.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No internships found matching your criteria
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default InternshipList;
