import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions for appointments
export const getAppointments = async (filters = {}) => {
  const response = await apiClient.get('/appointments', { params: filters });
  return response.data;
};

export const getAppointmentById = async (id) => {
  const response = await apiClient.get(`/appointments?id=${id}`);
  return response.data;
};

export const triggerAppointmentCall = async (appointmentId) => {
  const response = await apiClient.post(`/appointments/${appointmentId}/call`);
  return response.data;
};

// API functions for calls
export const getRecentCalls = async () => {
  const response = await apiClient.get('/calls/recent');
  return response.data;
};

// Dashboard data
export const getDashboardData = async () => {
  const response = await apiClient.get('/dashboard-data');
  return response.data;
};

const apiService = {
  getAppointments,
  getAppointmentById,
  triggerAppointmentCall,
  getRecentCalls,
  getDashboardData,
};

export default apiService; 