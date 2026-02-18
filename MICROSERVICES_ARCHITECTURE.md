# Microservices Architecture Documentation

## 🏛 Architecture Overview

This platform is built as a **true microservices architecture** with complete service isolation and independent deployability.

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (Nginx)                       │
│                         Port 80 (Optional)                       │
└────────┬────────────────────────────────────────────┬───────────┘
         │                                             │
         │                                             │
         ▼                                             ▼
┌────────────────────────┐              ┌──────────────────────────┐
│  Detection Service     │              │ Build Orchestrator       │
│  Port 8000             │              │ Service                  │
│                        │              │ Port 8001                │
│  Responsibilities:     │              │                          │
│  • Stack Detection     │◄─────────────┤ Responsibilities:        │
│  • File Scanning       │   REST API   │ • Validation             │
│  • Confidence Scoring  │              │ • Template Generation    │
│  • Platform ID         │              │ • Dockerfile Generation  │
│                        │              │ • Suggestions            │
└────────────────────────┘              └──────────────────────────┘
         │                                             │
         │                                             │
         ▼                                             ▼
    Read-only                                     Read-only
    File Access                                   File Access
```

## 🎯 Service Responsibilities

### Detection Service (Port 8000)

**Single Responsibility:** Detect project platform and technology stack

- ✅ Scans project files
- ✅ Identifies programming language
- ✅ Detects framework
- ✅ Identifies build tool
- ✅ Returns DetectionResult JSON
- ❌ NO validation logic
- ❌ NO file generation
- ❌ NO build orchestration

**API Contract:**
```json
POST /api/scan
Response: DetectionResult
{
  "primary_language": "Java",
  "framework": "Spring Boot",
  "build_tool": "Maven",
  "confidence_score": 0.95,
  "detected_files": [...]
}
```

### Build Orchestrator Service (Port 8001)

**Single Responsibility:** Validate, suggest, and generate build configurations

- ✅ Validates required files
- ✅ Generates suggestions
- ✅ Renders templates (pom.xml, package.json, etc.)
- ✅ Generates Dockerfiles
- ✅ Version configuration
- ❌ NO detection logic
- ❌ NO build execution
- ❌ NO Docker build commands

**API Contract:**
```json
POST /api/validate
Input: DetectionResult + project_path
Response: ValidationResponse
{
  "status": "missing_files",
  "missing_files": [...],
  "suggestions": [...],
  "version_options": {...}
}
```

## 🔐 Damage Containment Strategy

### Isolation Mechanisms

1. **Process Isolation**
   - Each service runs in separate container
   - Separate process spaces
   - Independent memory allocation
   - Crash in one service doesn't affect others

2. **Network Isolation**
   - Services communicate via HTTP REST API only
   - No shared memory or files
   - Network segmentation via Docker network
   - Can add authentication between services

3. **Failure Domain Isolation**
   - Detection service failure → Orchestrator continues to work with cached results
   - Orchestrator service failure → Detection continues to work
   - Independent restart/rollback possible

4. **Resource Isolation**
   - Separate CPU/memory limits
   - Independent scaling
   - No resource contention

### Security Boundaries

```
┌──────────────────────────────────────────────────────────────┐
│                     Security Boundary 1                       │
│  Detection Service Container                                  │
│  • Read-only file system (except /tmp)                       │
│  • Non-root user (detector:1000)                             │
│  • No network egress (except to orchestrator if needed)      │
│  • Limited syscalls                                           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     Security Boundary 2                       │
│  Build Orchestrator Container                                 │
│  • Read-only file system (except /tmp)                       │
│  • Non-root user (orchestrator:1000)                         │
│  • No build command execution                                 │
│  • No Docker socket access                                    │
│  • Path traversal protection                                  │
└──────────────────────────────────────────────────────────────┘
```

## 🔄 Communication Flow

### Typical User Flow

```
1. User → API Gateway → Detection Service
   POST /api/scan
   Input: GitHub URL or ZIP file

2. Detection Service → User
   Response: DetectionResult JSON

3. User → API Gateway → Build Orchestrator
   POST /api/validate
   Input: DetectionResult + project_path

4. Build Orchestrator → User
   Response: ValidationResponse with suggestions

5. User → API Gateway → Build Orchestrator
   POST /api/generate-template
   Input: Platform + FileType + VersionConfig

6. Build Orchestrator → User
   Response: Generated file content (string)
