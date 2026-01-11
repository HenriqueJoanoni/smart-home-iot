/**
 * Motion Card Component
 */

import React from 'react';
import { formatRelativeTime } from '../../utils/formatters';
import './SensorCard.scss';

const MotionCard = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="sensor-card sensor-card--motion sensor-card--loading">
        <div className="sensor-card__icon">🚶</div>
        <div className="sensor-card__content">
          <h3 className="sensor-card__title">Motion</h3>
          <div className="sensor-card__skeleton"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="sensor-card sensor-card--motion sensor-card--error">
        <div className="sensor-card__icon">🚶</div>
        <div className="sensor-card__content">
          <h3 className="sensor-card__title">Motion</h3>
          <p className="sensor-card__error">No data available</p>
        </div>
      </div>
    );
  }

  const isMotionDetected = data.value > 0;
  const status = isMotionDetected ? 'active' : 'normal';
  const timeAgo = formatRelativeTime(data.timestamp);

  return (
    <div className={`sensor-card sensor-card--motion sensor-card--${status}`}>
      <div className="sensor-card__header">
        <div className="sensor-card__icon">
          {isMotionDetected ? '🚶' : '🧍'}
        </div>
        <span className={`sensor-card__status sensor-card__status--${status}`}>
          {isMotionDetected ? 'Detected' : 'Clear'}
        </span>
      </div>
      
      <div className="sensor-card__content">
        <h3 className="sensor-card__title">Motion</h3>
        <div className="sensor-card__value">
          {isMotionDetected ? 'Motion Detected' : 'No Motion'}
        </div>
        
        <div className="sensor-card__footer">
          <span className="sensor-card__time">{timeAgo}</span>
          {data.device_id && (
            <span className="sensor-card__device">{data.device_id}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MotionCard;