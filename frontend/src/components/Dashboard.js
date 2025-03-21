import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Event as EventIcon,
  Phone as PhoneIcon,
  PhoneCallback as PhoneCallbackIcon,
  PersonOutline as PersonIcon,
  CallMade as CallMadeIcon
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';

import apiService from '../services/api';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [callInProgress, setCallInProgress] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
    
    // Refresh data every 30 seconds
    const intervalId = setInterval(fetchDashboardData, 30000);
    
    return () => clearInterval(intervalId);
  }, []);
  
  const fetchDashboardData = async () => {
    try {
      const data = await apiService.getDashboardData();
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerCall = async (appointmentId) => {
    setCallInProgress({...callInProgress, [appointmentId]: true});
    try {
      const response = await apiService.triggerAppointmentCall(appointmentId);
      if (response.success) {
        // Wait a bit and then refresh the dashboard to show the new call
        setTimeout(fetchDashboardData, 2000);
      } else {
        setError(`Failed to initiate call: ${response.message}`);
      }
    } catch (err) {
      console.error('Error triggering call:', err);
      setError('Failed to trigger the call. Please try again.');
    } finally {
      setCallInProgress({...callInProgress, [appointmentId]: false});
    }
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
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'medium' }}>
        Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <EventIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.upcoming_appointments || 0}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Upcoming Appointments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <PhoneIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.recent_calls?.length || 0}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Recent Calls
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <PersonIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {dashboardData?.total_appointments || 0}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Total Appointments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Upcoming Appointments */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <EventIcon sx={{ mr: 1 }} /> Upcoming Appointments
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {dashboardData?.recent_appointments?.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                  No upcoming appointments found.
                </Typography>
              ) : (
                <List>
                  {dashboardData?.recent_appointments?.map((appointment) => (
                    <ListItem 
                      key={appointment.id}
                      sx={{ 
                        mb: 1, 
                        borderRadius: 1,
                        '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                      }}
                    >
                      <ListItemText
                        primary={appointment.name}
                        secondary={
                          <>
                            <Typography component="span" variant="body2">
                              {appointment.appointment_time}
                            </Typography>
                            {appointment.notes && (
                              <Typography component="p" variant="caption" sx={{ mt: 0.5 }}>
                                Notes: {appointment.notes}
                              </Typography>
                            )}
                          </>
                        }
                        onClick={() => navigate(`/appointments/${appointment.id}`)}
                        sx={{ cursor: 'pointer' }}
                      />
                      <ListItemSecondaryAction>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<PhoneIcon />}
                          onClick={() => handleTriggerCall(appointment.id)}
                          disabled={callInProgress[appointment.id]}
                          sx={{ mr: 1 }}
                        >
                          {callInProgress[appointment.id] ? (
                            <CircularProgress size={20} />
                          ) : (
                            'Call'
                          )}
                        </Button>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button 
                  variant="text" 
                  onClick={() => navigate('/appointments')}
                >
                  View All Appointments
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Calls */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <PhoneCallbackIcon sx={{ mr: 1 }} /> Recent Calls
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {dashboardData?.recent_calls?.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                  No recent calls found.
                </Typography>
              ) : (
                <List>
                  {dashboardData?.recent_calls?.slice(0, 5).map((call) => (
                    <ListItem 
                      key={call.sid}
                      sx={{ 
                        mb: 1, 
                        borderRadius: 1,
                        '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {call.direction === 'inbound' ? (
                              <CallMadeIcon sx={{ mr: 1, transform: 'rotate(180deg)', color: 'success.main' }} />
                            ) : (
                              <CallMadeIcon sx={{ mr: 1, color: 'secondary.main' }} />
                            )}
                            {call.display_name || (call.direction === 'inbound' ? 'Unknown Caller' : 'Unknown Recipient')}
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography component="span" variant="body2">
                              {call.display_number || (call.direction === 'inbound' ? call.from : call.to)}
                            </Typography>
                            {call.date_created && (
                              <Typography component="div" variant="body2" sx={{ mt: 0.5 }}>
                                {format(parseISO(call.date_created), 'MMM d, yyyy h:mm a')}
                              </Typography>
                            )}
                            <Box sx={{ mt: 0.5 }}>
                              <Chip 
                                label={call.status} 
                                size="small" 
                                color={
                                  call.status === 'completed' ? 'success' :
                                  call.status === 'failed' ? 'error' :
                                  call.status === 'busy' ? 'warning' :
                                  'default'
                                }
                                variant="outlined"
                              />
                              <Chip 
                                label={call.direction === 'inbound' ? 'Incoming' : 'Outgoing'} 
                                size="small" 
                                sx={{ ml: 1 }}
                                variant="outlined"
                              />
                            </Box>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button 
                  variant="text" 
                  onClick={() => navigate('/calls')}
                >
                  View All Calls
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard; 