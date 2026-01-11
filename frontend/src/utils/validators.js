/**
 * Validators
 * Validation functions for data
 */

/**
 * Validate sensor reading
 */
export const isValidSensorReading = (reading) => {
  if (!reading) return false;
  
  return (
    reading.value !== null &&
    reading.value !== undefined &&
    typeof reading.sensor_type === 'string' &&
    typeof reading.unit === 'string'
  );
};

/**
 * Validate sensor type
 */
export const isValidSensorType = (type) => {
  const validTypes = ['temperature', 'humidity', 'light', 'motion'];
  return validTypes.includes(type);
};

/**
 * Validate timestamp
 */
export const isValidTimestamp = (timestamp) => {
  if (!timestamp) return false;
  
  const date = new Date(timestamp);
  return date instanceof Date && !isNaN(date);
};

/**
 * Validate control command
 */
export const isValidControlCommand = (device, action) => {
  const validCommands = {
    led:  ['on', 'off', 'toggle'],
    buzzer: ['on', 'off', 'beep', 'alarm'],
  };
  
  return (
    validCommands[device] &&
    validCommands[device].includes(action)
  );
};

/**
 * Validate API response
 */
export const isValidApiResponse = (response) => {
  return (
    response &&
    typeof response === 'object' &&
    ! response.error
  );
};

/**
 * Sanitize sensor data (remove invalid readings)
 */
export const sanitizeSensorData = (data) => {
  if (!Array.isArray(data)) return [];
  
  return data.filter(reading => isValidSensorReading(reading));
};