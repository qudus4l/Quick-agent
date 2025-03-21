import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination
} from '@mui/material';
import {
  CallMade as CallMadeIcon,
  CallReceived as CallReceivedIcon
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';

import apiService from '../services/api';

function CallHistory() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchCallHistory();
    
    // Refresh data every 60 seconds
    const intervalId = setInterval(fetchCallHistory, 60000);
    
    return () => clearInterval(intervalId);
  }, []);

  const fetchCallHistory = async () => {
    try {
      setLoading(true);
      const data = await apiService.getRecentCalls();
      setCalls(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching call history:', err);
      setError('Failed to load call history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading && calls.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Get status color based on call status
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'busy':
        return 'warning';
      case 'no-answer':
        return 'error';
      case 'in-progress':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'medium' }}>
        Call History
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {loading && (
        <Box sx={{ display: 'flex', my: 2 }}>
          <CircularProgress size={24} sx={{ mr: 2 }} />
          <Typography>Refreshing call data...</Typography>
        </Box>
      )}
      
      <Card>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="call history table">
            <TableHead>
              <TableRow>
                <TableCell>Direction</TableCell>
                <TableCell>Contact</TableCell>
                <TableCell>Phone Number</TableCell>
                <TableCell>Date/Time</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Duration</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {calls.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((call) => (
                <TableRow key={call.sid} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {call.direction === 'inbound' ? (
                        <>
                          <CallReceivedIcon sx={{ mr: 1, color: 'success.main' }} />
                          <Typography>Incoming</Typography>
                        </>
                      ) : (
                        <>
                          <CallMadeIcon sx={{ mr: 1, color: 'secondary.main' }} />
                          <Typography>Outgoing</Typography>
                        </>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {call.display_name || (call.direction === 'inbound' ? 'Unknown Caller' : 'Unknown Recipient')}
                  </TableCell>
                  <TableCell>
                    {call.display_number || (call.direction === 'inbound' ? call.from : call.to)}
                  </TableCell>
                  <TableCell>
                    {call.date_created ? format(parseISO(call.date_created), 'MMM d, yyyy h:mm a') : 'Unknown'}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={call.status} 
                      color={getStatusColor(call.status)}
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {call.duration ? `${call.duration} seconds` : '-'}
                  </TableCell>
                </TableRow>
              ))}
              
              {calls.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1" color="text.secondary">
                      No call history available.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={calls.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>
    </Box>
  );
}

export default CallHistory;