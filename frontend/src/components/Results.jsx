import React, { useState } from 'react';
import BuildOrchestrator from './BuildOrchestrator';
import '../styles/Results.css';

const Results = ({ data, onReset }) => {
  const { primary, detections, min_confidence_threshold } = data;
  const [showOrchestrator, setShowOrchestrator] = useState(true);

  const getConfidenceBadgeClass = (level) => {
    const levelMap = {
      'unreliable': 'badge-unreliable',
      'moderate': 'badge-moderate',
      'high': 'badge-high',
      'very_high': 'badge-very-high'
    };
    return levelMap[level] || 'badge-moderate';
  };

  const getConfidenceColor = (score) => {
    if (score < 0.45) return '#ef4444';
    if (score < 0.65) return '#f59e0b';
    if (score < 0.80) return '#10b981';
    return '#8b5cf6';
  };

  const formatConfidenceLevel = (level) => {
    return level.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <div className="results-title-section">
          <h2 className="results-title">Detection Results</h2>
          <p className="results-subtitle">
            {detections.length} detection{detections.length !== 1 ? 's' : ''} found 
            (min confidence: {min_confidence_threshold.toFixed(2)})
          </p>
        </div>
        <button onClick={onReset} className="reset-btn">
          ← New Scan
        </button>
      </div>

      {/* Primary Detection */}
      <div className="primary-card">
        <div className="card-header primary-header">
          <div className="header-content">
            <span className="primary-badge">⭐ Primary Detection</span>
            <h3 className="card-title">{primary.primary_language}</h3>
          </div>
          <div className="confidence-circle" style={{ '--progress': primary.confidence_score }}>
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle
                cx="40"
                cy="40"
                r="35"
                fill="none"
                stroke="rgba(255,255,255,0.2)"
                strokeWidth="8"
              />
              <circle
                cx="40"
                cy="40"
                r="35"
                fill="none"
                stroke={getConfidenceColor(primary.confidence_score)}
                strokeWidth="8"
                strokeDasharray={`${primary.confidence_score * 220} 220`}
                strokeLinecap="round"
                transform="rotate(-90 40 40)"
              />
            </svg>
            <div className="confidence-value">
              {(primary.confidence_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="card-body">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Language</span>
              <span className="info-value">{primary.primary_language}</span>
            </div>
            
            {primary.framework && (
              <div className="info-item">
                <span className="info-label">Framework</span>
                <span className="info-value">{primary.framework}</span>
              </div>
            )}
            
            {primary.build_tool && (
              <div className="info-item">
                <span className="info-label">Build Tool</span>
                <span className="info-value">{primary.build_tool}</span>
              </div>
            )}
            
            <div className="info-item">
              <span className="info-label">Build Required</span>
              <span className={`info-value ${primary.build_required ? 'text-warning' : 'text-success'}`}>
                {primary.build_required ? 'Yes' : 'No'}
              </span>
            </div>

            <div className="info-item">
              <span className="info-label">Confidence Level</span>
              <span className={`confidence-badge ${getConfidenceBadgeClass(primary.confidence_level)}`}>
                {formatConfidenceLevel(primary.confidence_level)}
              </span>
            </div>
          </div>

          {(primary.install_command || primary.build_command) && (
            <div className="commands-section">
              <h4 className="commands-title">Commands</h4>
              
              {primary.install_command && (
                <div className="command-block">
                  <div className="command-header">
                    <span className="command-label">Install</span>
                    <button 
                      className="copy-btn"
                      onClick={() => navigator.clipboard.writeText(primary.install_command)}
                    >
                      📋 Copy
                    </button>
                  </div>
                  <code className="command-code">{primary.install_command}</code>
                </div>
              )}
              
              {primary.build_command && (
                <div className="command-block">
                  <div className="command-header">
                    <span className="command-label">Build</span>
                    <button 
                      className="copy-btn"
                      onClick={() => navigator.clipboard.writeText(primary.build_command)}
                    >
                      📋 Copy
                    </button>
                  </div>
                  <code className="command-code">{primary.build_command}</code>
                </div>
              )}
            </div>
          )}

          {primary.detected_files && primary.detected_files.length > 0 && (
            <div className="files-section">
              <h4 className="files-title">Detected Files ({primary.detected_files.length})</h4>
              <div className="files-list">
                {primary.detected_files.map((file, idx) => (
                  <span key={idx} className="file-tag">{file}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Additional Detections */}
      {detections.length > 1 && (
        <div className="additional-detections">
          <h3 className="section-title">Additional Detections</h3>
          <div className="detections-grid">
            {detections
              .filter(d => d.confidence_score !== primary.confidence_score || d.primary_language !== primary.primary_language)
              .map((detection, idx) => (
                <div key={idx} className="detection-card">
                  <div className="detection-header">
                    <h4 className="detection-language">{detection.primary_language}</h4>
                    <div className="detection-score" style={{ color: getConfidenceColor(detection.confidence_score) }}>
                      {(detection.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="detection-details">
                    {detection.framework && (
                      <div className="detail-row">
                        <span className="detail-label">Framework:</span>
                        <span className="detail-value">{detection.framework}</span>
                      </div>
                    )}
                    {detection.build_tool && (
                      <div className="detail-row">
                        <span className="detail-label">Build Tool:</span>
                        <span className="detail-value">{detection.build_tool}</span>
                      </div>
                    )}
                    <div className="detail-row">
                      <span className="detail-label">Confidence:</span>
                      <span className={`confidence-badge small ${getConfidenceBadgeClass(detection.confidence_level)}`}>
                        {formatConfidenceLevel(detection.confidence_level)}
                      </span>
                    </div>
                  </div>

                  {detection.detected_files && detection.detected_files.length > 0 && (
                    <div className="detection-files">
                      <span className="files-count">📁 {detection.detected_files.length} file{detection.detected_files.length !== 1 ? 's' : ''}</span>
                    </div>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Build Orchestrator Integration */}
      {showOrchestrator && (
        <BuildOrchestrator detectionResult={primary} />
      )}
    </div>
  );
};

export default Results;
