"""
Docker Generator Service

Handles Dockerfile detection, validation, and generation
for all supported platforms.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from models.request_models import LanguageType, FileType, VersionConfig
from models.response_models import DockerfileStatus, DockerOption
from services.template_engine import TemplateEngine


class DockerGenerator:
    """Service for Dockerfile generation and management"""
    
    def __init__(self):
        """Initialize Docker generator with template engine"""
        self.template_engine = TemplateEngine()
        self.docker_options = self._initialize_docker_options()
    
    def _initialize_docker_options(self) -> Dict:
        """Define Docker options for each platform"""
        return {
            LanguageType.JAVA: {
                "base_images": [
                    {"version": "21", "image": "eclipse-temurin:21-jdk"},
                    {"version": "17", "image": "eclipse-temurin:17-jdk"},
                    {"version": "11", "image": "eclipse-temurin:11-jdk"},
                    {"version": "8", "image": "eclipse-temurin:8-jdk"}
                ],
                "default_port": 8080,
                "supports_multistage": True
            },
            LanguageType.NODEJS: {
                "base_images": [
                    {"version": "20", "image": "node:20-alpine"},
                    {"version": "18", "image": "node:18-alpine"},
                    {"version": "16", "image": "node:16-alpine"}
                ],
                "default_port": 3000,
                "supports_multistage": True
            },
            LanguageType.PYTHON: {
                "base_images": [
                    {"version": "3.12", "image": "python:3.12-slim"},
                    {"version": "3.11", "image": "python:3.11-slim"},
                    {"version": "3.10", "image": "python:3.10-slim"},
                    {"version": "3.9", "image": "python:3.9-slim"}
                ],
                "default_port": 8000,
                "supports_multistage": True
            },
            LanguageType.DOTNET: {
                "base_images": [
                    {"version": "8.0", "image": "mcr.microsoft.com/dotnet/aspnet:8.0"},
                    {"version": "7.0", "image": "mcr.microsoft.com/dotnet/aspnet:7.0"},
                    {"version": "6.0", "image": "mcr.microsoft.com/dotnet/aspnet:6.0"}
                ],
                "default_port": 80,
                "supports_multistage": True
            },
            LanguageType.GO: {
                "base_images": [
                    {"version": "1.22", "image": "golang:1.22-alpine"},
                    {"version": "1.21", "image": "golang:1.21-alpine"},
                    {"version": "1.20", "image": "golang:1.20-alpine"}
                ],
                "default_port": 8080,
                "supports_multistage": True
            },
            LanguageType.RUST: {
                "base_images": [
                    {"version": "1.76", "image": "rust:1.76-slim"},
                    {"version": "1.75", "image": "rust:1.75-slim"},
                    {"version": "1.74", "image": "rust:1.74-slim"}
                ],
                "default_port": 8080,
                "supports_multistage": True
            },
            LanguageType.RUBY: {
                "base_images": [
                    {"version": "3.3", "image": "ruby:3.3-slim"},
                    {"version": "3.2", "image": "ruby:3.2-slim"},
                    {"version": "3.1", "image": "ruby:3.1-slim"}
                ],
                "default_port": 3000,
                "supports_multistage": True
            },
            LanguageType.PHP: {
                "base_images": [
                    {"version": "8.3", "image": "php:8.3-fpm"},
                    {"version": "8.2", "image": "php:8.2-fpm"},
                    {"version": "8.1", "image": "php:8.1-fpm"}
                ],
                "default_port": 80,
                "supports_multistage": True
            }
        }
    
    def check_dockerfile_status(self, project_path: str) -> Tuple[DockerfileStatus, Optional[str]]:
        """
        Check if Dockerfile exists in project
        
        Args:
            project_path: Path to project directory
        
        Returns:
            Tuple of (status, dockerfile_path)
        """
        # Common Dockerfile locations
        dockerfile_names = ["Dockerfile", "dockerfile", "Dockerfile.dev", "Dockerfile.prod"]
        
        try:
            base_path = Path(project_path)
            
            for name in dockerfile_names:
                dockerfile_path = base_path / name
                if dockerfile_path.exists():
                    # Validate Dockerfile
                    if self._validate_dockerfile(dockerfile_path):
                        return DockerfileStatus.EXISTS, str(dockerfile_path)
                    else:
                        return DockerfileStatus.INVALID, str(dockerfile_path)
            
            return DockerfileStatus.MISSING, None
        
        except Exception:
            return DockerfileStatus.MISSING, None
    
    def _validate_dockerfile(self, dockerfile_path: Path) -> bool:
        """
        Validate Dockerfile content
        
        Args:
            dockerfile_path: Path to Dockerfile
        
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                
                # Basic validation - check for FROM instruction
                if not content.strip():
                    return False
                
                # Check for FROM instruction (required)
                if "FROM" not in content.upper():
                    return False
                
                return True
        except Exception:
            return False
    
    def get_docker_options(
        self,
        platform: LanguageType,
        dockerfile_status: DockerfileStatus
    ) -> List[DockerOption]:
        """
        Get available Docker options based on platform and status
        
        Args:
            platform: Target platform
            dockerfile_status: Current Dockerfile status
        
        Returns:
            List of available Docker options
        """
        options = []
        
        if dockerfile_status == DockerfileStatus.EXISTS:
            options.append(DockerOption(
                option="use_existing",
                description="Use the existing Dockerfile found in your project",
                automated=True
            ))
            options.append(DockerOption(
                option="regenerate",
                description="Generate a new optimized Dockerfile (will backup existing)",
                automated=True
            ))
            options.append(DockerOption(
                option="edit_existing",
                description="Manually edit the existing Dockerfile",
                automated=False
            ))
        
        elif dockerfile_status == DockerfileStatus.INVALID:
            options.append(DockerOption(
                option="fix_invalid",
                description="Fix the invalid Dockerfile automatically",
                automated=True
            ))
            options.append(DockerOption(
                option="regenerate",
                description="Generate a new Dockerfile (will backup invalid one)",
                automated=True
            ))
        
        else:  # MISSING
            options.append(DockerOption(
                option="generate_standard",
                description=f"Generate a standard Dockerfile for {platform.value}",
                automated=True
            ))
            
            # Add multi-stage option if supported
            if self.docker_options.get(platform, {}).get("supports_multistage"):
                options.append(DockerOption(
                    option="generate_multistage",
                    description=f"Generate an optimized multi-stage Dockerfile for {platform.value}",
                    automated=True
                ))
            
            options.append(DockerOption(
                option="upload_custom",
                description="Upload your own Dockerfile",
                automated=False
            ))
        
        return options
    
    def generate_dockerfile(
        self,
        platform: LanguageType,
        config: VersionConfig,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate Dockerfile content
        
        Args:
            platform: Target platform
            config: Version configuration
            context: Additional context for generation
        
        Returns:
            Generated Dockerfile content
        """
        # Prepare context for Dockerfile generation
        docker_context = self._prepare_dockerfile_context(platform, config, context)
        
        # Render Dockerfile template
        dockerfile_content = self.template_engine.render_template(
            platform=platform,
            file_type=FileType.DOCKERFILE,
            config=config,
            context=docker_context
        )
        
        return dockerfile_content
    
    def _prepare_dockerfile_context(
        self,
        platform: LanguageType,
        config: VersionConfig,
        context: Optional[Dict]
    ) -> Dict:
        """
        Prepare context for Dockerfile generation
        
        Args:
            platform: Target platform
            config: Version configuration
            context: Additional context
        
        Returns:
            Complete context for Dockerfile rendering
        """
        docker_context = context.copy() if context else {}
        
        # Get platform-specific defaults
        platform_defaults = self.docker_options.get(platform, {})
        
        # Set default port if not specified
        if not config.expose_port and "port" not in docker_context:
            docker_context["port"] = platform_defaults.get("default_port", 8080)
        
        # Add platform-specific context
        if platform == LanguageType.JAVA:
            docker_context.setdefault("build_tool", context.get("build_tool", "maven") if context else "maven")
            docker_context.setdefault("packaging_type", config.packaging_type.value if config.packaging_type else "jar")
        
        elif platform == LanguageType.NODEJS:
            docker_context.setdefault("package_manager", "npm")
            docker_context.setdefault("needs_build", False)
            docker_context.setdefault("main_file", "index.js")
            
            # Detect framework and set build requirements
            framework = context.get("framework") if context else None
            if framework in ["React", "Vue", "Next.js", "Angular"]:
                docker_context["needs_build"] = True
        
        elif platform == LanguageType.PYTHON:
            docker_context.setdefault("has_pyproject", False)
            docker_context.setdefault("has_requirements", True)
            docker_context.setdefault("has_pipfile", False)
            docker_context.setdefault("main_file", "main.py")
            
            # Detect framework
            framework = context.get("framework") if context else None
            docker_context["framework"] = framework
        
        elif platform == LanguageType.DOTNET:
            docker_context.setdefault("assembly_name", "MyApp.dll")
        
        elif platform == LanguageType.GO:
            docker_context.setdefault("has_go_sum", False)
            docker_context.setdefault("main_package", ".")
        
        elif platform == LanguageType.RUST:
            docker_context.setdefault("has_cargo_lock", False)
            docker_context.setdefault("binary_name", "app")
        
        elif platform == LanguageType.RUBY:
            docker_context.setdefault("framework", context.get("framework") if context else None)
            docker_context.setdefault("main_file", "app.rb")
        
        elif platform == LanguageType.PHP:
            docker_context.setdefault("framework", context.get("framework") if context else None)
        
        return docker_context
    
    def get_generation_config(self, platform: LanguageType) -> Dict:
        """
        Get Dockerfile generation configuration for a platform
        
        Args:
            platform: Target platform
        
        Returns:
            Configuration options for Dockerfile generation
        """
        platform_config = self.docker_options.get(platform, {})
        
        return {
            "base_images": platform_config.get("base_images", []),
            "default_port": platform_config.get("default_port", 8080),
            "supports_multistage": platform_config.get("supports_multistage", False),
            "optimization_options": {
                "multistage_build": platform_config.get("supports_multistage", False),
                "alpine_base": platform in [LanguageType.NODEJS, LanguageType.GO, LanguageType.RUST],
                "layer_caching": True
            }
        }
