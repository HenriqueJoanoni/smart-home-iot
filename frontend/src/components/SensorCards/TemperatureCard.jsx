/**
 * Temperature Card Component
 */

import React from 'react';
import { formatSensorValue, formatRelativeTime } from '../../utils/formatters';
import { getSensorStatus } from '../../utils/formatters';
import { THRESHOLDS } from '../../utils/constants';
import './SensorCard.scss';

const TemperatureCard = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="sensor-card sensor-card--temperature sensor-card--loading">
        <div className="sensor-card__icon">🌡️</div>
        <div className="sensor-card__content">
          <h3 className="sensor-card__title">Temperature</h3>
          <div className="sensor-card__skeleton"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="sensor-card sensor-card--temperature sensor-card--error">
        <div className="sensor-card__icon">🌡️</div>
        <div className="sensor-card__content">
          <h3 className="sensor-card__title">Temperature</h3>
          <p className="sensor-card__error">No data available</p>
        </div>
      </div>
    );
  }

  const status = getSensorStatus('temperature', data.value, THRESHOLDS);
  const formattedValue = formatSensorValue(data.value, data.unit);
  const timeAgo = formatRelativeTime(data.timestamp);

  return (
    <div className={`sensor-card sensor-card--temperature sensor-card--${status}`}>
      <div className="sensor-card__header">
        <div className="sensor-card__icon">🌡️</div>
        <span className={`sensor-card__status sensor-card__status--${status}`}>
          {status}
        </span>
      </div>
      
      <div className="sensor-card__content">
        <h3 className="sensor-card__title">Temperature</h3>
        <div className="sensor-card__value">{formattedValue}</div>
        
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

export default TemperatureCard;