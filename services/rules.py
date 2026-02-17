from typing import Dict, List, Tuple, Any
import json
import os

class DetectionRules:
    """Centralized detection rules for different platforms"""
    
    # File patterns for each platform
    PLATFORM_FILES = {
        "java": {
            "primary": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "secondary": ["src/main/java", "gradlew", "mvnw"],
            "framework_indicators": {
                "Spring Boot": ["application.properties", "application.yml", 
                               "@SpringBootApplication", "spring-boot-starter"],
                "Maven": ["pom.xml"],
                "Gradle": ["build.gradle", "build.gradle.kts"]
            }
        },
        "nodejs": {
            "primary": ["package.json"],
            "secondary": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "node_modules"],
            "framework_indicators": {
                "React": ["react", "create-react-app"],
                "Next.js": ["next", "next.config"],
                "Vue.js": ["vue", "@vue"],
                "Express": ["express"],
                "NestJS": ["@nestjs"]
            }
        },
        "python": {
            "primary": ["requirements.txt", "pyproject.toml", "setup.py"],
            "secondary": ["manage.py", "app.py", "main.py", "__init__.py"],
            "framework_indicators": {
                "Django": ["manage.py", "settings.py", "django"],
                "Flask": ["flask", "app.py"],
                "FastAPI": ["fastapi", "main.py"]
            }
        },
        "dotnet": {
            "primary": ["*.csproj", "*.sln"],
            "secondary": ["Program.cs", "Startup.cs", "appsettings.json"],
            "framework_indicators": {
                "ASP.NET Core": ["Microsoft.AspNetCore", "Startup.cs"],
                "Console App": ["Program.cs"]
            }
        },
        "go": {
            "primary": ["go.mod"],
            "secondary": ["go.sum", "main.go"],
            "framework_indicators": {
                "Gin": ["gin-gonic"],
                "Echo": ["labstack/echo"],
                "Standard": ["main.go"]
            }
        }
    }
    
    # Scoring weights
    SCORE_WEIGHTS = {
        "primary_file": 0.5,
        "secondary_file": 0.2,
        "framework_file": 0.2,
        "lock_file": 0.1
    }
    
    # Build commands
    BUILD_COMMANDS = {
        "java": {
            "Maven": "mvn clean package",
            "Gradle": "gradle build"
        },
        "nodejs": {
            "npm": "npm run build",
            "yarn": "yarn build",
            "pnpm": "pnpm build"
        },
        "python": {
            "pip": "pip install -r requirements.txt"
        },
        "dotnet": {
            "dotnet": "dotnet build"
        },
        "go": {
            "go": "go build"
        }
    }
    
    # Directories to ignore during scanning
    IGNORED_DIRS = {
        "node_modules", ".git", "venv", "__pycache__", 
        "target", "build", "dist", ".vscode", ".idea",
        "bin", "obj", "vendor"
    }
