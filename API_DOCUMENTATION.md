# Project Detector API - Complete Documentation

> **FastAPI-based REST API for Intelligent Project Platform Detection**

Version: 1.0.0  
Base URL: `http://localhost:8000`

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Confidence Scoring](#confidence-scoring)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [SDKs & Clients](#sdks--clients)

---

## 🌟 Overview

The Project Detector API automatically analyzes source code repositories to detect:

- **Programming Languages** (Python, Node.js, Java, Go, Ruby, PHP, etc.)
- **Frameworks** (React, Django, Spring Boot, Express, etc.)
- **Build Tools** (Maven, Gradle, npm, yarn, pip, etc.)
- **Package Managers** (npm, pip, composer, bundler, etc.)
- **CI/CD Tools** (GitHub Actions, Jenkins, GitLab CI, etc.)
- **Containerization** (Docker, Kubernetes, etc.)

### Key Features

✅ **Dual Input Methods**: GitHub URL or ZIP file upload  
✅ **Confidence Scoring**: Reliability indicators for each detection  
✅ **Multi-Detection**: Detects multiple languages/frameworks in monorepos  
✅ **Smart Build Commands**: Returns recommended build/install commands  
✅ **File Evidence**: Shows which files led to each detection  

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd deploy_pilot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### First API Call

```bash
# Health check
curl http://localhost:8000/api/health

# Scan a GitHub repository
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/facebook/react" \
  -F "min_confidence=0.5"
```

---

## 🔐 Authentication

**Current Version**: No authentication required (MVP)

**Future Versions**: Will support API keys via header:
```
Authorization: Bearer YOUR_API_KEY
```

---

## 📡 Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Project Detection API",
  "version": "1.0.0",
  "endpoints": {
    "scan": "/api/scan",
    "health": "/api/health"
  }
}
```

---

### 2. Health Check

**GET** `/api/health`

Check if the API service is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "project-detector"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### 3. Scan Repository

**POST** `/api/scan`

Analyze a repository to detect platforms, languages, and build tools.

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `github_url` | string | Conditional* | GitHub repository URL (e.g., `https://github.com/user/repo`) |
| `zip_file` | file | Conditional* | ZIP archive of the project |
| `min_confidence` | float | Optional | Minimum confidence threshold (0.0-1.0, default: 0.45) |

*Either `github_url` OR `zip_file` must be provided, not both.

#### Confidence Threshold Guidelines

| Range | Level | Use Case |
|-------|-------|----------|
| **0.0 - 0.44** | Low/Unreliable | Not recommended for automation |
| **0.45 - 0.64** | Moderate | Use with caution, manual verification recommended |
| **0.65 - 0.79** | High | Safe for most automation scenarios |
| **0.80 - 1.0** | Very High | Fully automated deployment ready |

#### Response Format

```json
{
  "detections": [
    {
      "primary_language": "Node.js",
      "framework": "React",
      "build_tool": "yarn",
      "build_required": true,
      "build_command": "yarn build",
      "install_command": "yarn install",
      "confidence_score": 0.75,
      "confidence_level": "high",
      "detected_files": [
        "package.json",
        "yarn.lock",
        "src/App.jsx"
      ]
    },
    {
      "primary_language": "Python",
      "framework": "FastAPI",
      "build_tool": "pip",
      "build_required": false,
      "build_command": null,
      "install_command": "pip install -r requirements.txt",
      "confidence_score": 0.68,
      "confidence_level": "high",
      "detected_files": [
        "requirements.txt",
        "main.py"
      ]
    }
  ],
  "primary": {
    "primary_language": "Node.js",
    "framework": "React",
    "build_tool": "yarn",
    "build_required": true,
    "build_command": "yarn build",
    "install_command": "yarn install",
    "confidence_score": 0.75,
    "confidence_level": "high",
    "detected_files": [
      "package.json",
      "yarn.lock",
      "src/App.jsx"
    ]
  },
  "min_confidence_threshold": 0.45
}
```

#### Response Fields

**Detection Object:**

