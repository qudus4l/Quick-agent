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
import apiService from '../services/api';

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
        const data = await apiService.getPhoneNumbers();
        
        if (data && data.twilioPhone) {
          setTwilioPhone(data.twilioPhone);
        }
        
        if (data && data.testClientPhone) {
          setTestClientPhone(data.testClientPhone);
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
      const data = await apiService.callTestClient();
      
      if (data && data.success) {
        setSnackbarMessage(`Agent is calling the test client: ${testClientPhone}`);
      } else {
        setSnackbarMessage(data.message || 'Failed to initiate call');
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

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        Test Tools
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ marginBottom: 2 }}>
          {error}
        </Alert>
      )}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', marginY: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ height: '100%' }}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" component="div" gutterBottom>
                    Call the Agent
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    You can test the agent by calling the Twilio number directly.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Twilio Number: {twilioPhone || 'Not configured'}
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<PhoneIcon />}
                    onClick={handleCallAgent}
                    disabled={!twilioPhone}
                    sx={{ marginTop: 2 }}
                  >
                    Call Agent
                  </Button>
                </CardContent>
              </Card>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ height: '100%' }}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" component="div" gutterBottom>
                    Test Agent Outbound Call
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Test the agent's ability to make outbound calls to a client.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Test Client Number: {testClientPhone || 'Not configured'}
                  </Typography>
                  <Button
                    variant="contained"
                    color="secondary"
                    startIcon={<PhoneCallbackIcon />}
                    onClick={handleCallClient}
                    disabled={!testClientPhone || callingClient}
                    sx={{ marginTop: 2 }}
                  >
                    {callingClient ? (
                      <>
                        <CircularProgress size={24} sx={{ marginRight: 1, color: 'white' }} />
                        Calling...
                      </>
                    ) : (
                      "Have Agent Call Client"
                    )}
                  </Button>
                </CardContent>
              </Card>
            </Paper>
          </Grid>
        </Grid>
      )}
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </Box>
  );
}

export default TestPage; 