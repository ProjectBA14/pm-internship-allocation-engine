import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Schedule,
  Error,
  Info,
} from '@mui/icons-material';

const AllocationResults: React.FC = () => {
  const mockResults = [
    {
      candidate: 'John Doe',
      internship: 'Software Development Intern',
      company: 'TechCorp India',
      status: 'allocated',
      score: 0.85,
      category: 'General',
    },
    {
      candidate: 'Jane Smith',
      internship: 'Data Science Intern',
      company: 'DataMinds',
      status: 'allocated',
      score: 0.92,
      category: 'SC',
    },
    {
      candidate: 'Alex Johnson',
      internship: 'Digital Marketing Intern',
      company: 'BrandBoost',
      status: 'waitlisted',
      score: 0.73,
      category: 'General',
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'allocated':
        return <CheckCircle color="success" />;
      case 'waitlisted':
        return <Schedule color="warning" />;
      case 'rejected':
        return <Error color="error" />;
      default:
        return <Info color="info" />;
    }
  };

  const getStatusColor = (status: string): "success" | "warning" | "error" | "info" => {
    switch (status) {
      case 'allocated':
        return 'success';
      case 'waitlisted':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'info';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Allocation Results
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
        View the results of the AI-powered matching and allocation process
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {mockResults.map((result, index) => (
          <Box key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {getStatusIcon(result.status)}
                    <Typography variant="h6">
                      {result.candidate}
                    </Typography>
                    <Chip
                      label={result.status.toUpperCase()}
                      color={getStatusColor(result.status)}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="text.secondary">
                      Match Score: {Math.round(result.score * 100)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Category: {result.category}
                    </Typography>
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="body1" fontWeight="medium">
                    {result.internship}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {result.company}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📊 Allocation Summary
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr 1fr' },
            gap: 2
          }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                2
              </Typography>
              <Typography variant="body2">Allocated</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">
                1
              </Typography>
              <Typography variant="body2">Waitlisted</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main">
                0
              </Typography>
              <Typography variant="body2">Rejected</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default AllocationResults;
