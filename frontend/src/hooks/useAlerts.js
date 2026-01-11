/**
 * useAlerts Hook
 * Fetches and manages alerts
 */

import { useState, useEffect, useCallback } from 'react';
import { getAlerts, resolveAlert } from '../services/api';
import { REFRESH_INTERVALS } from '../utils/constants';

const useAlerts = (autoRefresh = true, refreshInterval = REFRESH_INTERVALS.ALERTS) => {
  const [alerts, setAlerts] = useState([]);
  const [unresolvedAlerts, setUnresolvedAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch alerts
  const fetchAlerts = useCallback(async (resolved = null, limit = 50) => {
    try {
      setError(null);
      const data = await getAlerts(resolved, limit);
      
      if (data && data.alerts) {
        setAlerts(data.alerts);
        
        // Filter unresolved
        const unresolved = data.alerts.filter(alert => !alert.resolved);
        setUnresolvedAlerts(unresolved);
      }
      
      setLastUpdate(new Date());
      setLoading(false);
      return data;
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError(err.message || 'Failed to fetch alerts');
      setLoading(false);
      return null;
    }
  }, []);

  // Resolve an alert
  const resolve = useCallback(async (alertId, resolvedBy = 'user') => {
    try {
      const result = await resolveAlert(alertId, resolvedBy);
      
      // Update local state
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, resolved: true, resolved_at: new Date().toISOString(), resolved_by: resolvedBy }
          : alert
      ));
      
      setUnresolvedAlerts(prev => prev.filter(alert => alert.id !== alertId));
      
      console.log(`[useAlerts] Alert ${alertId} resolved`);
      return result;
    } catch (err) {
      console.error('[useAlerts] Failed to resolve alert:', err);
      return null;
    }
  }, []);

  // Get alerts by severity
  const getAlertsBySeverity = useCallback((severity) => {
    return alerts.filter(alert => alert.severity === severity);
  }, [alerts]);

  // Get alert count by severity
  const getAlertCountBySeverity = useCallback(() => {
    return alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, {});
  }, [alerts]);

  // Initial fetch
  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAlerts();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchAlerts]);

  return {
    alerts,
    unresolvedAlerts,
    loading,
    error,
    lastUpdate,
    fetchAlerts,
    resolve,
    getAlertsBySeverity,
    getAlertCountBySeverity,
    unresolvedCount: unresolvedAlerts.length,
  };
};

export default useAlerts;