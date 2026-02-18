"""Request models for Build Orchestrator Service"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class LanguageType(str, Enum):
    """Supported language platforms"""
    JAVA = "Java"
    NODEJS = "Node.js"
    PYTHON = "Python"
    DOTNET = ".NET"
    GO = "Go"
    RUST = "Rust"
    PHP = "PHP"
    RUBY = "Ruby"


class FileType(str, Enum):
    """Types of files that can be generated"""
    POM_XML = "pom.xml"
    BUILD_GRADLE = "build.gradle"
    PACKAGE_JSON = "package.json"
    REQUIREMENTS_TXT = "requirements.txt"
    PYPROJECT_TOML = "pyproject.toml"
    CSPROJ = "csproj"
    GO_MOD = "go.mod"
    CARGO_TOML = "Cargo.toml"
    GEMFILE = "Gemfile"
    COMPOSER_JSON = "composer.json"
    DOCKERFILE = "Dockerfile"


class PackagingType(str, Enum):
    """Java packaging types"""
    JAR = "jar"
    WAR = "war"


class ProjectType(str, Enum):
    """.NET project types"""
    WEB_API = "WebAPI"
    CONSOLE = "Console"
    WEB = "Web"


class VersionConfig(BaseModel):
    """Configuration for runtime and dependency versions"""
    
    # Common
    runtime_version: Optional[str] = Field(
        None, 
        description="Runtime version (e.g., Java 17, Python 3.11, Node 18)"
    )
    
    # Java specific
    java_version: Optional[str] = Field(None, description="Java version (8, 11, 17, 21)")
    packaging_type: Optional[PackagingType] = Field(None, description="Java packaging type")
    group_id: Optional[str] = Field(None, description="Maven group ID")
    artifact_id: Optional[str] = Field(None, description="Maven artifact ID")
    
    # Node.js specific
    node_version: Optional[str] = Field(None, description="Node.js version")
    npm_version: Optional[str] = Field(None, description="npm version")
    package_name: Optional[str] = Field(None, description="Package name")
    
    # Python specific
    python_version: Optional[str] = Field(None, description="Python version")
    project_name: Optional[str] = Field(None, description="Python project name")
    
    # .NET specific
    dotnet_version: Optional[str] = Field(None, description=".NET version (net6.0, net7.0, net8.0)")
    project_type: Optional[ProjectType] = Field(None, description=".NET project type")
    
    # Go specific
    go_version: Optional[str] = Field(None, description="Go version")
    module_name: Optional[str] = Field(None, description="Go module name")
    
    # Rust specific
    rust_version: Optional[str] = Field(None, description="Rust version")
    package_name_rust: Optional[str] = Field(None, description="Rust package name")
    
    # Ruby specific
    ruby_version: Optional[str] = Field(None, description="Ruby version")
    
    # PHP specific
    php_version: Optional[str] = Field(None, description="PHP version")
    
    # Dockerfile specific
    base_image: Optional[str] = Field(None, description="Docker base image")
    expose_port: Optional[int] = Field(None, description="Port to expose in Dockerfile")
    
    # Additional dependencies
    dependencies: Optional[List[str]] = Field(
        default_factory=list, 
        description="Additional dependencies to include"
    )
    
    # Custom environment variables
    env_vars: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Environment variables for Dockerfile"
    )


class DetectionResult(BaseModel):
    """Detection result from the Detection Service"""
    primary_language: str
    framework: Optional[str] = None
    build_tool: Optional[str] = None
    build_required: bool = False
    build_command: Optional[str] = None
    install_command: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: Optional[str] = None
    detected_files: List[str] = []


class ValidationRequest(BaseModel):
    """Request to validate a detected project"""
    detection_result: DetectionResult = Field(
        ..., 
        description="Detection result from the Detection Service"
    )
    project_path: str = Field(
        ..., 
        description="Path to the project directory (read-only access)"
    )
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that project_path doesn't contain path traversal"""
        if '..' in v:
            raise ValueError("Invalid project path: path traversal not allowed")
        return v


class TemplateGenerationRequest(BaseModel):
    """Request to generate a template file"""
    platform: LanguageType = Field(..., description="Target platform")
    file_type: FileType = Field(..., description="Type of file to generate")
    version_config: VersionConfig = Field(
        default_factory=VersionConfig,
        description="Version and configuration settings"
    )
    project_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional project context for template generation"
    )


class DockerOptionsRequest(BaseModel):
    """Request to get Dockerfile options"""
    project_path: str = Field(
        ..., 
        description="Path to the project directory"
    )
    platform: LanguageType = Field(..., description="Detected platform")
    version_config: Optional[VersionConfig] = Field(
        default_factory=VersionConfig,
        description="Version configuration for Dockerfile generation"
    )
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that project_path doesn't contain path traversal"""
        if '..' in v:
            raise ValueError("Invalid project path: path traversal not allowed")
        return v