| Field | Type | Description |
|-------|------|-------------|
| `primary_language` | string | Main programming language detected |
| `framework` | string\|null | Web/application framework (if detected) |
| `build_tool` | string\|null | Build tool or package manager |
| `build_required` | boolean | Whether a build step is needed |
| `build_command` | string\|null | Recommended build command |
| `install_command` | string\|null | Recommended install command |
| `confidence_score` | float | Confidence score (0.0-1.0) |
| `confidence_level` | string | Human-readable level: `unreliable`, `moderate`, `high`, `very_high` |
| `detected_files` | array | Files that led to this detection |

**Top-Level Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `detections` | array | All detections above the confidence threshold |
| `primary` | object | The highest-confidence detection |
| `min_confidence_threshold` | float | The threshold used for filtering |

#### Status Codes

- `200 OK`: Scan successful
- `400 Bad Request`: Invalid input (missing URL/file, invalid confidence)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error during processing

---

## 📤 Request/Response Formats

### Example 1: GitHub URL Scan

**Request:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/django/django" \
  -F "min_confidence=0.5"
```

**Response:**
```json
{
  "detections": [
    {
      "primary_language": "Python",
      "framework": "Django",
      "build_tool": "pip",
      "build_required": false,
      "build_command": null,
      "install_command": "pip install -r requirements.txt",
      "confidence_score": 0.85,
      "confidence_level": "very_high",
      "detected_files": [
        "setup.py",
        "django/__init__.py",
        "requirements.txt"
      ]
    }
  ],
  "primary": {
    "primary_language": "Python",
    "framework": "Django",
    "build_tool": "pip",
    "build_required": false,
    "build_command": null,
    "install_command": "pip install -r requirements.txt",
    "confidence_score": 0.85,
    "confidence_level": "very_high",
    "detected_files": [
      "setup.py",
      "django/__init__.py",
      "requirements.txt"
    ]
  },
  "min_confidence_threshold": 0.5
}
```

### Example 2: ZIP File Upload

**Request:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "zip_file=@/path/to/project.zip" \
  -F "min_confidence=0.45"
```

**Response:** Same format as Example 1

### Example 3: Error Response

**Request:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "min_confidence=0.5"
```

**Response (400 Bad Request):**
```json
{
  "detail": "Either github_url or zip_file must be provided"
}
```

---

## 🎯 Confidence Scoring

The API uses a sophisticated confidence scoring system based on:

1. **File Presence**: Specific configuration files (e.g., `package.json`, `pom.xml`)
2. **File Content**: Code patterns and imports
3. **File Patterns**: Multiple related files
4. **Ecosystem Indicators**: Lock files, specific directory structures

### Confidence Levels

```
┌─────────────────────────────────────────────┐
│ 1.0  ████████████████████  Very High (≥0.80)│
│ 0.8  ████████████████      High (0.65-0.79) │
│ 0.6  ██████████            Moderate (0.45-0.64)│
│ 0.4  ████                  Low (<0.45)       │
│ 0.0                                          │
└─────────────────────────────────────────────┘
```

### Using Confidence Scores

**Production Automation:**
```python
if detection["confidence_score"] >= 0.80:
    # Safe to automate deployment
    deploy(detection["build_command"])
elif detection["confidence_score"] >= 0.65:
    # Log and automate with monitoring
    log_deployment(detection)
    deploy(detection["build_command"])
else:
    # Manual review required
    notify_human(detection)
```

---

## ❌ Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 400 | `Either github_url or zip_file must be provided` | Provide exactly one input method |
| 400 | `min_confidence must be between 0.0 and 1.0` | Use valid confidence value |
| 400 | `Invalid GitHub URL format` | Use format: `https://github.com/user/repo` |
| 400 | `Invalid ZIP file` | Ensure file is a valid ZIP archive |
| 404 | `GitHub repository not found` | Check URL, ensure repo is public |
| 422 | `Validation error` | Check request format and types |
| 500 | `Internal server error` | Check server logs, contact support |

---

## ⏱️ Rate Limiting

**Current Version**: No rate limiting (MVP)

**Future Versions**: 
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## 💻 Examples

### Python Example

