# Project Detector - Intelligent Platform Detection System

> **Automated detection of programming languages, frameworks, and build tools for streamlined deployments**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

Project Detector is an intelligent API service that automatically analyzes source code repositories to detect:

- **Programming Languages** (Python, Node.js, Java, Go, Ruby, PHP, and more)
- **Frameworks** (React, Django, Spring Boot, Express, Laravel, etc.)
- **Build Tools** (Maven, Gradle, npm, yarn, pip, cargo, etc.)
- **Build Requirements** (Whether compilation/build step is needed)
- **Recommended Commands** (Install and build commands)

Perfect for **CI/CD pipelines**, **deployment automation**, and **project analysis**.

---

## 🌟 Key Features

✅ **Dual Input Methods**: Scan GitHub URLs or upload ZIP files  
✅ **Confidence Scoring**: Get reliability scores for each detection  
✅ **Multi-Language Support**: Handles monorepos with multiple languages  
✅ **Smart Recommendations**: Returns optimal build and install commands  
✅ **Zero Configuration**: Works out of the box  
✅ **Modern Web UI**: Beautiful vanilla JavaScript frontend included  
✅ **REST API**: Easy integration with existing tools  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd deploy_pilot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Backend

```bash
# Start the FastAPI server
python main.py

# Server will start at http://localhost:8000
```

### Running the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start the frontend server
python3 serve.py

# Frontend will be available at http://localhost:3000
```

---

## 🖥️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Port 3000)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Vanilla JavaScript + HTML + CSS                │   │
│  │  - GitHub URL Input                             │   │
│  │  - ZIP File Upload                              │   │
│  │  - Confidence Threshold Slider                  │   │
│  │  - Real-time Results Display                    │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST API
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend API (Port 8000)              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FastAPI + Python                               │   │
│  │  - Repository Cloning/Extraction                │   │
│  │  - Multi-Platform Detection Engine              │   │
│  │  - Confidence Scoring Algorithm                 │   │
│  │  - Build Command Generation                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
deploy_pilot/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── API_DOCUMENTATION.md       # Detailed API documentation
│
├── routes/                    # API route handlers
│   ├── __init__.py
│   └── scan.py               # Scan endpoint logic
│
├── services/                  # Business logic
│   ├── __init__.py
│   ├── github_service.py     # GitHub cloning
│   ├── zip_service.py        # ZIP file handling
│   └── detector_service.py   # Detection engine
│
├── models/                    # Data models
│   ├── __init__.py
│   └── detection.py          # Detection response models
│
├── detectors/                 # Platform-specific detectors
│   ├── __init__.py
│   ├── python_detector.py
│   ├── nodejs_detector.py
│   ├── java_detector.py
│   └── ... (more detectors)
│
└── frontend/                  # Web interface
    ├── public/
    │   ├── index.html        # Main page
    │   ├── styles.css        # Styling
    │   └── app.js            # Frontend logic
    ├── serve.py              # Frontend server with API proxy
    ├── package.json          # Minimal config (no dependencies!)
    └── README.md             # Frontend documentation
```

---

## 🔌 API Usage

### Health Check

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "project-detector"
}
```

### Scan GitHub Repository

```bash
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/facebook/react" \
  -F "min_confidence=0.5"
```

### Scan ZIP File

```bash
curl -X POST http://localhost:8000/api/scan \
  -F "zip_file=@/path/to/project.zip" \
  -F "min_confidence=0.45"
```

### Response Format

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
      "detected_files": ["package.json", "yarn.lock"]
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
    "detected_files": ["package.json", "yarn.lock"]
  },
  "min_confidence_threshold": 0.45
}
```

---

## 🎯 Confidence Scoring

The system uses a confidence scoring system to indicate detection reliability:

| Score Range | Level | Description | Recommended Use |
|------------|-------|-------------|-----------------|
| **≥ 0.80** | Very High | Fully reliable | ✅ Full automation |
| **0.65-0.79** | High | Safe for most cases | ✅ Automation with logging |
| **0.45-0.64** | Moderate | Proceed with caution | ⚠️ Manual verification |
| **< 0.45** | Low | Unreliable | ❌ Not recommended |

