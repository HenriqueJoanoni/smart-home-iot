/**
 * Data Formatters
 * Functions to format sensor data, timestamps, etc.
 */

import { format, formatDistanceToNow } from 'date-fns';

/**
 * Format sensor value with unit
 */
export const formatSensorValue = (value, unit) => {
  if (value === null || value === undefined) return '--';
  
  const numValue = parseFloat(value);
  
  if (isNaN(numValue)) return '--';
  
  // Format based on unit
  switch (unit) {
    case '°C':
    case '°F':
      return `${numValue.toFixed(1)}${unit}`;
    case '%':
      return `${Math.round(numValue)}${unit}`;
    case 'lux':
      return `${Math.round(numValue)} ${unit}`;
    case 'boolean':
      return numValue > 0 ? 'Yes' : 'No';
    default:
      return `${numValue.toFixed(1)} ${unit}`;
  }
};

/**
 * Format timestamp
 */
export const formatTimestamp = (timestamp, formatString = 'PPpp') => {
  if (!timestamp) return '--';
  
  try {
    const date = new Date(timestamp);
    return format(date, formatString);
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return '--';
  }
};

/**
 * Format relative time (e.g., "2 minutes ago")
 */
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return '--';
  
  try {
    const date = new Date(timestamp);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return '--';
  }
};

/**
 * Format time only (HH:mm: ss)
 */
export const formatTime = (timestamp) => {
  return formatTimestamp(timestamp, 'HH:mm:ss');
};

/**
 * Format date only (dd/MM/yyyy)
 */
export const formatDate = (timestamp) => {
  return formatTimestamp(timestamp, 'dd/MM/yyyy');
};

/**
 * Get sensor status based on value and thresholds
 */
export const getSensorStatus = (sensorType, value, thresholds) => {
  if (!thresholds || value === null || value === undefined) {
    return 'unknown';
  }
  
  const threshold = thresholds[sensorType];
  if (!threshold) return 'normal';
  
  const numValue = parseFloat(value);
  
  if (numValue < threshold.min) return 'low';
  if (numValue > threshold.max) return 'high';
  return 'normal';
};

/**
 * Get status color
 */
export const getStatusColor = (status) => {
  switch (status) {
    case 'normal':
      return 'success';
    case 'low': 
    case 'high':
      return 'warning';
    case 'critical':
      return 'danger';
    default:
      return 'muted';
  }
};

/**
 * Format alert severity
 */
export const formatAlertSeverity = (severity) => {
  return severity ?  severity.charAt(0).toUpperCase() + severity.slice(1).toLowerCase() : '--';
};

/**
 * Truncate text
 */
export const truncate = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Format device ID (remove prefix, make readable)
 */
export const formatDeviceId = (deviceId) => {
  if (!deviceId) return '--';
  
  // Remove common prefixes
  let formatted = deviceId
    .replace('raspberry_pi_', '')
    .replace('rpi-', '')
    .replace('_', ' ');
  
  // Capitalize
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
};