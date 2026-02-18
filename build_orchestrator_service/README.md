# Build Orchestrator Service

A production-grade microservice for build validation, configuration file generation, and Dockerfile orchestration.

## 🎯 Overview

The Build Orchestrator Service is a **stateless, isolated microservice** designed to work alongside the Detection Service. It provides intelligent validation, suggestion generation, and template rendering for software projects across multiple platforms.

## 🏛 Architecture Principles

### Microservice Isolation

- **Damage Containment**: Service runs in isolated container with restricted permissions
- **Failure Domain Isolation**: Crashes in this service do NOT affect Detection Service
- **Precise Rollback**: Can be rolled back independently without affecting other services
- **Independent Scaling**: Scale based on orchestration demand, not detection demand

### Security & Safety

- ✅ **Read-only operations** - Never modifies project files
- ✅ **No code execution** - Never runs `mvn`, `npm`, `go`, `dotnet`, or any build commands
- ✅ **No Docker operations** - Never executes `docker build` or container commands
- ✅ **Path traversal protection** - Validated via Pydantic models
- ✅ **Stateless design** - No persistent state between requests
- ✅ **Sandbox-only writes** - Only writes to isolated sandbox directory

## 🚀 Features

### Platform Support

All features are implemented for **ALL** supported platforms:

- ☕ **Java** - Maven (`pom.xml`), Gradle (`build.gradle`)
- 🟨 **Node.js** - npm/yarn/pnpm (`package.json`)
- 🐍 **Python** - pip (`requirements.txt`), Poetry (`pyproject.toml`)
- 🟪 **.NET** - dotnet (`*.csproj`)
- 🐹 **Go** - Go modules (`go.mod`)

### Core Capabilities

1. **Validation Engine**
   - Detects missing required build files
   - Identifies optional files for better project structure
   - Platform-specific validation rules
   - Severity classification (Critical, Warning, Info)

2. **Suggestion Engine**
   - Intelligent corrective action recommendations
   - Automated vs manual action classification
   - Priority-based suggestion ordering
   - Context-aware suggestions

3. **Template Generation**
   - Jinja2-based template rendering
   - Version-aware configuration
   - Dynamic dependency injection
   - Framework-specific customization

4. **Dockerfile Management**
   - Dockerfile detection and validation
   - Multi-stage build generation
   - Platform-optimized base images
   - Production-ready configurations

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)

### Local Development

```bash
# Clone repository
cd build_orchestrator_service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python -m build_orchestrator_service.main
```

The service will start on `http://localhost:8001`

### Docker Deployment

```bash
# Build the Docker image
docker build -t build-orchestrator:1.0.0 .

# Run the container
docker run -p 8001:8001 build-orchestrator:1.0.0
```

## 🔌 API Endpoints

### Validation

#### `POST /api/validate`

Validate a project based on detection results.

**Request:**
```json
{
  "detection_result": {
    "primary_language": "Java",
    "framework": "Spring Boot",
    "build_tool": "Maven",
    "confidence_score": 0.95,
    "detected_files": ["src/", "target/"]
  },
  "project_path": "projects/myapp"
}
```

**Response:**
```json
{
  "status": "missing_files",
  "platform": "Java",
  "missing_files": [
    {
      "file_name": "pom.xml",
      "file_type": "build_config",
      "severity": "critical",
      "description": "Java build configuration file (Maven or Gradle)",
      "can_generate": true
    }
  ],
  "suggestions": [
    {
      "action": "Generate Maven pom.xml",
      "description": "Create a minimal Maven configuration file",
      "automated": true,
      "priority": 1
    }
  ],
  "available_actions": ["generate_files", "dockerize"],
  "version_options": {
    "java_version": [
      {"version": "21", "recommended": true},
      {"version": "17", "recommended": true}
    ]
  }
}
```

#### `POST /api/generate-template`

Generate a configuration file from template.

**Request:**
```json
{
  "platform": "Java",
  "file_type": "pom.xml",
  "version_config": {
    "java_version": "17",
    "packaging_type": "jar",
    "group_id": "com.example",
    "artifact_id": "myapp"
  }
}
```

**Response:**
```json
{
  "success": true,
  "file_type": "pom.xml",
  "content": "<?xml version=\"1.0\"...>",
  "file_name": "pom.xml",
  "metadata": {
    "platform": "Java",
    "runtime_version": "17"
  }
}
```

### Docker Management

#### `POST /api/docker-options`

Get Dockerfile options for a project.

**Request:**
```json
{
  "project_path": "projects/myapp",
  "platform": "Node.js",
  "version_config": {
    "node_version": "18"
  }
}
```

**Response:**
```json
{
  "dockerfile_status": "missing",
  "options": [
    {
      "option": "generate_standard",
      "description": "Generate a standard Dockerfile for Node.js",
      "automated": true
    },
    {
      "option": "generate_multistage",
      "description": "Generate optimized multi-stage Dockerfile",
      "automated": true
    }
  ],
  "can_generate": true,
  "generation_config": {
    "base_images": [
      {"version": "20", "image": "node:20-alpine"},
      {"version": "18", "image": "node:18-alpine"}
    ],
    "default_port": 3000
  }
}
```

