/**
 * useSensorData Hook
 * Fetches and manages sensor data from API
 */

import { useState, useEffect, useCallback } from 'react';
import { getLatestSensorReadings, getSensorHistory } from '../services/api';
import { REFRESH_INTERVALS } from '../utils/constants';

const useSensorData = (autoRefresh = true, refreshInterval = REFRESH_INTERVALS.SENSORS) => {
  const [latestReadings, setLatestReadings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch latest sensor readings
  const fetchLatest = useCallback(async () => {
    try {
      setError(null);
      const data = await getLatestSensorReadings();
      setLatestReadings(data);
      setLastUpdate(new Date());
      setLoading(false);
      return data;
    } catch (err) {
      console.error('Error fetching sensor data:', err);
      setError(err.message || 'Failed to fetch sensor data');
      setLoading(false);
      return null;
    }
  }, []);

  // Fetch sensor history
  const fetchHistory = useCallback(async (sensorType, hours = 24, limit = 100) => {
    try {
      const data = await getSensorHistory(sensorType, hours, limit);
      return data;
    } catch (err) {
      console.error(`Error fetching ${sensorType} history:`, err);
      return null;
    }
  }, []);

  // Get specific sensor value
  const getSensorValue = useCallback((sensorType) => {
    if (!latestReadings) return null;
    return latestReadings[sensorType] || null;
  }, [latestReadings]);

  // Initial fetch
  useEffect(() => {
    fetchLatest();
  }, [fetchLatest]);

  // Auto-refresh
  useEffect(() => {
    if (! autoRefresh) return;

    const interval = setInterval(() => {
      fetchLatest();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchLatest]);

  return {
    latestReadings,
    loading,
    error,
    lastUpdate,
    fetchLatest,
    fetchHistory,
    getSensorValue,
  };
};

export default useSensorData;