```python
import requests

# Scan a GitHub repository
response = requests.post(
    "http://localhost:8000/api/scan",
    data={
        "github_url": "https://github.com/pallets/flask",
        "min_confidence": 0.5
    }
)

result = response.json()
primary = result["primary"]

print(f"Language: {primary['primary_language']}")
print(f"Framework: {primary['framework']}")
print(f"Build Tool: {primary['build_tool']}")
print(f"Confidence: {primary['confidence_score']:.2%}")

if primary["build_required"]:
    print(f"Build Command: {primary['build_command']}")
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('github_url', 'https://github.com/expressjs/express');
formData.append('min_confidence', '0.5');

fetch('http://localhost:8000/api/scan', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    const primary = data.primary;
    console.log(`Language: ${primary.primary_language}`);
    console.log(`Framework: ${primary.framework}`);
    console.log(`Confidence: ${(primary.confidence_score * 100).toFixed(1)}%`);
});
```

### cURL Examples

**Basic Scan:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/spring-projects/spring-boot"
```

**With Custom Confidence:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/rails/rails" \
  -F "min_confidence=0.7"
```

**Upload ZIP File:**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "zip_file=@myproject.zip" \
  -F "min_confidence=0.45"
```

---

## 🔌 SDKs & Clients

### Official Clients

**Coming Soon:**
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

### Community Clients

We welcome community-contributed clients! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🧪 Testing

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Repositories

Use these public repositories for testing:

| Repository | Expected Detection |
|------------|-------------------|
| `facebook/react` | Node.js, yarn |
| `django/django` | Python, Django |
| `spring-projects/spring-boot` | Java, Maven/Gradle |
| `rails/rails` | Ruby, Bundler |
| `laravel/laravel` | PHP, Composer |
| `golang/go` | Go |

---

## 📊 Detection Coverage

### Supported Languages

- ✅ Python
- ✅ Node.js / JavaScript
- ✅ Java
- ✅ Ruby
- ✅ PHP
- ✅ Go
- ✅ Rust
- ✅ C/C++
- ✅ C#/.NET
- ✅ Swift
- ✅ Kotlin
- ✅ Scala
- ✅ TypeScript

### Supported Frameworks

**Python:** Django, Flask, FastAPI, Pyramid  
**Node.js:** Express, React, Vue, Angular, Next.js  
**Java:** Spring Boot, Quarkus, Micronaut  
**Ruby:** Rails, Sinatra  
**PHP:** Laravel, Symfony, WordPress  
**Go:** Gin, Echo, Fiber  

### Supported Build Tools

npm, yarn, pnpm, pip, poetry, Maven, Gradle, cargo, composer, bundler, go mod, dotnet, swift package manager

---

## 🔒 Security & Privacy

- 🔐 No data is stored permanently
- 🗑️ Temporary files are cleaned up after processing
- 🚫 No code execution - static analysis only
- ✅ ZIP files are validated before extraction
- ⚠️ GitHub tokens are not required (public repos only)

**Production Recommendations:**
- Use HTTPS in production
- Implement rate limiting
- Add authentication
- Scan for vulnerabilities regularly
- Keep dependencies updated

---

## 📈 Performance

**Typical Response Times:**
- Small repos (<100 files): 1-3 seconds
- Medium repos (100-1000 files): 3-10 seconds
- Large repos (>1000 files): 10-30 seconds

**Optimization Tips:**
- Use higher `min_confidence` to reduce processing
- Cache results for frequently scanned repos
- Use ZIP uploads for faster processing (no GitHub API calls)

---

## 🐛 Troubleshooting

### "GitHub repository not found"
- Ensure the repository is public
- Check the URL format: `https://github.com/owner/repo`
- Verify repository exists

### "Invalid ZIP file"
- Ensure file is a valid ZIP archive
- Check file is not corrupted
- Verify file contains project files at root or in single directory

### Low Confidence Scores
- Repository may use uncommon structure
- Try lowering `min_confidence` threshold
- Check if repository contains standard config files

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This file + README.md
- **API Explorer**: http://localhost:8000/docs

---

## 🗺️ Roadmap

**v1.1:**
- [ ] Authentication & API keys
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Private repository support

**v1.2:**
- [ ] Webhooks for async processing
- [ ] Batch scanning
- [ ] Historical scan results
- [ ] Custom detection rules

**v2.0:**
- [ ] ML-based detection improvements
- [ ] Security vulnerability scanning
- [ ] Dependency analysis
- [ ] Cost estimation

---

## 📄 License

See LICENSE file in the project root.

---

**API Version:** 1.0.0  
**Last Updated:** 2026-02-17  
**Maintained by:** Project Detector Team
