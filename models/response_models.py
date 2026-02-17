from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class LanguageType(str, Enum):
    JAVA = "Java"
    NODEJS = "Node.js"
    PYTHON = "Python"
    DOTNET = ".NET"
    GO = "Go"
    UNKNOWN = "Unknown"

class BuildTool(str, Enum):
    MAVEN = "Maven"
    GRADLE = "Gradle"
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    DOTNET = "dotnet"
    GO = "go"

class DetectionResult(BaseModel):
    primary_language: LanguageType
    framework: Optional[str] = None
    build_tool: Optional[BuildTool] = None
    build_required: bool = False
    build_command: Optional[str] = None
    install_command: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detected_files: List[str] = []

class ScanRequest(BaseModel):
    github_url: Optional[str] = None
    
class MultiDetectionResult(BaseModel):
    detections: List[DetectionResult]
    primary: DetectionResult
