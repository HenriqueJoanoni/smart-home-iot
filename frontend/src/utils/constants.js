/**
 * Application Constants
 */

// API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// PubNub Configuration
export const PUBNUB_CONFIG = {
  publishKey: process.env.REACT_APP_PUBNUB_PUBLISH_KEY,
  subscribeKey: process.env.REACT_APP_PUBNUB_SUBSCRIBE_KEY,
  uuid: `web-client-${Math.random().toString(36).substring(7)}`,
};

// PubNub Channels
export const CHANNELS = {
  SENSOR:  process.env.REACT_APP_PUBNUB_SENSOR_CHANNEL || 'smart-home-sensors',
  CONTROL: process.env.REACT_APP_PUBNUB_CONTROL_CHANNEL || 'smart-home-control',
  ALERT: process.env.REACT_APP_PUBNUB_ALERT_CHANNEL || 'smart-home-alerts',
};

// Device Configuration
export const DEVICE_ID = process.env.REACT_APP_DEVICE_ID || 'raspberry_pi_main';
export const POLLING_INTERVAL = parseInt(process.env.REACT_APP_POLLING_INTERVAL || '10000', 10);

// Sensor Thresholds (for UI indicators)
export const THRESHOLDS = {
  temperature: { min: 18, max: 28, unit: '°C' },
  humidity:  { min: 30, max: 70, unit: '%' },
  light: { min: 50, max: 800, unit: 'lux' },
};

// Chart Configuration
export const CHART_CONFIG = {
  maxDataPoints: 50,
  updateInterval: 5000,
  colors: {
    temperature: '#ff6b6b',
    humidity:  '#4ecdc4',
    light: '#ffe66d',
  },
};

// Alert Severity Levels
export const ALERT_SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical',
};

// API Endpoints
export const ENDPOINTS = {
  SENSORS: {
    LATEST: '/sensors/latest',
    HISTORY:  (type) => `/sensors/${type}/history`,
  },
  CONTROL: {
    LED: '/control/led',
    BUZZER: '/control/buzzer',
    STATUS: '/control/status',
  },
  ALERTS: {
    LIST: '/alerts',
    RESOLVE: (id) => `/alerts/${id}/resolve`,
  },
  STATS: {
    DASHBOARD: '/stats/dashboard',
  },
};

// Refresh Intervals
export const REFRESH_INTERVALS = {
  SENSORS: 10000,
  ALERTS: 30000,
  STATS: 60000,
};