# Build Orchestrator Service - API Examples

Complete examples for all API endpoints across all supported platforms.

## Table of Contents

- [Java Examples](#java-examples)
- [Node.js Examples](#nodejs-examples)
- [Python Examples](#python-examples)
- [.NET Examples](#dotnet-examples)
- [Go Examples](#go-examples)

---

## Java Examples

### Validate Java Project (Missing pom.xml)

**Request:**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Java",
      "framework": "Spring Boot",
      "build_tool": "Maven",
      "confidence_score": 0.92,
      "detected_files": ["src/main/java/"]
    },
    "project_path": "projects/java-app"
  }'
```

**Response:**
```json
{
  "status": "missing_files",
  "platform": "Java",
  "missing_files": [
    {
      "file_name": "pom.xml OR build.gradle OR build.gradle.kts",
      "file_type": "build_config",
      "severity": "critical",
      "description": "Java build configuration file (Maven or Gradle)",
      "can_generate": true
    }
  ],
  "suggestions": [
    {
      "action": "Generate Maven pom.xml",
      "description": "Create a minimal Maven configuration file with standard Java project structure",
      "automated": true,
      "file_type": "build_config",
      "priority": 1
    },
    {
      "action": "Generate Gradle build.gradle",
      "description": "Create a Gradle build configuration file (modern alternative to Maven)",
      "automated": true,
      "file_type": "build_config",
      "priority": 2
    }
  ],
  "available_actions": ["generate_files", "manual_fix"],
  "version_options": {
    "java_version": [
      {"version": "21", "recommended": true, "description": "Java 21 LTS (Latest)"},
      {"version": "17", "recommended": true, "description": "Java 17 LTS"},
      {"version": "11", "recommended": false, "description": "Java 11 LTS"}
    ]
  }
}
```

### Generate Maven pom.xml

**Request:**
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

### Generate Java Dockerfile

**Request:**
```bash
curl -X POST http://localhost:8001/api/generate-dockerfile \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Java",
    "file_type": "Dockerfile",
    "version_config": {
      "java_version": "17",
      "packaging_type": "jar",
      "expose_port": 8080
    },
    "project_context": {
      "build_tool": "maven"
    }
  }'
```

---

## Node.js Examples

### Validate Node.js Project (Missing package.json)

**Request:**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Node.js",
      "framework": "React",
      "build_tool": "npm",
      "confidence_score": 0.88,
      "detected_files": ["src/", "public/"]
    },
    "project_path": "projects/react-app"
  }'
```

### Generate package.json for React

**Request:**
```bash
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
      "framework": "React",
      "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0"
      }
    }
  }'
```

### Generate Node.js Dockerfile

**Request:**
```bash
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
      "needs_build": true,
      "package_manager": "npm"
    }
  }'
```

---

## Python Examples

### Validate Python Project

**Request:**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Python",
      "framework": "FastAPI",
      "build_tool": "pip",
      "confidence_score": 0.95,
      "detected_files": ["main.py", "app/"]
    },
    "project_path": "projects/fastapi-app"
  }'
```

### Generate requirements.txt

**Request:**
```bash
curl -X POST http://localhost:8001/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Python",
    "file_type": "requirements.txt",
    "version_config": {
      "python_version": "3.11",
      "dependencies": [
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.3"
      ]
    }
  }'
```

### Generate Python Dockerfile

**Request:**
```bash
curl -X POST http://localhost:8001/api/generate-dockerfile \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Python",
    "file_type": "Dockerfile",
    "version_config": {
      "python_version": "3.11",
      "expose_port": 8000
    },
    "project_context": {
      "framework": "FastAPI",
      "has_requirements": true,
      "main_module": "main:app"
    }
  }'
```

---

## .NET Examples

### Validate .NET Project

**Request:**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": ".NET",
      "framework": "ASP.NET Core",
      "build_tool": "dotnet",
      "confidence_score": 0.90,
      "detected_files": ["Controllers/", "Program.cs"]
    },
    "project_path": "projects/dotnet-api"
  }'
```

### Generate .csproj

**Request:**
```bash
curl -X POST http://localhost:8001/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "platform": ".NET",
    "file_type": "csproj",
    "version_config": {
      "dotnet_version": "net8.0",
      "project_type": "WebAPI"
    },
    "project_context": {
      "namespace": "MyWebApi"
    }
  }'
```

---

## Go Examples

### Validate Go Project

**Request:**
```bash
curl -X POST http://localhost:8001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "primary_language": "Go",
      "framework": null,
      "build_tool": "go",
      "confidence_score": 0.93,
      "detected_files": ["main.go", "cmd/"]
    },
    "project_path": "projects/go-app"
  }'
```

### Generate go.mod

**Request:**
```bash
curl -X POST http://localhost:8001/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Go",
    "file_type": "go.mod",
    "version_config": {
      "go_version": "1.22",
      "module_name": "github.com/myorg/myapp"
    }
  }'
```

---

## Additional Endpoints

### Get Version Options

```bash
curl http://localhost:8001/api/version-options/java
```

### Get Docker Base Images

```bash
curl http://localhost:8001/api/base-images/nodejs
```

### Health Check

```bash
curl http://localhost:8001/api/health
```
