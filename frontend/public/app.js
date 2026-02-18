// API Configuration
const API_BASE_URL = '/api';

// DOM Elements
const scanForm = document.getElementById('scanForm');
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const githubUrlInput = document.getElementById('githubUrl');
const zipFileInput = document.getElementById('zipFile');
const minConfidenceInput = document.getElementById('minConfidence');
const confidenceValue = document.getElementById('confidenceValue');
const scanButton = document.getElementById('scanButton');
const apiStatus = document.getElementById('apiStatus');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');
const loadingContainer = document.getElementById('loadingContainer');
const resultsContainer = document.getElementById('resultsContainer');
const fileUploadDisplay = document.querySelector('.file-upload-display .file-text');

// State
let currentTab = 'github';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkBackendHealth();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });

    // Form submission
    scanForm.addEventListener('submit', handleFormSubmit);

    // Confidence slider
    minConfidenceInput.addEventListener('input', (e) => {
        confidenceValue.textContent = parseFloat(e.target.value).toFixed(2);
    });

    // File upload display
    zipFileInput.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || 'Choose a ZIP file or drag it here';
        fileUploadDisplay.textContent = fileName;
    });
}

// Tab Switching
function switchTab(tab) {
    currentTab = tab;

    // Update buttons
    tabButtons.forEach(button => {
        if (button.dataset.tab === tab) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Update content
    tabContents.forEach(content => {
        if (content.id === `${tab}-tab`) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });

    // Clear inputs from inactive tab
    if (tab === 'github') {
        zipFileInput.value = '';
        fileUploadDisplay.textContent = 'Choose a ZIP file or drag it here';
    } else {
        githubUrlInput.value = '';
    }
}

// Backend Health Check
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateApiStatus('healthy');
        } else {
            updateApiStatus('error');
        }
    } catch (error) {
        updateApiStatus('error');
    }
}

function updateApiStatus(status) {
    const statusMap = {
        healthy: { text: 'Online', className: 'status-healthy', icon: '●' },
        error: { text: 'Offline', className: 'status-error', icon: '●' },
        checking: { text: 'Checking...', className: 'status-checking', icon: '○' }
    };

    const statusInfo = statusMap[status];
    apiStatus.className = `status-indicator ${statusInfo.className}`;
    apiStatus.innerHTML = `
        <span class="status-dot">${statusInfo.icon}</span>
        <span class="status-text">API ${statusInfo.text}</span>
    `;
}

// Form Submission
async function handleFormSubmit(e) {
    e.preventDefault();

    // Hide previous results/errors
    hideElement(errorContainer);
    hideElement(resultsContainer);

    // Validate input
    const formData = new FormData();
    
    if (currentTab === 'github') {
        const githubUrl = githubUrlInput.value.trim();
        if (!githubUrl) {
            showError('Please enter a GitHub URL');
            return;
        }
        formData.append('github_url', githubUrl);
    } else {
        const zipFile = zipFileInput.files[0];
        if (!zipFile) {
            showError('Please select a ZIP file');
            return;
        }
        formData.append('zip_file', zipFile);
    }

    // Add confidence threshold
    formData.append('min_confidence', minConfidenceInput.value);

    // Show loading
    showElement(loadingContainer);
    scanButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Scan failed');
        }

        // Show results
        displayResults(data);
    } catch (error) {
        showError(error.message || 'Failed to scan repository. Please check if the backend is running.');
    } finally {
        hideElement(loadingContainer);
        scanButton.disabled = false;
    }
}

