/**
 * LED Control Component
 */

import React, { useState } from 'react';
import { FaLightbulb, FaPowerOff } from 'react-icons/fa';
import './Controls.scss';

const LedControl = ({ 
  onToggle, 
  onBrightnessChange,
  loading = false,
  disabled = false,
  currentState = 'off',
  currentBrightness = 100
}) => {
  const [brightness, setBrightness] = useState(currentBrightness);

  const handleToggle = async () => {
    if (onToggle) {
      await onToggle();
    }
  };

  const handleBrightnessChange = (e) => {
    const newBrightness = parseInt(e.target.value);
    setBrightness(newBrightness);
  };

  const handleBrightnessCommit = async () => {
    if (onBrightnessChange) {
      await onBrightnessChange(brightness);
    }
  };

  const isOn = currentState === 'on';

  return (
    <div className="control-card">
      <div className="control-card__header">
        <div className={`control-card__icon ${isOn ? 'control-card__icon--active' : ''}`}>
          <FaLightbulb />
        </div>
        <div className="control-card__info">
          <h3 className="control-card__title">LED</h3>
          <span className={`control-card__status control-card__status--${currentState}`}>
            {isOn ? 'On' : 'Off'}
          </span>
        </div>
      </div>

      <div className="control-card__body">
        <div className="control-card__buttons">
          <button
            className={`control-button control-button--large ${isOn ? 'control-button--danger' : 'control-button--success'}`}
            onClick={handleToggle}
            disabled={loading || disabled}
          >
            {isOn ? (
              <>
                <FaPowerOff />
                <span>Turn Off</span>
              </>
            ) : (
              <>
                <FaLightbulb />
                <span>Turn On</span>
              </>
            )}
          </button>
        </div>

        {onBrightnessChange && (
          <div className="control-card__slider">
            <label className="control-card__label">
              Brightness:  {brightness}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={brightness}
              onChange={handleBrightnessChange}
              onMouseUp={handleBrightnessCommit}
              onTouchEnd={handleBrightnessCommit}
              disabled={loading || disabled || !isOn}
              className="control-slider"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default LedControl;