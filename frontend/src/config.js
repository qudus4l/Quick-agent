/**
 * Configuration settings for the frontend application
 * This centralizes API URLs and other environment-specific settings
 */

// Determine the base API URL based on the environment
const getBaseApiUrl = () => {
  // Check if we're running on AWS or other production environment
  if (window.location.hostname !== 'localhost') {
    // Use relative URL if on the same domain
    return '';
  }
  // For local development
  return 'http://localhost:5001';
};

const config = {
  // Base URL for API endpoints
  apiBaseUrl: getBaseApiUrl(),
  
  // Specific API endpoints
  endpoints: {
    phoneNumbers: '/api/config/phones',
    callTestClient: '/api/call/test-client',
    appointments: '/api/appointments',
    calls: '/api/calls/recent',
    dashboardData: '/api/dashboard-data'
  }
};

export default config; 