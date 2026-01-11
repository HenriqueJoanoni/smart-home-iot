/**
 * Buzzer Control Component
 */

import React, { useState } from 'react';
import { FaBell, FaExclamationTriangle } from 'react-icons/fa';
import './Controls.scss';

const BuzzerControl = ({ 
  onBeep, 
  onAlarm, 
  onToggle,
  loading = false,
  disabled = false,
  currentState = 'off'
}) => {
  const [isActive, setIsActive] = useState(false);

  const handleBeep = async () => {
    setIsActive(true);
    if (onBeep) {
      await onBeep();
    }
    setTimeout(() => setIsActive(false), 500);
  };

  const handleAlarm = async () => {
    setIsActive(true);
    if (onAlarm) {
      await onAlarm();
    }
    setTimeout(() => setIsActive(false), 2000);
  };

  const handleToggle = async () => {
    if (onToggle) {
      await onToggle();
    }
  };

  return (
    <div className="control-card">
      <div className="control-card__header">
        <div className="control-card__icon">
          <FaBell />
        </div>
        <div className="control-card__info">
          <h3 className="control-card__title">Buzzer</h3>
          <span className={`control-card__status control-card__status--${currentState}`}>
            {currentState === 'on' ? 'Active' : 'Idle'}
          </span>
        </div>
      </div>

      <div className="control-card__body">
        <div className="control-card__buttons">
          <button
            className="control-button control-button--primary"
            onClick={handleBeep}
            disabled={loading || disabled}
          >
            <FaBell />
            <span>Beep</span>
          </button>

          <button
            className="control-button control-button--warning"
            onClick={handleAlarm}
            disabled={loading || disabled}
          >
            <FaExclamationTriangle />
            <span>Alarm</span>
          </button>

          {onToggle && (
            <button
              className="control-button control-button--secondary"
              onClick={handleToggle}
              disabled={loading || disabled}
            >
              <span>{currentState === 'on' ? 'Turn Off' : 'Turn On'}</span>
            </button>
          )}
        </div>

        {isActive && (
          <div className="control-card__indicator control-card__indicator--active">
            🔊 Sound playing...
          </div>
        )}
      </div>
    </div>
  );
};

export default BuzzerControl;