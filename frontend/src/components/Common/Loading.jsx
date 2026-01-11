/**
 * Loading Component
 * Spinner/loading indicator
 */

import React from 'react';
import './Common.scss';

const Loading = ({ 
  size = 'medium', 
  message = 'Loading...', 
  fullscreen = false 
}) => {
  const sizeClass = `loading-spinner--${size}`;
  const containerClass = fullscreen ? 'loading-container--fullscreen' : 'loading-container';

  return (
    <div className={containerClass}>
      <div className={`loading-spinner ${sizeClass}`}>
        <div className="spinner"></div>
      </div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
};

export default Loading;