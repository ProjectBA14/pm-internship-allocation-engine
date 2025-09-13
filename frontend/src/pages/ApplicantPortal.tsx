import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
} from '@mui/material';
import { CloudUpload, Work, Assessment, Person } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const ApplicantPortal: React.FC = () => {
  const navigate = useNavigate();

  const actions = [
    {
      title: 'Upload CV',
      description: 'Upload your CV for AI-powered parsing and profile creation',
      icon: <CloudUpload />,
      action: () => navigate('/cv-upload'),
      color: 'primary',
    },
    {
      title: 'Browse Internships',
      description: 'Explore available internship opportunities',
      icon: <Work />,
      action: () => navigate('/internships'),
      color: 'secondary',
    },
    {
      title: 'View Results',
      description: 'Check your allocation status and results',
      icon: <Assessment />,
      action: () => navigate('/results'),
      color: 'success',
    },
    {
      title: 'Profile Management',
      description: 'Update your profile and preferences',
      icon: <Person />,
      action: () => {},
      color: 'info',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Student Applicant Portal
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
        Welcome to your personalized portal. Upload your CV, browse internships, and track your application status.
      </Typography>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
        gap: 3
      }}>
        {actions.map((action, index) => (
          <Box key={index}>
            <Card 
              sx={{ 
                height: '100%', 
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}
              onClick={action.action}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ color: `${action.color}.main`, mb: 2 }}>
                  {React.cloneElement(action.icon, { sx: { fontSize: 48 } })}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {action.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {action.description}
                </Typography>
                <Button variant="outlined" color={action.color as any}>
                  Get Started
                </Button>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>
    </Container>
  );
};

export default ApplicantPortal;
