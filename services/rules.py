from typing import Dict, List, Tuple, Any
import json
import os

class DetectionRules:
    """Centralized detection rules for different platforms"""
    
    # File patterns for each platform
    PLATFORM_FILES = {
        "java": {
            "primary": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "secondary": ["src/main/java", "gradlew", "mvnw", "gradlew.bat", "mvnw.cmd"],
            "structure_indicators": ["src/main/resources", "src/test/java", "src/main/webapp"],
            "config_files": ["application.properties", "application.yml", "application.yaml"],
            "framework_indicators": {
                "Spring Boot": ["spring-boot-starter", "SpringBootApplication", "@SpringBootApplication", 
                               "application.properties", "application.yml"],
                "Spring": ["springframework", "@Component", "@Service", "@Controller"],
                "Jakarta EE": ["jakarta.servlet", "persistence.xml", "beans.xml"],
                "Micronaut": ["micronaut", "@Controller"],
                "Quarkus": ["quarkus", "application.properties"],
                "Maven": ["pom.xml"],
                "Gradle": ["build.gradle", "build.gradle.kts", "settings.gradle"]
            },
            "content_patterns": {
                "pom.xml": ["<groupId>org.springframework.boot</groupId>", "<artifactId>spring-boot", 
                           "<groupId>jakarta.enterprise</groupId>", "<groupId>io.micronaut</groupId>"],
                "build.gradle": ["spring-boot-starter", "org.springframework.boot", "io.micronaut"],
                "*.java": ["@SpringBootApplication", "@RestController", "@Service", "@Component"]
            }
        },
        "nodejs": {
            "primary": ["package.json"],
            "secondary": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "node_modules", 
                         ".npmrc", ".yarnrc", "pnpm-workspace.yaml"],
            "structure_indicators": ["src", "public", "dist", "build"],
            "config_files": ["tsconfig.json", "webpack.config.js", "vite.config.js", "next.config.js", 
                           "vue.config.js", "nuxt.config.js", ".babelrc", "jest.config.js"],
            "framework_indicators": {
                "React": ["react", "react-dom", "create-react-app", "jsx"],
                "Next.js": ["next", "next.config", "pages", "app"],
                "Vue.js": ["vue", "@vue", "vuex", "vue-router"],
                "Nuxt.js": ["nuxt", "nuxt.config"],
                "Angular": ["@angular/core", "angular.json"],
                "Express": ["express", "app.use", "app.listen"],
                "NestJS": ["@nestjs/core", "@nestjs/common"],
                "Fastify": ["fastify"],
                "Koa": ["koa"],
                "Svelte": ["svelte", "svelte.config"],
                "Gatsby": ["gatsby", "gatsby-config"],
                "Electron": ["electron"]
            },
            "content_patterns": {
                "package.json": ["\"react\":", "\"next\":", "\"vue\":", "\"express\":", "\"@nestjs/core\":",
                                "\"angular\":", "\"svelte\":", "\"gatsby\":", "\"electron\":"],
                "*.jsx": ["import React", "from 'react'", "export default"],
                "*.tsx": ["import React", "from 'react'", "interface", "type"]
            }
        },
        "python": {
            "primary": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock"],
            "secondary": ["manage.py", "app.py", "main.py", "__init__.py", "setup.cfg", 
                         "Pipfile.lock", "tox.ini", "pytest.ini"],
            "structure_indicators": ["src", "tests", "docs"],
            "config_files": ["setup.cfg", "pyproject.toml", "tox.ini", ".flake8", "mypy.ini"],
            "framework_indicators": {
                "Django": ["django", "manage.py", "settings.py", "urls.py", "wsgi.py"],
                "Flask": ["flask", "Flask", "app.py", "from flask import"],
                "FastAPI": ["fastapi", "FastAPI", "uvicorn", "from fastapi import"],
                "Tornado": ["tornado"],
                "Pyramid": ["pyramid"],
                "Bottle": ["bottle"],
                "Streamlit": ["streamlit", "st."],
                "Celery": ["celery", "from celery import"],
                "Scrapy": ["scrapy", "scrapy.cfg"],
                "Jupyter": ["jupyter", ".ipynb"]
            },
            "content_patterns": {
                "requirements.txt": ["django", "flask", "fastapi", "tornado", "pyramid"],
                "pyproject.toml": ["django", "flask", "fastapi", "poetry"],
                "*.py": ["from django", "from flask import", "from fastapi import", "FastAPI()", 
                        "Flask(__name__)"]
            }
        },
        "dotnet": {
            "primary": ["*.csproj", "*.sln", "*.fsproj", "*.vbproj"],
            "secondary": ["Program.cs", "Startup.cs", "appsettings.json", "appsettings.Development.json",
                         "web.config", "nuget.config"],
            "structure_indicators": ["Controllers", "Models", "Views", "Properties", "wwwroot"],
            "config_files": ["appsettings.json", "launchSettings.json", "web.config"],
            "framework_indicators": {
                "ASP.NET Core": ["Microsoft.AspNetCore", "Startup.cs", "Program.cs"],
                "ASP.NET MVC": ["System.Web.Mvc", "Controllers", "Views"],
                "Blazor": ["Microsoft.AspNetCore.Components", "Blazor", ".razor"],
                "WPF": ["System.Windows", "App.xaml"],
                "WinForms": ["System.Windows.Forms"],
                "Console App": ["Program.cs", "static void Main"],
                "Web API": ["ApiController", "Microsoft.AspNetCore.Mvc"],
                "gRPC": ["Grpc.AspNetCore", ".proto"]
            },
            "content_patterns": {
                "*.csproj": ["Microsoft.NET.Sdk.Web", "Microsoft.AspNetCore", "Microsoft.EntityFrameworkCore"],
                "Program.cs": ["WebApplication.CreateBuilder", "app.Run()", "static void Main"]
            }
        },
        "go": {
            "primary": ["go.mod"],
            "secondary": ["go.sum", "main.go", "Makefile"],
            "structure_indicators": ["cmd", "pkg", "internal", "api"],
            "config_files": ["go.work", ".golangci.yml"],
            "framework_indicators": {
                "Gin": ["gin-gonic/gin", "gin.Default()", "gin.Engine"],
                "Echo": ["labstack/echo", "echo.New()"],
                "Fiber": ["gofiber/fiber"],
                "Chi": ["go-chi/chi"],
                "Gorilla Mux": ["gorilla/mux"],
                "Beego": ["beego"],
                "Buffalo": ["gobuffalo/buffalo"],
                "Standard": ["net/http", "http.ListenAndServe"]
            },
            "content_patterns": {
                "go.mod": ["gin-gonic", "labstack/echo", "gofiber", "go-chi", "gorilla/mux"],
                "*.go": ["package main", "func main()", "import ("]
            }
        },
        "rust": {
            "primary": ["Cargo.toml"],
            "secondary": ["Cargo.lock", "main.rs", "lib.rs"],
            "structure_indicators": ["src", "tests", "benches"],
            "config_files": ["rust-toolchain", ".cargo/config.toml"],
            "framework_indicators": {
                "Actix": ["actix-web", "actix_web"],
                "Rocket": ["rocket"],
                "Axum": ["axum"],
                "Warp": ["warp"],
                "Tokio": ["tokio"]
            },
            "content_patterns": {
                "Cargo.toml": ["actix-web", "rocket", "axum", "warp", "tokio"],
                "*.rs": ["fn main()", "use actix_web", "use rocket"]
            }
        },
        "php": {
            "primary": ["composer.json"],
            "secondary": ["composer.lock", "index.php", "artisan", "wp-config.php"],
            "structure_indicators": ["vendor", "public", "app", "src"],
            "config_files": [".env", "config.php"],
            "framework_indicators": {
                "Laravel": ["laravel/framework", "artisan", "app/Http"],
                "Symfony": ["symfony/symfony", "symfony/framework-bundle"],
                "WordPress": ["wp-config.php", "wp-content", "wp-includes"],
                "CodeIgniter": ["codeigniter", "system/core"],
                "CakePHP": ["cakephp/cakephp"],
                "Yii": ["yiisoft/yii2"]
            },
            "content_patterns": {
                "composer.json": ["laravel/framework", "symfony/symfony", "cakephp", "yiisoft"],
                "*.php": ["<?php", "namespace", "use Illuminate"]
            }
        },
        "ruby": {
            "primary": ["Gemfile"],
            "secondary": ["Gemfile.lock", "Rakefile", "config.ru"],
            "structure_indicators": ["app", "config", "db", "lib"],
            "config_files": ["config/application.rb", "config/environment.rb"],
            "framework_indicators": {
                "Ruby on Rails": ["rails", "config/application.rb", "app/controllers"],
                "Sinatra": ["sinatra"],
                "Hanami": ["hanami"],
                "Jekyll": ["jekyll", "_config.yml"]
            },
            "content_patterns": {
                "Gemfile": ["gem 'rails'", "gem 'sinatra'", "gem 'jekyll'"],
                "*.rb": ["class ApplicationController", "Rails.application"]
            }
        }
    }
    
    # Enhanced scoring weights for better accuracy
    SCORE_WEIGHTS = {
        "primary_file": 0.35,           # Core project files (reduced from 0.5)
        "secondary_file": 0.10,         # Supporting files (reduced from 0.2)
        "structure_indicator": 0.15,    # Directory structure (NEW)
        "config_file": 0.10,            # Configuration files (NEW)
        "framework_match": 0.20,        # Framework detection (increased from 0.2)
        "content_match": 0.10           # File content analysis (NEW - replaces lock_file)
    }
    
    # Minimum confidence threshold recommendations
    CONFIDENCE_THRESHOLDS = {
        "minimum": 0.45,      # Below this, detection is unreliable
        "moderate": 0.65,     # Moderate confidence - proceed with caution
        "high": 0.80,         # High confidence - safe for automation
        "very_high": 0.90     # Very high confidence - fully automated
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
        },
        "rust": {
            "cargo": "cargo build --release"
        },
        "php": {
            "composer": "composer install"
        },
        "ruby": {
            "bundle": "bundle install"
        }
    }
    
    # Directories to ignore during scanning
    IGNORED_DIRS = {
        "node_modules", ".git", "venv", "__pycache__", 
        "target", "build", "dist", ".vscode", ".idea",
        "bin", "obj", "vendor"
    }