```

### Service-to-Service Communication

**Current:** Services are independent (no direct communication)

**Future (if needed):**
```python
# Build Orchestrator calling Detection Service (optional)
async def get_detection(project_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://detection-service:8000/api/scan",
            json={"project_path": project_path}
        )
        return response.json()
```

## 📊 Scaling Strategy

### Independent Scaling

Each service can scale independently based on demand:

```yaml
# Scale Detection Service (high scan volume)
docker-compose up -d --scale detection-service=5

# Scale Build Orchestrator (high generation volume)
docker-compose up -d --scale build-orchestrator=3
```

### Load Balancing

```
         ┌─────────────────┐
         │  Load Balancer  │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌─────▼───┐
    │ Detect  │      │ Detect  │
    │ Pod 1   │      │ Pod 2   │
    └─────────┘      └─────────┘
```

## 🚀 Deployment Options

### Option 1: Docker Compose (Development/Small Production)

```bash
docker-compose up -d
```

- Both services start together
- Shared network
- Health checks
- Automatic restarts

### Option 2: Kubernetes (Production)

```yaml
# detection-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: detection-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: detection
  template:
    spec:
      containers:
      - name: detection
        image: detection-service:1.0.0
        ports:
        - containerPort: 8000
---
# orchestrator-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: build-orchestrator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: orchestrator
  template:
    spec:
      containers:
      - name: orchestrator
        image: build-orchestrator:1.0.0
        ports:
        - containerPort: 8001
```

### Option 3: Separate Deployments

Each service can be deployed completely independently:

```bash
# Deploy Detection Service only
cd /detection
docker build -t detection:1.0.0 .
docker run -p 8000:8000 detection:1.0.0

# Deploy Build Orchestrator only
cd /build_orchestrator_service
docker build -t orchestrator:1.0.0 .
docker run -p 8001:8001 orchestrator:1.0.0
```

## 🔧 Configuration Management

### Environment Variables

**Detection Service:**
```bash
SERVICE_NAME=detection-service
PORT=8000
LOG_LEVEL=INFO
MIN_CONFIDENCE=0.45
```

**Build Orchestrator:**
```bash
SERVICE_NAME=build-orchestrator
PORT=8001
LOG_LEVEL=INFO
DETECTION_SERVICE_URL=http://detection-service:8000
```

## 📈 Monitoring & Observability

### Health Checks

```bash
# Detection Service
curl http://localhost:8000/api/health

# Build Orchestrator
curl http://localhost:8001/api/health

# Aggregate (via Gateway)
curl http://localhost/api/health
```

### Metrics

Each service exposes metrics:

```bash
curl http://localhost:8000/metrics  # Detection
curl http://localhost:8001/metrics  # Orchestrator
```

## 🛡 Rollback Strategy

### Independent Rollback

```bash
# Rollback only Build Orchestrator (Detection unaffected)
docker-compose stop build-orchestrator
docker pull build-orchestrator:1.0.0-previous
docker-compose up -d build-orchestrator

# Detection Service continues serving requests
```

### Version Pinning

```yaml
services:
  detection-service:
    image: detection-service:1.0.0  # Stable version
  
  build-orchestrator:
    image: build-orchestrator:1.1.0  # New version (testing)
```

## 🔮 Future Extensions

The modular architecture allows easy addition of new services:

### Potential Future Services

1. **CI/CD Generator Service** (Port 8002)
   - Generates GitHub Actions workflows
   - GitLab CI configurations
   - Jenkins pipelines

2. **Security Scanner Service** (Port 8003)
   - SBOM generation
   - Vulnerability scanning
   - License compliance

3. **Deployment Service** (Port 8004)
   - Kubernetes manifests
   - Helm charts
   - Terraform configs

Each new service follows the same pattern:
- Independent container
- REST API communication
- Read-only operations
- No code execution

## 📝 Best Practices

1. **Never share databases** between services
2. **Use API versioning** (/api/v1/validate)
3. **Implement circuit breakers** for service calls
4. **Use async communication** where possible
5. **Monitor service health** continuously
6. **Log correlation IDs** across services
7. **Document API contracts** (OpenAPI/Swagger)
8. **Version Docker images** properly

## 🎓 Key Takeaways

✅ **Isolation**: Each service fails independently  
✅ **Scalability**: Scale services based on their specific load  
✅ **Maintainability**: Update one service without affecting others  
✅ **Security**: Damage contained within service boundary  
✅ **Deployability**: Deploy, rollback, version independently  

---

**This is a production-ready microservices architecture designed for safety, scalability, and maintainability.**
