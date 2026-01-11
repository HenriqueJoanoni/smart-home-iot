/**
 * API Service
 * HTTP requests to backend API
 */

import axios from 'axios';
import { API_URL, ENDPOINTS } from '../utils/constants';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for debugging)
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor (for error handling)
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response:`, response.data);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ================================
// SENSOR ENDPOINTS
// ================================

/**
 * Get latest sensor readings
 */
export const getLatestSensorReadings = async () => {
  try {
    const response = await api.get(ENDPOINTS.SENSORS.LATEST);
    return response.data;
  } catch (error) {
    console.error('Error fetching latest sensors:', error);
    throw error;
  }
};

/**
 * Get sensor history
 */
export const getSensorHistory = async (sensorType, hours = 24, limit = 100) => {
  try {
    const response = await api.get(ENDPOINTS.SENSORS.HISTORY(sensorType), {
      params: { hours, limit },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${sensorType} history:`, error);
    throw error;
  }
};

// ================================
// CONTROL ENDPOINTS
// ================================

/**
 * Control LED
 */
export const controlLED = async (action, brightness = 100) => {
  try {
    const response = await api.post(ENDPOINTS.CONTROL.LED, {
      action,
      brightness,
    });
    return response.data;
  } catch (error) {
    console.error('Error controlling LED:', error);
    throw error;
  }
};

/**
 * Control Buzzer
 */
export const controlBuzzer = async (action) => {
  try {
    const response = await api.post(ENDPOINTS.CONTROL.BUZZER, {
      action,
    });
    return response.data;
  } catch (error) {
    console.error('Error controlling buzzer:', error);
    throw error;
  }
};

/**
 * Get device status
 */
export const getDeviceStatus = async () => {
  try {
    const response = await api.get(ENDPOINTS.CONTROL.STATUS);
    return response.data;
  } catch (error) {
    console.error('Error fetching device status:', error);
    throw error;
  }
};

// ================================
// ALERT ENDPOINTS
// ================================

/**
 * Get alerts
 */
export const getAlerts = async (resolved = null, limit = 50) => {
  try {
    const params = { limit };
    if (resolved !== null) {
      params.resolved = resolved;
    }
    
    const response = await api.get(ENDPOINTS.ALERTS.LIST, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};

/**
 * Resolve alert
 */
export const resolveAlert = async (alertId, resolvedBy = 'user') => {
  try {
    const response = await api.post(ENDPOINTS.ALERTS.RESOLVE(alertId), {
      resolved_by: resolvedBy,
    });
    return response.data;
  } catch (error) {
    console.error('Error resolving alert:', error);
    throw error;
  }
};

// ================================
// STATS ENDPOINTS
// ================================

/**
 * Get dashboard statistics
 */
export const getDashboardStats = async (hours = 24) => {
  try {
    const response = await api.get(ENDPOINTS.STATS.DASHBOARD, {
      params: { hours },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

// ================================
// HEALTH CHECK
// ================================

/**
 * Check API health
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health', {
      baseURL: API_URL.replace('/api', ''),
    });
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export default api;