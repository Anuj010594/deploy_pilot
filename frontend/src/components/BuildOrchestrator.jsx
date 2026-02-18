import React, { useState, useEffect } from 'react';
import { 
  validateProject, 
  generateTemplate, 
  getDockerOptions, 
  generateDockerfile,
  getVersionOptions 
} from '../services/api';
import '../styles/BuildOrchestrator.css';

const BuildOrchestrator = ({ detectionResult }) => {
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('validation');
  const [generatedContent, setGeneratedContent] = useState(null);
  const [versionOptions, setVersionOptions] = useState(null);
  const [selectedVersions, setSelectedVersions] = useState({});
  const [dockerOptions, setDockerOptions] = useState(null);

  useEffect(() => {
    if (detectionResult) {
      performValidation();
      loadVersionOptions();
    }
  }, [detectionResult]);

  const performValidation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await validateProject(detectionResult, 'temp/repo');
      setValidationResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadVersionOptions = async () => {
    try {
      const options = await getVersionOptions(detectionResult.primary_language);
      setVersionOptions(options);
    } catch (err) {
      console.error('Failed to load version options:', err);
    }
  };

  const handleGenerateTemplate = async (fileType) => {
    setLoading(true);
    setError(null);
    try {
      const versionConfig = {
        runtime_version: selectedVersions.runtime_version,
        ...selectedVersions
      };

      const projectContext = {
        framework: detectionResult.framework,
        build_tool: detectionResult.build_tool
      };

      const result = await generateTemplate(
        detectionResult.primary_language,
        fileType,
        versionConfig,
        projectContext
      );

      setGeneratedContent(result);
      setActiveTab('generated');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDockerfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const versionConfig = {
        runtime_version: selectedVersions.runtime_version,
        expose_port: selectedVersions.port || getDefaultPort(),
        ...selectedVersions
      };

      const projectContext = {
        framework: detectionResult.framework,
        build_tool: detectionResult.build_tool,
        needs_build: ['React', 'Vue', 'Angular', 'Next.js'].includes(detectionResult.framework)
      };

      const result = await generateDockerfile(
        detectionResult.primary_language,
        versionConfig,
        projectContext
      );

      setGeneratedContent(result);
      setActiveTab('generated');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckDockerOptions = async () => {
    setLoading(true);
    setError(null);
    try {
      const options = await getDockerOptions(
        'temp/repo',
        detectionResult.primary_language,
        selectedVersions
      );
      setDockerOptions(options);
      setActiveTab('docker');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultPort = () => {
    const portMap = {
      'Java': 8080,
      'Node.js': 3000,
      'Python': 8000,
      '.NET': 80,
      'Go': 8080,
      'Rust': 8080,
      'Ruby': 3000,
      'PHP': 80
    };
    return portMap[detectionResult.primary_language] || 8080;
  };

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getSeverityBadge = (severity) => {
    const classes = {
      critical: 'severity-critical',
      warning: 'severity-warning',
      info: 'severity-info'
    };
    return <span className={`severity-badge ${classes[severity]}`}>{severity}</span>;
  };

  if (!detectionResult) {
    return (
      <div className="build-orchestrator">
        <p className="no-detection">No detection result available. Please scan a project first.</p>
      </div>
    );
  }

  return (
    <div className="build-orchestrator">
      <h2>🏗️ Build Orchestrator</h2>
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'validation' ? 'active' : ''}`}
          onClick={() => setActiveTab('validation')}
        >
          Validation
        </button>
        <button 
          className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          Generate Files
        </button>
        <button 
          className={`tab ${activeTab === 'docker' ? 'active' : ''}`}
          onClick={() => setActiveTab('docker')}
        >
          Docker
        </button>
        <button 
          className={`tab ${activeTab === 'generated' ? 'active' : ''}`}
          onClick={() => setActiveTab('generated')}
          disabled={!generatedContent}
        >
          Generated Content
        </button>
      </div>

      {loading && <div className="loading-spinner">Loading...</div>}

      {/* Validation Tab */}
      {activeTab === 'validation' && validationResult && (
        <div className="validation-results">
          <div className={`status-badge status-${validationResult.status}`}>
            Status: {validationResult.status.replace('_', ' ').toUpperCase()}
          </div>

          {validationResult.missing_files && validationResult.missing_files.length > 0 && (
            <div className="missing-files-section">
              <h3>Missing Files</h3>
              <ul className="missing-files-list">
                {validationResult.missing_files.map((file, index) => (
                  <li key={index} className="missing-file-item">
                    <div className="file-header">
                      <strong>{file.file_name}</strong>
                      {getSeverityBadge(file.severity)}
                    </div>
                    <p className="file-description">{file.description}</p>
                    {file.can_generate && (
                      <span className="can-generate">✓ Can be auto-generated</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {validationResult.suggestions && validationResult.suggestions.length > 0 && (
            <div className="suggestions-section">
              <h3>Suggestions</h3>
              <ul className="suggestions-list">
                {validationResult.suggestions.map((suggestion, index) => (
                  <li key={index} className="suggestion-item">
                    <div className="suggestion-header">
                      <strong>{suggestion.action}</strong>
                      {suggestion.automated && <span className="automated-badge">Automated</span>}
                    </div>
                    <p className="suggestion-description">{suggestion.description}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {validationResult.available_actions && validationResult.available_actions.length > 0 && (
            <div className="available-actions">
              <h3>Available Actions</h3>
              <div className="action-buttons">
                {validationResult.available_actions.map((action, index) => (
                  <button key={index} className="action-button">
                    {action.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="templates-section">
          <h3>Generate Configuration Files</h3>
          
          {versionOptions && (
            <div className="version-selection">
              <h4>Select Versions</h4>
              {Object.entries(versionOptions.version_options || {}).map(([key, options]) => (
                <div key={key} className="version-option-group">
                  <label>{key.replace('_', ' ').toUpperCase()}</label>
                  <select 
                    onChange={(e) => setSelectedVersions({...selectedVersions, [key]: e.target.value})}
                  >
                    <option value="">Select {key}</option>
                    {options.map((opt, idx) => (
                      <option key={idx} value={opt.version}>
                        {opt.version} {opt.recommended ? '(Recommended)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          )}

          <div className="template-buttons">
            {getTemplateButtons().map((btn, index) => (
              <button 
                key={index}
                className="template-button"
                onClick={() => handleGenerateTemplate(btn.fileType)}
                disabled={loading}
              >
                Generate {btn.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Docker Tab */}
      {activeTab === 'docker' && (
        <div className="docker-section">
          <h3>Docker Configuration</h3>
          <button 
            className="primary-button"
            onClick={handleCheckDockerOptions}
            disabled={loading}
          >
            Check Dockerfile Status
          </button>

          {dockerOptions && (
            <div className="docker-options-result">
              <div className={`docker-status status-${dockerOptions.dockerfile_status}`}>
                Dockerfile Status: {dockerOptions.dockerfile_status}
              </div>

              {dockerOptions.options && dockerOptions.options.length > 0 && (
                <div className="docker-options-list">
                  <h4>Available Options</h4>
                  {dockerOptions.options.map((option, index) => (
                    <div key={index} className="docker-option-item">
                      <strong>{option.option.replace('_', ' ')}</strong>
                      <p>{option.description}</p>
                    </div>
                  ))}
                </div>
              )}

              <button 
                className="primary-button"
                onClick={handleGenerateDockerfile}
                disabled={loading}
              >
                Generate Optimized Dockerfile
              </button>
            </div>
          )}
        </div>
      )}

      {/* Generated Content Tab */}
      {activeTab === 'generated' && generatedContent && (
        <div className="generated-content">
          <div className="content-header">
            <h3>Generated: {generatedContent.file_name}</h3>
            <button 
              className="download-button"
              onClick={() => downloadFile(generatedContent.content, generatedContent.file_name)}
            >
              📥 Download
            </button>
          </div>
          <pre className="code-block">
            <code>{generatedContent.content}</code>
          </pre>
        </div>
      )}
    </div>
  );

  function getTemplateButtons() {
    const platform = detectionResult.primary_language;
    const templates = {
      'Java': [
        { label: 'pom.xml', fileType: 'pom.xml' },
        { label: 'build.gradle', fileType: 'build.gradle' }
      ],
      'Node.js': [
        { label: 'package.json', fileType: 'package.json' }
      ],
      'Python': [
        { label: 'requirements.txt', fileType: 'requirements.txt' },
        { label: 'pyproject.toml', fileType: 'pyproject.toml' }
      ],
      '.NET': [
        { label: '.csproj', fileType: 'csproj' }
      ],
      'Go': [
        { label: 'go.mod', fileType: 'go.mod' }
      ],
      'Rust': [
        { label: 'Cargo.toml', fileType: 'Cargo.toml' }
      ],
      'Ruby': [
        { label: 'Gemfile', fileType: 'Gemfile' }
      ],
      'PHP': [
        { label: 'composer.json', fileType: 'composer.json' }
      ]
    };

    return templates[platform] || [];
  }
};

export default BuildOrchestrator;