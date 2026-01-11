/**
 * Header Component
 */

import React from 'react';
import { FaHome, FaGithub } from 'react-icons/fa';
import StatusIndicator from '../Common/StatusIndicator';
import './Layout.scss';

const Header = ({ 
  apiStatus = 'unknown', 
  pubnubStatus = 'unknown',
  unresolvedAlerts = 0 
}) => {
  return (
    <header className="header">
      <div className="header__container">
        <div className="header__brand">
          <FaHome className="header__logo" />
          <div className="header__text">
            <h1 className="header__title">Smart Home IoT</h1>
            <p className="header__subtitle">Environmental Monitoring</p>
          </div>
        </div>

        <div className="header__status">
          <StatusIndicator 
            status={apiStatus} 
            label="API" 
            size="small"
          />
          <StatusIndicator 
            status={pubnubStatus} 
            label="Real-time" 
            size="small"
          />
          
          {unresolvedAlerts > 0 && (
            <div className="header__alerts">
              <span className="header__alerts-badge">{unresolvedAlerts}</span>
              <span className="header__alerts-text">Alerts</span>
            </div>
          )}
        </div>

        <div className="header__actions">
          <a 
            href="https://github.com/HenriqueJoanoni/smart-home-iot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="header__link"
            title="View on GitHub"
          >
            <FaGithub />
          </a>
        </div>
      </div>
    </header>
  );
};

export default Header;