---

## 📊 Supported Technologies

### Languages
Python • Node.js • Java • Ruby • PHP • Go • Rust • C/C++ • C#/.NET • Swift • Kotlin • Scala • TypeScript

### Frameworks
**Python:** Django, Flask, FastAPI, Pyramid  
**Node.js:** Express, React, Vue, Angular, Next.js  
**Java:** Spring Boot, Quarkus, Micronaut  
**Ruby:** Rails, Sinatra  
**PHP:** Laravel, Symfony, WordPress  
**Go:** Gin, Echo, Fiber  

### Build Tools
npm • yarn • pnpm • pip • poetry • Maven • Gradle • cargo • composer • bundler • go mod • dotnet

---

## 🖼️ Frontend Features

The included web interface provides:

- **🎨 Modern UI**: Beautiful gradient design with smooth animations
- **📱 Responsive**: Works on desktop, tablet, and mobile
- **🔄 Real-time**: Live API health monitoring
- **📤 Dual Input**: GitHub URL or drag-and-drop ZIP upload
- **🎚️ Adjustable Confidence**: Slider to set detection threshold
- **📊 Rich Results**: Detailed detection information with confidence badges
- **⚡ Zero Dependencies**: Pure HTML/CSS/JavaScript - no build tools!

**Access the frontend at:** http://localhost:3000

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t project-detector .

# Run the container
docker run -p 8000:8000 project-detector
```

### Docker Compose

```bash
# Start both backend and frontend
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Testing

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test with Sample Repositories

```bash
# Test with React
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/facebook/react"

# Test with Django
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/django/django"

# Test with Spring Boot
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/spring-projects/spring-boot"
```

---

## 🔒 Security

- ✅ No persistent data storage
- ✅ Temporary files cleaned automatically
- ✅ Static analysis only (no code execution)
- ✅ ZIP file validation before extraction
- ✅ Public repositories only (no authentication required)

**Production Recommendations:**
- Use HTTPS
- Implement rate limiting
- Add API authentication
- Configure CORS properly
- Regular security updates

---

## 📈 Performance

**Typical Response Times:**
- Small repos (<100 files): 1-3 seconds
- Medium repos (100-1000 files): 3-10 seconds
- Large repos (>1000 files): 10-30 seconds

**Optimization Tips:**
- Use higher confidence thresholds
- Upload ZIP files instead of GitHub URLs (faster)
- Cache results for frequently scanned repos

---

## 🛠️ Development

### Adding New Detectors

1. Create a new detector in `detectors/`:
```python
# detectors/mylang_detector.py
from models.detection import Detection

def detect_mylang(files: list) -> Detection:
    # Your detection logic
    pass
```

2. Register in `services/detector_service.py`
3. Add tests
4. Update documentation

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Frontend README](frontend/README.md)** - Frontend setup and usage
- **[Interactive Docs](http://localhost:8000/docs)** - Swagger UI (when server is running)

---

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] Authentication & API keys
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Private repository support (with GitHub tokens)
- [ ] Batch scanning

### v1.2
- [ ] Webhooks for async processing
- [ ] Historical scan results
- [ ] Custom detection rules
- [ ] More language support

### v2.0
- [ ] ML-based detection improvements
- [ ] Security vulnerability scanning
- [ ] Dependency analysis
- [ ] Cost estimation for cloud deployments

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend shows "API Offline"
- Ensure backend is running on port 8000
- Check `BACKEND_URL` in `frontend/serve.py`
- Verify no firewall blocking

### Low confidence scores
- Repository may use non-standard structure
- Try lowering `min_confidence` threshold
- Check if standard config files are present

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for more troubleshooting tips.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Project Detector Team**

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- All the open-source projects that inspired this tool
- Contributors and testers

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@projectdetector.example.com

---

**Made with ❤️ and Python**

---

### Quick Links

- [API Documentation](API_DOCUMENTATION.md)
- [Frontend Guide](frontend/README.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
