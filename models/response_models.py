from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum

class LanguageType(str, Enum):
    JAVA = "Java"
    NODEJS = "Node.js"
    PYTHON = "Python"
    DOTNET = ".NET"
    GO = "Go"
    RUST = "Rust"
    PHP = "PHP"
    RUBY = "Ruby"
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
    CARGO = "cargo"
    COMPOSER = "composer"
    BUNDLE = "bundle"

class ConfidenceLevel(str, Enum):
    """Confidence level classification"""
    UNRELIABLE = "unreliable"      # < 0.45
    MODERATE = "moderate"           # 0.45 - 0.64
    HIGH = "high"                   # 0.65 - 0.79
    VERY_HIGH = "very_high"         # >= 0.80

class DetectionResult(BaseModel):
    primary_language: LanguageType
    framework: Optional[str] = None
    build_tool: Optional[BuildTool] = None
    build_required: bool = False
    build_command: Optional[str] = None
    install_command: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: Optional[ConfidenceLevel] = None
    detected_files: List[str] = []
    
    def __init__(self, **data):
        """Initialize and auto-calculate confidence level"""
        super().__init__(**data)
        if self.confidence_level is None:
            score = self.confidence_score
            if score < 0.45:
                self.confidence_level = ConfidenceLevel.UNRELIABLE
            elif score < 0.65:
                self.confidence_level = ConfidenceLevel.MODERATE
            elif score < 0.80:
                self.confidence_level = ConfidenceLevel.HIGH
            else:
                self.confidence_level = ConfidenceLevel.VERY_HIGH

class ScanRequest(BaseModel):
    github_url: Optional[str] = None
    min_confidence: Optional[float] = Field(default=0.45, ge=0.0, le=1.0, 
                                            description="Minimum confidence threshold (default: 0.45)")
    
class MultiDetectionResult(BaseModel):
    detections: List[DetectionResult]
    primary: DetectionResult
    min_confidence_threshold: float = 0.45
    project_path: Optional[str] = None  # Path to scanned project for Build Orchestrator
