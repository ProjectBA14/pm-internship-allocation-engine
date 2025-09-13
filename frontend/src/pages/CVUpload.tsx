import React, { useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  TextField,
  Chip,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Edit,
  Save,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

interface ParsedData {
  name: string;
  email: string;
  phone: string;
  location: string;
  category: string;
  education: Array<{
    degree: string;
    institution: string;
    year: string;
    field_of_study: string;
  }>;
  experience: Array<{
    job_title: string;
    company: string;
    duration: string;
    description: string;
  }>;
  skills: {
    technical: string[];
    soft: string[];
    languages: string[];
    tools: string[];
  };
  key_strengths: string[];
  confidence_score: number;
}

const CVUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState<ParsedData | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF, DOC, or DOCX file');
      return;
    }

    // Validate file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
      setError('File size must be less than 16MB');
      return;
    }

    setError(null);
    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Create FormData
      const formData = new FormData();
      formData.append('cv_file', file);

      // Upload and parse CV
      const response = await fetch('http://localhost:5000/api/cv-parse', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new (globalThis.Error)('Failed to parse CV');
      }

      const result = await response.json();
      setParsedData(result.parsed_data);
      setEditedData({ ...result.parsed_data });
      
      // Save parsed CV data to localStorage for use in InternshipList
      localStorage.setItem('parsedCVData', JSON.stringify(result.parsed_data));
      
      setSuccess(true);

    } catch (err) {
      setError(err instanceof globalThis.Error ? (err as globalThis.Error).message : 'Failed to upload and parse CV');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false,
  });

  const handleSaveProfile = async () => {
    if (!editedData) return;

    try {
      const response = await fetch('http://localhost:5000/api/applicants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editedData),
      });

      if (!response.ok) {
        throw new (globalThis.Error)('Failed to save profile');
      }

      await response.json();
      setEditMode(false);
      // Could navigate to profile page or show success message
      
    } catch (err) {
      setError(err instanceof globalThis.Error ? (err as globalThis.Error).message : 'Failed to save profile');
    }
  };

  const renderParsedData = () => {
    if (!parsedData || !editedData) return null;

    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Extracted Information
            </Typography>
            <Box>
              <Chip 
                label={`Confidence: ${Math.round(parsedData.confidence_score * 100)}%`}
                color={parsedData.confidence_score > 0.8 ? 'success' : parsedData.confidence_score > 0.6 ? 'warning' : 'error'}
                size="small"
              />
              <Button
                startIcon={editMode ? <Save /> : <Edit />}
                onClick={editMode ? handleSaveProfile : () => setEditMode(true)}
                sx={{ ml: 1 }}
              >
                {editMode ? 'Save Profile' : 'Edit'}
              </Button>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Personal Information */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Personal Information
              </Typography>
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                gap: 2
              }}>
                <Box>
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={editedData.name}
                    onChange={(e) => setEditedData({ ...editedData, name: e.target.value })}
                    disabled={!editMode}
                    size="small"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="Email"
                    value={editedData.email}
                    onChange={(e) => setEditedData({ ...editedData, email: e.target.value })}
                    disabled={!editMode}
                    size="small"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="Phone"
                    value={editedData.phone}
                    onChange={(e) => setEditedData({ ...editedData, phone: e.target.value })}
                    disabled={!editMode}
                    size="small"
                  />
                </Box>
                <Box>
                  <TextField
                    fullWidth
                    label="Location"
                    value={editedData.location}
                    onChange={(e) => setEditedData({ ...editedData, location: e.target.value })}
                    disabled={!editMode}
                    size="small"
                  />
                </Box>
              </Box>
            </Box>

            <Box>
              <Divider />
            </Box>

            {/* Education */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Education
              </Typography>
              {editedData.education.map((edu, index) => (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Box sx={{ 
                    display: 'grid', 
                    gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                    gap: 2
                  }}>
                    <Box>
                      <TextField
                        fullWidth
                        label="Degree"
                        value={edu.degree}
                        disabled={!editMode}
                        size="small"
                      />
                    </Box>
                    <Box>
                      <TextField
                        fullWidth
                        label="Institution"
                        value={edu.institution}
                        disabled={!editMode}
                        size="small"
                      />
                    </Box>
                    <Box>
                      <TextField
                        fullWidth
                        label="Year"
                        value={edu.year}
                        disabled={!editMode}
                        size="small"
                      />
                    </Box>
                    <Box>
                      <TextField
                        fullWidth
                        label="Field of Study"
                        value={edu.field_of_study}
                        disabled={!editMode}
                        size="small"
                      />
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>

            <Box>
              <Divider />
            </Box>

            {/* Skills */}
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Skills
              </Typography>
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                gap: 2
              }}>
                {Object.entries(editedData.skills).map(([category, skillList]) => (
                  <Box key={category}>
                    <Typography variant="body2" fontWeight="medium" gutterBottom>
                      {category.charAt(0).toUpperCase() + category.slice(1)}:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {skillList.map((skill, index) => (
                        <Chip key={index} label={skill} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                ))}
              </Box>
            </Box>

            {/* Category and Strengths */}
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
              gap: 2
            }}>
              <Box>
              <TextField
                fullWidth
                label="Category"
                value={editedData.category}
                onChange={(e) => setEditedData({ ...editedData, category: e.target.value })}
                disabled={!editMode}
                size="small"
              />
              </Box>
              <Box>
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                Key Strengths:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {editedData.key_strengths.map((strength, index) => (
                  <Chip key={index} label={strength} size="small" color="primary" variant="outlined" />
                ))}
              </Box>
            </Box>
          </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Upload Your CV
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
        Upload your CV and let our AI extract your information automatically. 
        You can review and edit the extracted data before submitting.
      </Typography>

      {/* Upload Area */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop your CV here' : 'Drag & drop your CV here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          or click to select a file
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Supported formats: PDF, DOC, DOCX (Max size: 16MB)
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button variant="outlined" component="span">
            Choose File
          </Button>
        </Box>
      </Paper>

      {/* Upload Progress */}
      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
          <Typography variant="body2" textAlign="center" sx={{ mt: 1 }}>
            {uploadProgress < 90 ? 'Uploading...' : 'Processing with AI...'}
          </Typography>
        </Box>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Success Message */}
      {success && (
        <Alert 
          severity="success" 
          sx={{ mt: 2 }} 
          icon={<CheckCircle />}
          onClose={() => setSuccess(false)}
        >
          CV uploaded and parsed successfully! Review the extracted information below.
        </Alert>
      )}

      {/* Parsed Data Display */}
      {renderParsedData()}

      {/* Help Section */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📝 Tips for Better Results
          </Typography>
          <ul>
            <li>Use a well-formatted CV with clear sections</li>
            <li>Include complete contact information</li>
            <li>List your education, experience, and skills clearly</li>
            <li>Avoid using images or complex layouts</li>
            <li>Review and correct any extracted information before saving</li>
          </ul>
        </CardContent>
      </Card>
    </Container>
  );
};

export default CVUpload;
