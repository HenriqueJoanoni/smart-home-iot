/**
 * Footer Component
 */

import React from 'react';
import { formatRelativeTime } from '../../utils/formatters';
import './Layout.scss';

const Footer = ({ lastUpdate = null }) => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__container">
        <div className="footer__section">
          <p className="footer__text">
            © {currentYear} Smart Home IoT Dashboard
          </p>
          <p className="footer__author">
            Developed by <strong>Jose Henrique Joanoni</strong>
          </p>
        </div>

        {lastUpdate && (
          <div className="footer__section">
            <p className="footer__update">
              Last update: {formatRelativeTime(lastUpdate)}
            </p>
          </div>
        )}

        <div className="footer__section">
          <div className="footer__tech">
            <span className="footer__badge">React</span>
            <span className="footer__badge">PubNub</span>
            <span className="footer__badge">Raspberry Pi</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;