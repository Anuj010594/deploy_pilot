# Quick Start Guide - Microservice Platform

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Docker & Docker Compose installed
- Ports 8000, 8001, and 80 available

### Option 1: Start Everything (Recommended)

```bash
# Start both services with API Gateway
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services Running:**
- Detection Service: `http://localhost:8000`
- Build Orchestrator: `http://localhost:8001`
- API Gateway: `http://localhost:80`

### Option 2: Start Services Individually

**Start Detection Service Only:**
```bash
cd /path/to/project
docker build -t detection-service:1.0.0 .
docker run -p 8000:8000 detection-service:1.0.0
```

**Start Build Orchestrator Only:**
```bash
cd build_orchestrator_service
docker build -t build-orchestrator:1.0.0 .
docker run -p 8001:8001 build-orchestrator:1.0.0
```

### Option 3: Local Development (No Docker)

**Detection Service:**
```bash
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

**Build Orchestrator Service:**
```bash
cd build_orchestrator_service
pip install -r requirements.txt
python -m build_orchestrator_service.main
# Runs on http://localhost:8001
```

---

## 🧪 Test the Services

### 1. Health Check

```bash
# Detection Service
curl http://localhost:8000/api/health

# Build Orchestrator
curl http://localhost:8001/api/health

# Expected: {"status":"healthy",...}
```

### 2. Complete Workflow Example (Java Project)

**Step 1: Detect Project Stack**
```bash
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/spring-projects/spring-petclinic"
```

**Response:**
```json
{
  "primary": {
    "primary_language": "Java",
    "framework": "Spring Boot",
    "build_tool": "Maven",
    "confidence_score": 0.95
  }
}
```

**Step 2: Validate Project**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Java",
      "framework": "Spring Boot",
      "build_tool": "Maven",
      "confidence_score": 0.95,
      "detected_files": []
    },
    "project_path": "temp/repo"
  }'
```

**Step 3: Generate Missing Files**
```bash
curl -X POST http://localhost:8001/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Java",
    "file_type": "pom.xml",
    "version_config": {
      "java_version": "17",
      "packaging_type": "jar",
      "group_id": "com.example",
      "artifact_id": "myapp"
    }
  }'
```

**Step 4: Generate Dockerfile**
```bash
curl -X POST http://localhost:8001/api/generate-dockerfile \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Java",
    "file_type": "Dockerfile",
    "version_config": {
      "java_version": "17",
      "expose_port": 8080
    },
    "project_context": {
      "build_tool": "maven"
    }
  }'
```

---

## 📚 Interactive API Documentation

### Swagger UI

**Build Orchestrator:**
- Open browser: `http://localhost:8001/docs`
- Interactive API testing
- Request/response schemas
- Try all endpoints

**Detection Service:**
- Open browser: `http://localhost:8000/docs`

---

## 🔍 Example: Node.js React App

```bash
# 1. Scan project
curl -X POST http://localhost:8000/api/scan \
  -F "github_url=https://github.com/facebook/create-react-app"

# 2. Validate
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Node.js",
      "framework": "React",
      "build_tool": "npm",
      "confidence_score": 0.88,
      "detected_files": []
    },
    "project_path": "temp/react-app"
  }'

# 3. Generate package.json
curl -X POST http://localhost:8001/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Node.js",
    "file_type": "package.json",
    "version_config": {
      "node_version": "18",
      "package_name": "my-react-app"
    },
    "project_context": {
      "framework": "React"
    }
  }'

# 4. Generate Dockerfile
curl -X POST http://localhost:8001/api/generate-dockerfile \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Node.js",
    "file_type": "Dockerfile",
    "version_config": {
      "node_version": "18",
      "expose_port": 3000
    },
    "project_context": {
      "framework": "React",
      "needs_build": true
    }
  }'
```

---

## 🛠 Useful Commands

### Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart build-orchestrator

# Scale services
docker-compose up -d --scale build-orchestrator=3

# Remove everything
docker-compose down -v
```

### Check Service Status

```bash
# List running containers
docker ps

# Check logs for specific service
docker logs build-orchestrator

# Execute command in container
docker exec -it build-orchestrator sh
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check if ports are already in use
lsof -i :8000
lsof -i :8001

# Check Docker logs
docker-compose logs build-orchestrator
```

### Template Generation Fails

```bash
# Check if templates directory exists
docker exec -it build-orchestrator ls /app/templates

# Verify Jinja2 installation
docker exec -it build-orchestrator pip list | grep jinja2
```

### Connection Refused

```bash
# Check if services are running
curl http://localhost:8001/api/health

# Check network connectivity
docker-compose exec build-orchestrator ping detection-service
```

---

## 📊 Monitoring

### Health Checks

```bash
# Continuous health monitoring
watch -n 5 'curl -s http://localhost:8001/api/health'
```

### Metrics

```bash
# Get service metrics
curl http://localhost:8001/metrics
```

---

## 🎯 Platform-Specific Examples

See `build_orchestrator_service/API_EXAMPLES.md` for complete examples:

- ☕ Java (Maven, Gradle)
- 🟨 Node.js (React, Vue, Next.js)
- 🐍 Python (FastAPI, Flask)
- 🟪 .NET (ASP.NET Core)
- 🐹 Go

---

## 📖 Further Reading

- **Architecture Details:** `MICROSERVICES_ARCHITECTURE.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Build Orchestrator Docs:** `build_orchestrator_service/README.md`
- **API Examples:** `build_orchestrator_service/API_EXAMPLES.md`

---

## 🚦 Production Deployment

### Environment Variables

```bash
# .env file
DETECTION_SERVICE_URL=http://detection-service:8000
BUILD_ORCHESTRATOR_URL=http://build-orchestrator:8001
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### Security Hardening

1. Enable authentication between services
2. Use HTTPS/TLS
3. Restrict CORS origins
4. Enable rate limiting
5. Add API keys

---

## ✅ Verification

Run the verification script:

```bash
./verify_implementation.sh
```

Expected output: `✅ Verification SUCCESSFUL - All components present!`

---

## 🎉 You're Ready!

The microservice platform is now running and ready to:

✅ Detect project stacks  
✅ Validate build configurations  
✅ Generate missing files  
✅ Create optimized Dockerfiles  
✅ Support 5 platforms (Java, Node.js, Python, .NET, Go)  

**Happy building! 🚀**
