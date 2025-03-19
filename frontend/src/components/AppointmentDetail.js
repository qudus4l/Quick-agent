import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Event as EventIcon,
  Notes as NotesIcon,
  AccessTime as TimeIcon,
  Person as PersonIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { format, parseISO, formatDistanceToNow } from 'date-fns';

import apiService from '../services/api';

function AppointmentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [callInProgress, setCallInProgress] = useState(false);

  useEffect(() => {
    fetchAppointmentDetails();
  }, [id]);

  const fetchAppointmentDetails = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAppointmentById(id);
      setAppointment(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching appointment details:', err);
      setError('Failed to load appointment details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerCall = async () => {
    setCallInProgress(true);
    try {
      const response = await apiService.triggerAppointmentCall(id);
      if (response.success) {
        // Show success message
      } else {
        setError(`Failed to initiate call: ${response.message}`);
      }
    } catch (err) {
      console.error('Error triggering call:', err);
      setError('Failed to trigger the call. Please try again.');
    } finally {
      setCallInProgress(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!appointment) {
    return (
      <Box>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/appointments')}
          sx={{ mb: 3 }}
        >
          Back to Appointments
        </Button>
        <Alert severity="error">Appointment not found. It may have been deleted or the ID is invalid.</Alert>
      </Box>
    );
  }

  // Format date strings
  const createdDate = appointment.created_at ? new Date(appointment.created_at) : null;
  const appointmentDateTime = appointment.datetime ? parseISO(appointment.datetime) : null;

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/appointments')}
        sx={{ mb: 3 }}
      >
        Back to Appointments
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 'medium' }}>
                  Appointment Details
                </Typography>

                <Button
                  variant="contained"
                  startIcon={<PhoneIcon />}
                  onClick={handleTriggerCall}
                  disabled={callInProgress}
                >
                  {callInProgress ? <CircularProgress size={24} color="inherit" /> : 'Call Client'}
                </Button>
              </Box>

              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Client Name"
                        secondary={appointment.name}
                        primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                        secondaryTypographyProps={{ variant: 'body1', fontWeight: 'medium' }}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <EventIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Appointment Time"
                        secondary={appointment.appointment_time}
                        primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                        secondaryTypographyProps={{ variant: 'body1', fontWeight: 'medium' }}
                      />
                    </ListItem>

                    {appointmentDateTime && (
                      <ListItem>
                        <ListItemIcon>
                          <TimeIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Time Until Appointment"
                          secondary={
                            <Chip 
                              label={`${formatDistanceToNow(appointmentDateTime, { addSuffix: true })}`}
                              color={appointment.days_until < 0 ? 'error' : appointment.days_until === 0 ? 'success' : 'primary'}
                              variant="outlined"
                            />
                          }
                          primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                        />
                      </ListItem>
                    )}
                  </List>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <PhoneIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Phone Number"
                        secondary={appointment.phone_number || "Not provided"}
                        primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                        secondaryTypographyProps={{ 
                          variant: 'body1', 
                          fontWeight: 'medium',
                          color: appointment.phone_number ? 'text.primary' : 'text.secondary' 
                        }}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <NotesIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Notes"
                        secondary={appointment.notes || "No notes"}
                        primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                        secondaryTypographyProps={{ 
                          variant: 'body1',
                          color: appointment.notes ? 'text.primary' : 'text.secondary' 
                        }}
                      />
                    </ListItem>

                    {createdDate && (
                      <ListItem>
                        <ListItemIcon>
                          <EventIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Created On"
                          secondary={format(createdDate, 'PPP p')}
                          primaryTypographyProps={{ variant: 'subtitle2', color: 'text.secondary' }}
                          secondaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    )}
                  </List>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Button
                fullWidth
                variant="contained"
                startIcon={<PhoneIcon />}
                onClick={handleTriggerCall}
                disabled={callInProgress}
                sx={{ mb: 2 }}
              >
                {callInProgress ? <CircularProgress size={24} color="inherit" /> : 'Call Client'}
              </Button>
              
              {/* Placeholder for additional quick actions in the future */}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AppointmentDetail; 