// Display Results
function displayResults(data) {
    hideElement(errorContainer);
    
    let html = `
        <div class="results-header">
            <h2 class="results-title">Detection Results</h2>
            <button class="btn-reset" onclick="resetForm()">New Scan</button>
        </div>
    `;

    // Show primary detection
    if (data.primary) {
        html += `
            <div class="detection-section primary-detection">
                <div class="section-header">
                    <span class="section-icon">⭐</span>
                    <h3 class="section-title">Primary Detection</h3>
                </div>
                ${createPrimaryDetectionCard(data.primary)}
            </div>
        `;
    }

    // Show all detections
    if (data.detections && data.detections.length > 0) {
        html += `
            <div class="detection-section">
                <div class="section-header">
                    <span class="section-icon">📋</span>
                    <h3 class="section-title">All Detections (${data.detections.length})</h3>
                </div>
                <div class="detection-grid">
                    ${data.detections.map(detection => createDetectionCard(detection)).join('')}
                </div>
            </div>
        `;
    }

    // If no detections
    if (!data.detections || data.detections.length === 0) {
        html += `
            <div class="detection-section">
                <p style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                    No detections found with the current confidence threshold (${data.min_confidence_threshold || 0.45}). 
                    Try lowering the minimum confidence value.
                </p>
            </div>
        `;
    }

    resultsContainer.innerHTML = html;
    showElement(resultsContainer);
    
    // Add Build Orchestrator Panel if primary detection exists
    if (data.primary) {
        addBuildOrchestratorPanel(data);
    }
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createPrimaryDetectionCard(detection) {
    const confidenceBadge = getConfidenceBadge(detection.confidence_score);
    
    return `
        <div class="primary-card" style="background: var(--card-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
            <div class="primary-info" style="display: grid; gap: 1rem;">
                <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                    <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Language:</span>
                    <span class="info-value" style="font-weight: 700; color: var(--primary-color);">${detection.primary_language || 'Unknown'}</span>
                </div>
                ${detection.framework ? `
                    <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                        <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Framework:</span>
                        <span class="info-value">${detection.framework}</span>
                    </div>
                ` : ''}
                ${detection.build_tool ? `
                    <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                        <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Build Tool:</span>
                        <span class="info-value">${detection.build_tool}</span>
                    </div>
                ` : ''}
                <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                    <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Build Required:</span>
                    <span class="info-value">${detection.build_required ? '✅ Yes' : '❌ No'}</span>
                </div>
                ${detection.build_command ? `
                    <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                        <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Build Command:</span>
                        <span class="info-value"><code style="background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">${detection.build_command}</code></span>
                    </div>
                ` : ''}
                ${detection.install_command ? `
                    <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                        <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Install Command:</span>
                        <span class="info-value"><code style="background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">${detection.install_command}</code></span>
                    </div>
                ` : ''}
                <div class="info-row" style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                    <span class="info-label" style="font-weight: 600; color: var(--text-secondary);">Confidence:</span>
                    <span class="confidence-badge ${confidenceBadge.class}">
                        ${confidenceBadge.text} (${(detection.confidence_score * 100).toFixed(1)}%)
                    </span>
                </div>
            </div>
        </div>
    `;
}

function createDetectionCard(detection) {
    const confidenceBadge = getConfidenceBadge(detection.confidence_score);
    const fileCount = detection.detected_files?.length || 0;
    
    return `
        <div class="detection-item">
            <div class="detection-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div class="detection-name" style="font-weight: 700; font-size: 1.1rem;">${detection.primary_language || 'Unknown'}</div>
                <span class="confidence-badge ${confidenceBadge.class}">
                    ${(detection.confidence_score * 100).toFixed(1)}%
                </span>
            </div>
            <div class="detection-details" style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.9rem;">
                ${detection.framework ? `<div class="detail-item">🎯 Framework: <strong>${detection.framework}</strong></div>` : ''}
                ${detection.build_tool ? `<div class="detail-item">🔧 Build Tool: <strong>${detection.build_tool}</strong></div>` : ''}
                ${detection.build_command ? `<div class="detail-item">📦 <code style="background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">${detection.build_command}</code></div>` : ''}
                <div class="detail-item" style="color: var(--text-secondary);">📄 ${fileCount} file${fileCount !== 1 ? 's' : ''} detected</div>
            </div>
        </div>
    `;
}

function getConfidenceBadge(confidence) {
    if (confidence >= 0.80) {
        return { text: 'Very High', class: 'very-high' };
    } else if (confidence >= 0.65) {
        return { text: 'High', class: 'high' };
    } else if (confidence >= 0.45) {
        return { text: 'Moderate', class: 'moderate' };
    } else {
        return { text: 'Low', class: 'low' };
    }
}

// Helper Functions
function showElement(element) {
    element.classList.remove('hidden');
}

function hideElement(element) {
    element.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    showElement(errorContainer);
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Build Orchestrator Integration
async function addBuildOrchestratorPanel(detectionData) {
    const orchestratorHTML = `
        <div class="detection-section" id="orchestratorSection" style="margin-top: 2rem;">
            <div class="section-header">
                <span class="section-icon">🔧</span>
                <h3 class="section-title">Build Orchestrator</h3>
            </div>
            <div class="orchestrator-panel" style="background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border-color); padding: 1.5rem;">
                <div class="orchestrator-loading" style="text-align: center; padding: 2rem;">
                    <div class="loading-spinner" style="display: inline-block; width: 40px; height: 40px; border: 4px solid var(--border-color); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">Validating project files...</p>
                </div>
            </div>
        </div>
    `;
    
    resultsContainer.insertAdjacentHTML('beforeend', orchestratorHTML);
    
    // Call validation API
    try {
        const response = await fetch('/api/orchestrator/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                detection_result: detectionData.primary,
                project_path: detectionData.project_path || '/tmp/scanned_project'
            })
        });
        
        if (!response.ok) throw new Error('Validation failed');
        
        const validationResult = await response.json();
        displayOrchestratorResults(validationResult, detectionData.primary);
    } catch (error) {
        document.querySelector('.orchestrator-panel').innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--error-color);">
                <p>⚠️ Could not validate project files</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">${error.message}</p>
            </div>
        `;
    }
}

function displayOrchestratorResults(validation, detection) {
    const panel = document.querySelector('.orchestrator-panel');
    
    let html = `
        <div class="orchestrator-tabs" style="display: flex; gap: 1rem; border-bottom: 2px solid var(--border-color); margin-bottom: 1.5rem;">
            <button class="orch-tab active" data-orch-tab="validation" onclick="switchOrchTab('validation')" style="background: none; border: none; padding: 0.75rem 1.5rem; cursor: pointer; font-weight: 600; border-bottom: 3px solid transparent; transition: all 0.3s;">
                ${validation.status === 'ready' ? '✅' : '⚠️'} Validation
            </button>
            <button class="orch-tab" data-orch-tab="generate" onclick="switchOrchTab('generate')" style="background: none; border: none; padding: 0.75rem 1.5rem; cursor: pointer; font-weight: 600; border-bottom: 3px solid transparent; transition: all 0.3s;">
                🔧 Generate Files
            </button>
            <button class="orch-tab" data-orch-tab="docker" onclick="switchOrchTab('docker')" style="background: none; border: none; padding: 0.75rem 1.5rem; cursor: pointer; font-weight: 600; border-bottom: 3px solid transparent; transition: all 0.3s;">
                🐳 Docker
            </button>
        </div>
        
        <div class="orch-content active" id="validation-content">
            ${createValidationContent(validation)}
        </div>
        
        <div class="orch-content" id="generate-content" style="display: none;">
            ${createGenerateContent(validation, detection)}
        </div>
        
        <div class="orch-content" id="docker-content" style="display: none;">
            ${createDockerContent(detection)}
        </div>
    `;
    
    panel.innerHTML = html;
}

function createValidationContent(validation) {
    let html = `<div class="validation-results">`;
    
    html += `
        <div class="status-card" style="background: ${validation.status === 'ready' ? '#d4edda' : '#fff3cd'}; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid ${validation.status === 'ready' ? '#c3e6cb' : '#ffeeba'};">
            <h4 style="margin: 0 0 0.5rem 0; color: ${validation.status === 'ready' ? '#155724' : '#856404'};">${validation.status === 'ready' ? '✅ Project is ready to build' : '⚠️ Missing required files'}</h4>
            <p style="margin: 0; font-size: 0.9rem; color: ${validation.status === 'ready' ? '#155724' : '#856404'};">
                ${validation.status === 'ready' ? 'All required build files are present' : `${validation.missing_files?.length || 0} file(s) need attention`}
            </p>
        </div>
    `;
    
    if (validation.missing_files && validation.missing_files.length > 0) {
        html += `
            <div class="missing-files" style="margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem;">Missing Files:</h4>
                ${validation.missing_files.map(file => `
                    <div class="file-item" style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600;">${file.files?.join(', ') || 'Unknown'}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">${file.description || ''}</div>
                        <span class="severity-badge" style="display: inline-block; margin-top: 0.5rem; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; background: ${file.severity === 'CRITICAL' ? '#dc3545' : '#ffc107'}; color: white;">
                            ${file.severity}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (validation.suggestions && validation.suggestions.length > 0) {
        html += `
            <div class="suggestions">
                <h4 style="margin-bottom: 1rem;">Suggestions:</h4>
                ${validation.suggestions.map((sug, idx) => `
                    <div class="suggestion-item" style="background: var(--bg-secondary); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid var(--primary-color);">
                        <div style="font-weight: 600;">${idx + 1}. ${sug.action}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">${sug.description}</div>
                        ${sug.automated ? '<span style="color: #28a745; font-size: 0.8rem; margin-top: 0.5rem; display: inline-block;">🤖 Can be automated</span>' : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    html += `</div>`;
    return html;
}

function createGenerateContent(validation, detection) {
    const language = detection.primary_language || 'Unknown';
    
    return `
        <div class="generate-files">
            <h4 style="margin-bottom: 1rem;">Generate Missing Files</h4>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Select a file type to generate with customizable options
            </p>
            
            <div class="file-generators" style="display: grid; gap: 1rem;">
                ${validation.missing_files?.filter(f => f.can_generate).map(file => `
                    <button class="generate-btn" onclick="generateFile('${file.file_type}', '${language}')" style="background: var(--primary-color); color: white; padding: 1rem; border: none; border-radius: 8px; cursor: pointer; text-align: left; transition: transform 0.2s;">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">Generate ${file.files?.[0] || file.file_type}</div>
                        <div style="font-size: 0.85rem; opacity: 0.9;">${file.description}</div>
                    </button>
                `).join('') || '<p style="color: var(--text-secondary);">No files can be auto-generated. All required files are present!</p>'}
            </div>
            
            <div id="generatedFilePreview" style="margin-top: 1.5rem;"></div>
        </div>
    `;
}

function createDockerContent(detection) {
    return `
        <div class="docker-generation">
            <h4 style="margin-bottom: 1rem;">Docker Configuration</h4>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Generate an optimized Dockerfile for ${detection.primary_language}
            </p>
            
            <button class="generate-btn" onclick="generateDockerfile('${detection.primary_language}')" style="background: #0db7ed; color: white; padding: 1rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: transform 0.2s;">
                🐳 Generate Dockerfile
            </button>
            
            <div id="dockerfilePreview" style="margin-top: 1.5rem;"></div>
        </div>
    `;
}

function switchOrchTab(tab) {
    document.querySelectorAll('.orch-tab').forEach(btn => {
        if (btn.dataset.orchTab === tab) {
            btn.classList.add('active');
            btn.style.borderBottom = '3px solid var(--primary-color)';
            btn.style.color = 'var(--primary-color)';
        } else {
            btn.classList.remove('active');
            btn.style.borderBottom = '3px solid transparent';
            btn.style.color = 'var(--text-primary)';
        }
    });
    
    document.querySelectorAll('.orch-content').forEach(content => {
        content.style.display = content.id === `${tab}-content` ? 'block' : 'none';
    });
}

async function generateFile(fileType, language) {
    const preview = document.getElementById('generatedFilePreview');
    preview.innerHTML = '<div style="text-align: center; padding: 1rem;">Generating...</div>';
    
    try {
        const response = await fetch('/api/orchestrator/generate-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                platform: language,
                file_type: fileType,
                version_config: {}
            })
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        const result = await response.json();
        
        preview.innerHTML = `
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h5 style="margin: 0;">${result.file_name}</h5>
                    <button onclick="downloadFile('${result.file_name}', \`${btoa(result.content)}\`)" style="background: #28a745; color: white; padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer;">
                        ⬇️ Download
                    </button>
                </div>
                <pre style="background: var(--card-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; max-height: 400px;"><code>${escapeHtml(result.content)}</code></pre>
            </div>
        `;
    } catch (error) {
        preview.innerHTML = `<div style="color: #dc3545; padding: 1rem;">Error: ${error.message}</div>`;
    }
}

async function generateDockerfile(language) {
    const preview = document.getElementById('dockerfilePreview');
    preview.innerHTML = '<div style="text-align: center; padding: 1rem;">Generating Dockerfile...</div>';
    
    try {
        const response = await fetch('/api/orchestrator/generate-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                platform: language,
                file_type: 'Dockerfile',
                version_config: {}
            })
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        const result = await response.json();
        
        preview.innerHTML = `
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h5 style="margin: 0;">Dockerfile</h5>
                    <button onclick="downloadFile('Dockerfile', \`${btoa(result.content)}\`)" style="background: #0db7ed; color: white; padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer;">
                        ⬇️ Download Dockerfile
                    </button>
                </div>
                <pre style="background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 6px; overflow-x: auto; max-height: 400px;"><code>${escapeHtml(result.content)}</code></pre>
            </div>
        `;
    } catch (error) {
        preview.innerHTML = `<div style="color: #dc3545; padding: 1rem;">Error: ${error.message}</div>`;
    }
}

function downloadFile(filename, base64Content) {
    const content = atob(base64Content);
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function resetForm() {
    scanForm.reset();
    hideElement(errorContainer);
    hideElement(resultsContainer);
    confidenceValue.textContent = '0.45';
    fileUploadDisplay.textContent = 'Choose a ZIP file or drag it here';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Drag and Drop Support
const fileUploadWrapper = document.querySelector('.file-upload-wrapper');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, () => {
        fileUploadWrapper.querySelector('.file-upload-display').style.borderColor = 'var(--primary-color)';
        fileUploadWrapper.querySelector('.file-upload-display').style.background = 'var(--bg-tertiary)';
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, () => {
        fileUploadWrapper.querySelector('.file-upload-display').style.borderColor = 'var(--border-color)';
        fileUploadWrapper.querySelector('.file-upload-display').style.background = 'var(--bg-secondary)';
    }, false);
});

fileUploadWrapper.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0 && files[0].name.endsWith('.zip')) {
        zipFileInput.files = files;
        fileUploadDisplay.textContent = files[0].name;
        switchTab('upload');
    }
}, false);
