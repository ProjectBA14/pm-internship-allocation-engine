import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Paper,
  Stack,
} from '@mui/material';
import {
  Dashboard,
  People,
  Work,
  Analytics,
  Settings,
  PlayArrow,
} from '@mui/icons-material';

const AdminDashboard: React.FC = () => {
  const stats = [
    { label: 'Total Applicants', value: '1,234', icon: <People /> },
    { label: 'Active Internships', value: '56', icon: <Work /> },
    { label: 'Completed Matches', value: '892', icon: <Analytics /> },
    { label: 'Allocation Rate', value: '78%', icon: <Dashboard /> },
  ];

  const actions = [
    { title: 'Run Matching Algorithm', icon: <PlayArrow />, color: 'primary' },
    { title: 'View Analytics', icon: <Analytics />, color: 'secondary' },
    { title: 'Manage Internships', icon: <Work />, color: 'success' },
    { title: 'System Settings', icon: <Settings />, color: 'info' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Monitor system performance and manage the internship allocation process
      </Typography>

      {/* Statistics */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
        gap: 3,
        mb: 4
      }}>
        {stats.map((stat, index) => (
          <Box key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </Box>
                  <Box sx={{ color: 'primary.main' }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Actions */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
        gap: 3
      }}>
        {actions.map((action, index) => (
          <Box key={index}>
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' },
              }}
            >
              <Box sx={{ color: `${action.color}.main`, mb: 2 }}>
                {React.cloneElement(action.icon, { sx: { fontSize: 48 } })}
              </Box>
              <Typography variant="h6" gutterBottom>
                {action.title}
              </Typography>
              <Button variant="outlined" color={action.color as any}>
                Open
              </Button>
            </Paper>
          </Box>
        ))}
      </Box>

      {/* Recent Activity */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Typography variant="body2" color="text.secondary">
            System activity and notifications will appear here
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default AdminDashboard;
