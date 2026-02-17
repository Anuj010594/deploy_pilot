import React, { useState } from 'react';
import { scanRepository } from '../services/api';
import '../styles/ScanForm.css';

const ScanForm = ({ onScanStart, onScanComplete, onScanError, loading }) => {
  const [inputType, setInputType] = useState('github');
  const [githubUrl, setGithubUrl] = useState('');
  const [zipFile, setZipFile] = useState(null);
  const [minConfidence, setMinConfidence] = useState(0.45);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (inputType === 'github' && !githubUrl.trim()) {
      onScanError(new Error('Please enter a GitHub URL'));
      return;
    }

    if (inputType === 'zip' && !zipFile) {
      onScanError(new Error('Please select a ZIP file'));
      return;
    }

    onScanStart();

    const formData = new FormData();
    
    if (inputType === 'github') {
      formData.append('github_url', githubUrl);
    } else {
      formData.append('zip_file', zipFile);
    }
    
    formData.append('min_confidence', minConfidence);

    try {
      const result = await scanRepository(formData);
      onScanComplete(result);
    } catch (error) {
      onScanError(error);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.zip')) {
      setZipFile(file);
    } else {
      onScanError(new Error('Please select a valid ZIP file'));
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.zip')) {
        setZipFile(file);
      } else {
        onScanError(new Error('Please drop a valid ZIP file'));
      }
    }
  };

  const getConfidenceLabel = () => {
    if (minConfidence < 0.45) return 'Unreliable';
    if (minConfidence < 0.65) return 'Moderate';
    if (minConfidence < 0.80) return 'High';
    return 'Very High';
  };

  return (
    <div className="scan-form-container">
      <form onSubmit={handleSubmit} className="scan-form">
        <div className="form-section">
          <label className="section-label">Source Type</label>
          <div className="input-type-selector">
            <button
              type="button"
              className={`type-btn ${inputType === 'github' ? 'active' : ''}`}
              onClick={() => setInputType('github')}
            >
              <span className="type-icon">🌐</span>
              <span>GitHub URL</span>
            </button>
            <button
              type="button"
              className={`type-btn ${inputType === 'zip' ? 'active' : ''}`}
              onClick={() => setInputType('zip')}
            >
              <span className="type-icon">📦</span>
              <span>ZIP Upload</span>
            </button>
          </div>
        </div>

        {inputType === 'github' ? (
          <div className="form-section">
            <label htmlFor="github-url" className="input-label">
              GitHub Repository URL
            </label>
            <input
              id="github-url"
              type="text"
              className="text-input"
              placeholder="https://github.com/username/repository"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              disabled={loading}
            />
            <p className="input-hint">Enter the full GitHub repository URL</p>
          </div>
        ) : (
          <div className="form-section">
            <label className="input-label">Upload ZIP File</label>
            <div
              className={`file-drop-zone ${dragActive ? 'drag-active' : ''} ${zipFile ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                id="zip-file"
                type="file"
                accept=".zip"
                onChange={handleFileChange}
                disabled={loading}
                className="file-input"
              />
              <label htmlFor="zip-file" className="file-label">
                {zipFile ? (
                  <>
                    <span className="file-icon">✓</span>
                    <span className="file-name">{zipFile.name}</span>
                    <span className="file-size">
                      ({(zipFile.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </>
                ) : (
                  <>
                    <span className="upload-icon">📁</span>
                    <span className="upload-text">
                      Drop your ZIP file here or click to browse
                    </span>
                  </>
                )}
              </label>
            </div>
          </div>
        )}

        <div className="form-section">
          <label htmlFor="confidence" className="input-label">
            Minimum Confidence Threshold
            <span className="confidence-badge">{getConfidenceLabel()}</span>
          </label>
          <div className="slider-container">
            <input
              id="confidence"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              disabled={loading}
              className="confidence-slider"
            />
            <div className="slider-labels">
              <span>0.0</span>
              <span className="slider-value">{minConfidence.toFixed(2)}</span>
              <span>1.0</span>
            </div>
          </div>
          <div className="confidence-guide">
            <div className="guide-item">
              <span className="guide-marker unreliable"></span>
              <span>{"< 0.45 Unreliable"}</span>
            </div>
            <div className="guide-item">
              <span className="guide-marker moderate"></span>
              <span>0.45-0.64 Moderate</span>
            </div>
            <div className="guide-item">
              <span className="guide-marker high"></span>
              <span>0.65-0.79 High</span>
            </div>
            <div className="guide-item">
              <span className="guide-marker very-high"></span>
              <span>≥ 0.80 Very High</span>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              <span>Scanning...</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>Scan Project</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ScanForm;
