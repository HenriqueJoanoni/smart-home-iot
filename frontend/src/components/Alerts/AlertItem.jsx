/**
 * Alert Item Component
 */

import React from 'react';
import { FaCheckCircle, FaTimes } from 'react-icons/fa';
import { formatRelativeTime, formatAlertSeverity } from '../../utils/formatters';
import './Alert.scss';

const AlertItem = ({ alert, onResolve, showResolveButton = true }) => {
  const handleResolve = () => {
    if (onResolve) {
      onResolve(alert.id);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': 
        return '🔴';
      case 'error':
        return '⚠️';
      case 'warning':
        return '⚡';
      case 'info': 
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  return (
    <div className={`alert-item alert-item--${alert.severity} ${alert.resolved ? 'alert-item--resolved' : ''}`}>
      <div className="alert-item__icon">
        {alert.resolved ? <FaCheckCircle /> : getSeverityIcon(alert.severity)}
      </div>
      
      <div className="alert-item__content">
        <div className="alert-item__header">
          <span className={`alert-item__severity alert-item__severity--${alert.severity}`}>
            {formatAlertSeverity(alert.severity)}
          </span>
          <span className="alert-item__type">{alert.alert_type}</span>
        </div>
        
        <p className="alert-item__message">{alert.message}</p>
        
        <div className="alert-item__footer">
          <span className="alert-item__time">
            {formatRelativeTime(alert.timestamp)}
          </span>
          
          {alert.device_id && (
            <span className="alert-item__device">{alert.device_id}</span>
          )}
          
          {alert.resolved && alert.resolved_by && (
            <span className="alert-item__resolved">
              Resolved by {alert.resolved_by}
            </span>
          )}
        </div>
      </div>
      
      {! alert.resolved && showResolveButton && onResolve && (
        <button
          className="alert-item__resolve-btn"
          onClick={handleResolve}
          title="Mark as resolved"
        >
          <FaTimes />
        </button>
      )}
    </div>
  );
};

export default AlertItem;