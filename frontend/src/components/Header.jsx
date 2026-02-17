import React from 'react';
import '../styles/Header.css';

const Header = ({ backendStatus }) => {
  const getStatusInfo = () => {
    switch (backendStatus) {
      case 'healthy':
        return { text: 'Online', className: 'status-healthy', icon: '●' };
      case 'error':
        return { text: 'Offline', className: 'status-error', icon: '●' };
      default:
        return { text: 'Checking...', className: 'status-checking', icon: '○' };
    }
  };

  const status = getStatusInfo();

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">🔍</div>
            <div className="logo-text">
              <h2>Project Detector</h2>
              <span className="logo-subtitle">Platform Intelligence</span>
            </div>
          </div>

          <div className="status-section">
            <div className={`status-indicator ${status.className}`}>
              <span className="status-dot">{status.icon}</span>
              <span className="status-text">API {status.text}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
