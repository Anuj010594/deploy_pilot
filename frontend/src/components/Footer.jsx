import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">Project Detector</h3>
            <p className="footer-description">
              Intelligent platform and build tool detection for modern development workflows
            </p>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Features</h4>
            <ul className="footer-list">
              <li>Multi-language detection</li>
              <li>Framework identification</li>
              <li>Build tool recognition</li>
              <li>Confidence scoring</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">API Info</h4>
            <ul className="footer-list">
              <li>Version: 1.0.0</li>
              <li>REST API</li>
              <li>FastAPI Backend</li>
              <li>React Frontend</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Connect</h4>
            <div className="footer-links">
              <a href="/api/health" className="footer-link" target="_blank" rel="noopener noreferrer">
                API Health
              </a>
              <a href="http://localhost:8000/docs" className="footer-link" target="_blank" rel="noopener noreferrer">
                API Docs
              </a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © 2024 Project Detector. Built with ❤️ using FastAPI & React
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
