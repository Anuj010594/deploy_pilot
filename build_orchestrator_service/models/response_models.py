"""Response models for Build Orchestrator Service"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation status outcomes"""
    READY = "ready"
    MISSING_FILES = "missing_files"
    INCOMPLETE = "incomplete"
    ERROR = "error"


class DockerfileStatus(str, Enum):
    """Dockerfile existence status"""
    EXISTS = "exists"
    MISSING = "missing"
    INVALID = "invalid"


class Severity(str, Enum):
    """Severity levels for missing files"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MissingFile(BaseModel):
    """Details about a missing file"""
    file_name: str = Field(..., description="Name of the missing file")
    file_type: str = Field(..., description="Type/category of the file")
    severity: Severity = Field(..., description="Severity of the missing file")
    description: str = Field(..., description="Why this file is needed")
    can_generate: bool = Field(
        default=False,
        description="Whether this file can be auto-generated"
    )


class Suggestion(BaseModel):
    """Suggestion for corrective action"""
    action: str = Field(..., description="Suggested action to take")
    description: str = Field(..., description="Detailed description of the action")
    automated: bool = Field(
        default=False,
        description="Whether this action can be automated"
    )
    file_type: Optional[str] = Field(None, description="Related file type")
    priority: int = Field(default=1, ge=1, le=3, description="Priority (1=highest, 3=lowest)")


class VersionOption(BaseModel):
    """Available version option"""
    version: str = Field(..., description="Version identifier")
    recommended: bool = Field(default=False, description="Whether this is the recommended version")
    description: Optional[str] = Field(None, description="Description of this version")


class ValidationResponse(BaseModel):
    """Response from validation endpoint"""
    status: ValidationStatus = Field(..., description="Overall validation status")
    platform: str = Field(..., description="Detected platform")
    missing_files: List[MissingFile] = Field(
        default_factory=list,
        description="List of missing files"
    )
    suggestions: List[Suggestion] = Field(
        default_factory=list,
        description="Suggested corrective actions"
    )
    available_actions: List[str] = Field(
        default_factory=list,
        description="Actions available to the user (e.g., 'build', 'dockerize')"
    )
    version_options: Dict[str, List[VersionOption]] = Field(
        default_factory=dict,
        description="Available version options for the platform"
    )
    validation_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional validation details"
    )


class TemplateGenerationResponse(BaseModel):
    """Response from template generation endpoint"""
    success: bool = Field(..., description="Whether generation was successful")
    file_type: str = Field(..., description="Type of file generated")
    content: Optional[str] = Field(None, description="Generated file content")
    file_name: str = Field(..., description="Suggested file name")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata about the generated file"
    )


class DockerOption(BaseModel):
    """Option for Dockerfile handling"""
    option: str = Field(..., description="Option identifier")
    description: str = Field(..., description="Description of the option")
    automated: bool = Field(default=False, description="Whether this can be automated")


class DockerOptionsResponse(BaseModel):
    """Response from docker-options endpoint"""
    dockerfile_status: DockerfileStatus = Field(..., description="Status of Dockerfile")
    dockerfile_path: Optional[str] = Field(None, description="Path to existing Dockerfile")
    options: List[DockerOption] = Field(
        default_factory=list,
        description="Available options for Dockerfile handling"
    )
    can_generate: bool = Field(
        default=True,
        description="Whether Dockerfile can be auto-generated"
    )
    generation_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Configuration options for Dockerfile generation"
    )
    platform: str = Field(..., description="Target platform")
