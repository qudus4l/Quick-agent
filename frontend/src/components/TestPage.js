import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Paper,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import { Phone as PhoneIcon, PhoneCallback as PhoneCallbackIcon } from '@mui/icons-material';
import axios from 'axios';
import config from '../config';

function TestPage() {
  const [twilioPhone, setTwilioPhone] = useState('');
  const [testClientPhone, setTestClientPhone] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [callingClient, setCallingClient] = useState(false);

  useEffect(() => {
    // Fetch phone numbers from the API
    const fetchPhoneNumbers = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${config.apiBaseUrl}${config.endpoints.phoneNumbers}`);
        
        if (response.data && response.data.twilioPhone) {
          setTwilioPhone(response.data.twilioPhone);
        }
        
        if (response.data && response.data.testClientPhone) {
          setTestClientPhone(response.data.testClientPhone);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching phone numbers:', err);
        setError('Failed to load phone numbers. Please make sure the API server is running.');
        setLoading(false);
      }
    };

    fetchPhoneNumbers();
  }, []);

  const handleCallAgent = () => {
    if (twilioPhone) {
      window.location.href = `tel:${twilioPhone}`;
    } else {
      setSnackbarMessage('Twilio phone number not available');
      setSnackbarOpen(true);
    }
  };

  const handleCallClient = async () => {
    if (!testClientPhone) {
      setSnackbarMessage('Test client phone number not available');
      setSnackbarOpen(true);
      return;
    }
    
    try {
      setCallingClient(true);
      const response = await axios.post(`${config.apiBaseUrl}${config.endpoints.callTestClient}`);
      
      if (response.data && response.data.success) {
        setSnackbarMessage(`Agent is calling the test client: ${testClientPhone}`);
      } else {
        setSnackbarMessage(response.data.message || 'Failed to initiate call');
      }
      
      setSnackbarOpen(true);
    } catch (err) {
      console.error('Error initiating call:', err);
      setSnackbarMessage(err.response?.data?.message || 'Failed to initiate call');
      setSnackbarOpen(true);
    } finally {
      setCallingClient(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Test Page
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                Call the Agent
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Click the button below to call the Agent via your phone app. 
                This simulates an inbound call to the system.
              </Typography>
              
              <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Twilio Phone Number:
                </Typography>
                <Typography variant="h6">
                  {twilioPhone || 'Not available'}
                </Typography>
              </Paper>
              
              <Button
                variant="contained"
                color="primary"
                startIcon={<PhoneIcon />}
                fullWidth
                size="large"
                onClick={handleCallAgent}
                disabled={!twilioPhone}
              >
                Call Agent
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                Test Client Phone
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Click the button below to have the Agent call the test client phone number.
                This simulates an outbound call from the system.
              </Typography>
              
              <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Test Client Phone Number:
                </Typography>
                <Typography variant="h6">
                  {testClientPhone || 'Not available'}
                </Typography>
              </Paper>
              
              <Button
                variant="contained"
                color="secondary"
                startIcon={<PhoneCallbackIcon />}
                fullWidth
                size="large"
                onClick={handleCallClient}
                disabled={!testClientPhone || callingClient}
              >
                {callingClient ? 'Calling...' : 'Have Agent Call Client'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Box>
  );
}

export default TestPage; 