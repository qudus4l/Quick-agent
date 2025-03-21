import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import {
  Search as SearchIcon,
  Phone as PhoneIcon,
  Event as EventIcon
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';

import apiService from '../services/api';

function AppointmentList() {
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [callInProgress, setCallInProgress] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchAppointments();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      const filtered = appointments.filter(appointment => 
        appointment.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        appointment.appointment_time.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (appointment.notes && appointment.notes.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredAppointments(filtered);
    } else {
      setFilteredAppointments(appointments);
    }
  }, [searchQuery, appointments]);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAppointments();
      setAppointments(data);
      setFilteredAppointments(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching appointments:', err);
      setError('Failed to load appointments. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerCall = async (appointmentId) => {
    setCallInProgress({...callInProgress, [appointmentId]: true});
    try {
      const response = await apiService.triggerAppointmentCall(appointmentId);
      if (response.success) {
        // Show success message or update UI
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

  const columns = [
    { 
      field: 'id', 
      headerName: 'ID', 
      width: 70 
    },
    { 
      field: 'name', 
      headerName: 'Client Name', 
      width: 200,
      renderCell: (params) => (
        <Box sx={{ fontWeight: 'medium', cursor: 'pointer' }} onClick={() => navigate(`/appointments/${params.row.id}`)}>
          {params.value}
        </Box>
      )
    },
    { 
      field: 'appointment_time', 
      headerName: 'Appointment Time', 
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <EventIcon sx={{ fontSize: 16, mr: 1, color: 'primary.main' }} />
          {params.value}
        </Box>
      )
    },
    { 
      field: 'phone_number', 
      headerName: 'Phone Number', 
      width: 180,
      renderCell: (params) => (
        params.value ? params.value : <Typography variant="body2" color="text.secondary">Not provided</Typography>
      )
    },
    { 
      field: 'notes', 
      headerName: 'Notes', 
      width: 250,
      renderCell: (params) => (
        params.value ? params.value : <Typography variant="body2" color="text.secondary">No notes</Typography>
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Button
          variant="outlined"
          size="small"
          startIcon={<PhoneIcon />}
          onClick={() => handleTriggerCall(params.row.id)}
          disabled={callInProgress[params.row.id]}
        >
          {callInProgress[params.row.id] ? (
            <CircularProgress size={20} />
          ) : (
            'Call'
          )}
        </Button>
      ),
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'medium' }}>
        Appointments
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Card sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search appointments by name, date, or notes..."
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Card>
      
      <Card sx={{ height: 'calc(100vh - 250px)', width: '100%' }}>
        <DataGrid
          rows={filteredAppointments}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          disableSelectionOnClick
          loading={loading}
          autoHeight
        />
      </Card>
    </Box>
  );
}

export default AppointmentList;