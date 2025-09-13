import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Paper,
  Chip,
} from '@mui/material';
import {
  SmartToy,
  Speed,
  Assessment,
  Security,
  CloudUpload,
  Analytics,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <SmartToy color="primary" />,
      title: 'AI-Powered Matching',
      description: 'Advanced AI models analyze CVs and match candidates to optimal internship opportunities',
    },
    {
      icon: <Speed color="primary" />,
      title: 'Automated CV Parsing',
      description: 'Google Gemini AI extracts key information from uploaded CVs automatically',
    },
    {
      icon: <Assessment color="primary" />,
      title: 'Affirmative Action',
      description: 'Built-in quota management ensures diversity and representation in allocations',
    },
    {
      icon: <Security color="primary" />,
      title: 'Secure & Scalable',
      description: 'Firebase backend ensures data security and real-time synchronization',
    },
    {
      icon: <CloudUpload color="primary" />,
      title: 'Easy Upload',
      description: 'Simple drag-and-drop CV upload with support for PDF and DOC formats',
    },
    {
      icon: <Analytics color="primary" />,
      title: 'Rich Analytics',
      description: 'Comprehensive reporting and analytics for administrators and stakeholders',
    },
  ];

  const stats = [
    { label: 'AI Models Integrated', value: '2+' },
    { label: 'Quota Categories', value: '5' },
    { label: 'File Formats Supported', value: '3' },
    { label: 'Real-time Updates', value: '✓' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to our Project
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: '800px', mx: 'auto' }}>
          An AI-powered smart allocation system for matching students to internship opportunities 
          under the PM Internship Scheme
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            size="large" 
            onClick={() => navigate('/applicant')}
            sx={{ minWidth: 180 }}
          >
            Apply for Internship
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            onClick={() => navigate('/admin')}
            sx={{ minWidth: 180 }}
          >
            Admin Dashboard
          </Button>
        </Box>
      </Box>

      {/* Statistics */}
      <Paper sx={{ p: 3, mb: 6, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)' }}>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
          gap: 3
        }}>
          {stats.map((stat, index) => (
            <Box key={index}>
              <Box sx={{ textAlign: 'center', color: 'white' }}>
                <Typography variant="h4" component="div" fontWeight="bold">
                  {stat.value}
                </Typography>
                <Typography variant="body2">
                  {stat.label}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Features Grid */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom textAlign="center" sx={{ mb: 4 }}>
          Key Features
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr', lg: '1fr 1fr 1fr' },
          gap: 3
        }}>
          {features.map((feature, index) => (
            <Box key={index}>
              <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
        </Box>
      </Box>

      {/* Technology Stack */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom textAlign="center" sx={{ mb: 4 }}>
          Technology Stack
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 2
        }}>
          <Box>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🎨 Frontend
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="React.js" color="primary" variant="outlined" />
                  <Chip label="TypeScript" color="primary" variant="outlined" />
                  <Chip label="Material-UI" color="primary" variant="outlined" />
                  <Chip label="React Router" color="primary" variant="outlined" />
                </Box>
              </CardContent>
            </Card>
          </Box>
          <Box>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ⚡ Backend
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="Flask" color="secondary" variant="outlined" />
                  <Chip label="Python" color="secondary" variant="outlined" />
                  <Chip label="Firebase" color="secondary" variant="outlined" />
                  <Chip label="Google Gemini AI" color="secondary" variant="outlined" />
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>

      {/* Call to Action */}
      <Paper 
        sx={{ 
          p: 4, 
          textAlign: 'center', 
          background: 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
        }}
      >
        <Typography variant="h5" gutterBottom>
          Ready to Get Started?
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Whether you're a student looking for internships or an admin managing allocations,
          our platform makes the process simple and efficient.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            size="large" 
            onClick={() => navigate('/cv-upload')}
          >
            Upload Your CV
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            onClick={() => navigate('/internships')}
          >
            Browse Internships
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Home;
