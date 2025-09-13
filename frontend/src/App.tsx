import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ApplicantPortal from './pages/ApplicantPortal';
import AdminDashboard from './pages/AdminDashboard';
import InternshipList from './pages/InternshipList';
import CVUpload from './pages/CVUpload';
import AllocationResults from './pages/AllocationResults';

// Theme configuration
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e', // Pink/Red
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/applicant" element={<ApplicantPortal />} />
            <Route path="/cv-upload" element={<CVUpload />} />
            <Route path="/internships" element={<InternshipList />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/results" element={<AllocationResults />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
