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
