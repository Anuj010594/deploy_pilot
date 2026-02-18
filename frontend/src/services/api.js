import axios from 'axios';

const API_BASE_URL = '/api';
const ORCHESTRATOR_BASE_URL = 'http://localhost:8001/api'; // Build Orchestrator Service

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const orchestratorApi = axios.create({
  baseURL: ORCHESTRATOR_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Detection Service APIs
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
};

export const scanRepository = async (formData) => {
  try {
    const response = await api.post('/scan', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Scan failed');
    } else if (error.request) {
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      throw new Error('Failed to send request');
    }
  }
};

// Build Orchestrator Service APIs
export const validateProject = async (detectionResult, projectPath) => {
  try {
    const response = await orchestratorApi.post('/validate', {
      detection_result: detectionResult,
      project_path: projectPath || 'temp/repo'
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Validation failed');
    } else {
      throw new Error('Validation service unavailable');
    }
  }
};

export const generateTemplate = async (platform, fileType, versionConfig, projectContext = {}) => {
  try {
    const response = await orchestratorApi.post('/generate-template', {
      platform,
      file_type: fileType,
      version_config: versionConfig,
      project_context: projectContext
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Template generation failed');
    } else {
      throw new Error('Template generation service unavailable');
    }
  }
};

export const getDockerOptions = async (projectPath, platform, versionConfig = {}) => {
  try {
    const response = await orchestratorApi.post('/docker-options', {
      project_path: projectPath || 'temp/repo',
      platform,
      version_config: versionConfig
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get Docker options');
    } else {
      throw new Error('Docker options service unavailable');
    }
  }
};

export const generateDockerfile = async (platform, versionConfig, projectContext = {}) => {
  try {
    const response = await orchestratorApi.post('/generate-dockerfile', {
      platform,
      file_type: 'Dockerfile',
      version_config: versionConfig,
      project_context: projectContext
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Dockerfile generation failed');
    } else {
      throw new Error('Dockerfile generation service unavailable');
    }
  }
};

export const getVersionOptions = async (platform) => {
  try {
    const response = await orchestratorApi.get(`/version-options/${platform.toLowerCase()}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get version options');
    } else {
      throw new Error('Version options service unavailable');
    }
  }
};

export const getBaseImages = async (platform) => {
  try {
    const response = await orchestratorApi.get(`/base-images/${platform.toLowerCase()}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get base images');
    } else {
      throw new Error('Base images service unavailable');
    }
  }
};

export default api;
