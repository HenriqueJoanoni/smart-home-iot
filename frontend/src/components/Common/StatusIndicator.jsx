/**
 * Status Indicator Component
 * Shows connection status (online/offline, connected/disconnected)
 */

import React from 'react';
import './Common.scss';

const StatusIndicator = ({ 
  status = 'unknown', 
  label = null, 
  showLabel = true,
  size = 'medium',
  animated = true 
}) => {
  const getStatusInfo = () => {
    switch (status.toLowerCase()) {
      case 'online':
      case 'connected':
      case 'active':
        return { color: 'success', text: 'Online', icon: '●' };
      
      case 'offline':
      case 'disconnected':
      case 'inactive':
        return { color: 'danger', text: 'Offline', icon: '●' };
      
      case 'connecting':
      case 'loading':
        return { color: 'warning', text: 'Connecting...', icon: '●' };
      
      case 'error':
        return { color: 'danger', text: 'Error', icon: '⚠' };
      
      default: 
        return { color: 'muted', text: 'Unknown', icon: '●' };
    }
  };

  const statusInfo = getStatusInfo();
  const displayLabel = label || statusInfo.text;

  return (
    <div className={`status-indicator status-indicator--${size}`}>
      <span 
        className={`status-indicator__dot status-indicator__dot--${statusInfo.color} ${animated ?  'status-indicator__dot--animated' : ''}`}
        aria-label={displayLabel}
      >
        {statusInfo.icon}
      </span>
      {showLabel && (
        <span className="status-indicator__label">{displayLabel}</span>
      )}
    </div>
  );
};

export default StatusIndicator;