#### `POST /api/generate-dockerfile`

Generate a Dockerfile.

**Request:**
```json
{
  "platform": "Python",
  "file_type": "Dockerfile",
  "version_config": {
    "python_version": "3.11",
    "expose_port": 8000
  },
  "project_context": {
    "framework": "FastAPI",
    "has_requirements": true
  }
}
```

### Utility Endpoints

- `GET /api/version-options/{platform}` - Get available versions for a platform
- `GET /api/base-images/{platform}` - Get Docker base images for a platform
- `GET /api/health` - Health check endpoint
- `GET /` - Service information
- `GET /docs` - Interactive API documentation (Swagger UI)

## 🔧 Configuration

### Environment Variables

```bash
# Service Configuration
PORT=8001
SERVICE_NAME=build-orchestrator

# Logging
LOG_LEVEL=INFO

# CORS (for production, restrict origins)
ALLOWED_ORIGINS=*
```

## 🏗 Project Structure

```
build_orchestrator_service/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image definition
├── .dockerignore               # Docker build exclusions
├── README.md                   # This file
├── API_EXAMPLES.md             # Detailed API examples
│
├── models/                     # Pydantic models
│   ├── __init__.py
│   ├── request_models.py       # Request schemas
│   └── response_models.py      # Response schemas
│
├── routes/                     # FastAPI route handlers
│   ├── __init__.py
│   ├── validation.py           # Validation endpoints
│   └── docker.py              # Docker endpoints
│
├── services/                   # Business logic
│   ├── __init__.py
│   ├── validator.py           # Platform validation
│   ├── suggestion_engine.py   # Suggestion generation
│   ├── template_engine.py     # Jinja2 template rendering
│   └── docker_generator.py    # Dockerfile generation
│
└── templates/                  # Jinja2 templates
    ├── java/
    │   ├── pom.xml.j2
    │   ├── build.gradle.j2
    │   └── Dockerfile.j2
    ├── nodejs/
    │   ├── package.json.j2
    │   └── Dockerfile.j2
    ├── python/
    │   ├── requirements.txt.j2
    │   ├── pyproject.toml.j2
    │   └── Dockerfile.j2
    ├── dotnet/
    │   ├── project.csproj.j2
    │   └── Dockerfile.j2
    └── go/
        ├── go.mod.j2
        └── Dockerfile.j2
```

## 🔐 Security Considerations

### What This Service DOES NOT Do

- ❌ Execute build commands (`mvn`, `npm`, `gradle`, etc.)
- ❌ Run Docker builds or container operations
- ❌ Modify project files directly
- ❌ Execute arbitrary code or scripts
- ❌ Deploy to production environments
- ❌ Access network resources (except Detection Service API)

### What This Service DOES

- ✅ Read project files for validation (read-only)
- ✅ Generate configuration file content (returns as string)
- ✅ Provide intelligent suggestions
- ✅ Render templates with user configuration
- ✅ Validate Dockerfile existence and syntax

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=build_orchestrator_service tests/

# Test specific platform
pytest tests/test_validator.py -k test_java_validation
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8001/api/health
```

### Metrics

```bash
curl http://localhost:8001/metrics
```

## 🔄 Integration with Detection Service

The Build Orchestrator Service is designed to receive `DetectionResult` from the Detection Service via REST API.

**Typical Flow:**

1. User submits project to Detection Service
2. Detection Service analyzes project → returns `DetectionResult`
3. Frontend calls Build Orchestrator with `DetectionResult`
4. Build Orchestrator validates and returns suggestions
5. User selects action (generate files, dockerize, etc.)
6. Build Orchestrator returns generated content
7. User downloads or applies generated files

**Service Independence:**

- Services communicate ONLY via REST API
- No shared database or state
- No direct code dependencies
- Each service can be deployed/scaled independently

## 🚢 Deployment

### Docker Compose (Multi-Service)

See `docker-compose.yml` in the root directory for orchestrating both services.

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: build-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: build-orchestrator
  template:
    metadata:
      labels:
        app: build-orchestrator
    spec:
      containers:
      - name: build-orchestrator
        image: build-orchestrator:1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: PORT
          value: "8001"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```

## 🛣 Roadmap

Future enhancements (modular design allows easy extension):

- 🔍 CI/CD pipeline generation (GitHub Actions, GitLab CI)
- 🔒 Security scanning integration (SBOM, vulnerability scanning)
- 📦 Dependency version recommendations
- 🎯 Multi-language project support (polyglot projects)
- 🔧 Custom template support (user-provided templates)

## 📝 License

See main project LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All platforms (Java, Node.js, Python, .NET, Go) remain supported
2. Security principles are maintained (no code execution)
3. Tests are added for new features
4. Documentation is updated

## 📧 Support

For issues or questions, please open an issue in the main repository.

---

**Built with ❤️ for safe, isolated build orchestration**
