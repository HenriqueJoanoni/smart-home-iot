/**
 * Alert List Component
 */

import React, { useState } from 'react';
import AlertItem from './AlertItem';
import Loading from '../Common/Loading';
import './Alert.scss';

const AlertList = ({ 
  alerts = [], 
  loading = false, 
  onResolve,
  showResolved = false,
  maxItems = null 
}) => {
  const [filter, setFilter] = useState('all');

  if (loading) {
    return (
      <div className="alert-list alert-list--loading">
        <Loading size="small" message="Loading alerts..." />
      </div>
    );
  }

  // Filter alerts
  let filteredAlerts = showResolved 
    ? alerts 
    : alerts.filter(alert => !alert.resolved);

  if (filter !== 'all') {
    filteredAlerts = filteredAlerts.filter(alert => alert.severity === filter);
  }

  // Limit items
  if (maxItems) {
    filteredAlerts = filteredAlerts.slice(0, maxItems);
  }

  // Count by severity
  const counts = alerts.reduce((acc, alert) => {
    if (! alert.resolved) {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
    }
    return acc;
  }, {});

  return (
    <div className="alert-list">
      {/* Filter buttons */}
      <div className="alert-list__filters">
        <button
          className={`alert-filter-btn ${filter === 'all' ? 'alert-filter-btn--active' :  ''}`}
          onClick={() => setFilter('all')}
        >
          All ({filteredAlerts.length})
        </button>
        
        {['critical', 'error', 'warning', 'info'].map(severity => (
          counts[severity] > 0 && (
            <button
              key={severity}
              className={`alert-filter-btn alert-filter-btn--${severity} ${filter === severity ? 'alert-filter-btn--active' :  ''}`}
              onClick={() => setFilter(severity)}
            >
              {severity.charAt(0).toUpperCase() + severity.slice(1)} ({counts[severity] || 0})
            </button>
          )
        ))}
      </div>

      {/* Alert items */}
      <div className="alert-list__items">
        {filteredAlerts.length > 0 ? (
          filteredAlerts.map(alert => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onResolve={onResolve}
              showResolveButton={! alert.resolved}
            />
          ))
        ) : (
          <div className="alert-list__empty">
            <p>✅ No alerts to display</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertList;