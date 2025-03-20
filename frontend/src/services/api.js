import axios from 'axios';
import config from '../config';

// Use the API base URL from our config
const apiClient = axios.create({
  baseURL: `${config.apiBaseUrl}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions for appointments
export const getAppointments = async (filters = {}) => {
  const response = await apiClient.get(config.endpoints.appointments, { params: filters });
  return response.data;
};

export const getAppointmentById = async (id) => {
  const response = await apiClient.get(`${config.endpoints.appointments}?id=${id}`);
  return response.data;
};

export const triggerAppointmentCall = async (appointmentId) => {
  const response = await apiClient.post(`${config.endpoints.appointments}/${appointmentId}/call`);
  return response.data;
};

// API functions for calls
export const getRecentCalls = async () => {
  const response = await apiClient.get(config.endpoints.calls);
  return response.data;
};

// Dashboard data
export const getDashboardData = async () => {
  const response = await apiClient.get(config.endpoints.dashboardData);
  return response.data;
};

// Phone number data
export const getPhoneNumbers = async () => {
  const response = await apiClient.get(config.endpoints.phoneNumbers);
  return response.data;
};

// Call test client
export const callTestClient = async () => {
  const response = await apiClient.post(config.endpoints.callTestClient);
  return response.data;
};

const apiService = {
  getAppointments,
  getAppointmentById,
  triggerAppointmentCall,
  getRecentCalls,
  getDashboardData,
  getPhoneNumbers,
  callTestClient,
};

export default apiService; 