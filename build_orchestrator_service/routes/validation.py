"""
Validation Routes

Endpoints for project validation and template generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models.request_models import (
    ValidationRequest,
    TemplateGenerationRequest,
    LanguageType
)
from models.response_models import (
    ValidationResponse,
    ValidationStatus,
    TemplateGenerationResponse
)
from services.validator import ValidationService
from services.suggestion_engine import SuggestionEngine
from services.template_engine import TemplateEngine

router = APIRouter(prefix="/api", tags=["validation"])

# Initialize services
validator = ValidationService()
suggestion_engine = SuggestionEngine()
template_engine = TemplateEngine()


@router.post("/validate", response_model=ValidationResponse)
async def validate_project(request: ValidationRequest):
    """
    Validate a project based on detection results
    
    This endpoint performs comprehensive validation of project build files
    and returns suggestions for missing or incomplete configurations.
    
    **Damage Containment:**
    - Read-only access to project files
    - No code execution
    - Path traversal protection via Pydantic validators
    
    Args:
        request: Validation request containing detection result and project path
    
    Returns:
        ValidationResponse with status, missing files, suggestions, and version options
    
    Raises:
        HTTPException: 400 for invalid input, 500 for internal errors
    """
    try:
        # Perform validation
        status, missing_files, version_options = validator.validate_project(
            detection_result=request.detection_result,
            project_path=request.project_path
        )
        
        # Generate suggestions based on missing files
        suggestions = suggestion_engine.generate_suggestions(
            missing_files=missing_files,
            detection_result=request.detection_result
        )
        
        # Determine available actions
        available_actions = validator.get_available_actions(status)
        
        # Prepare validation details
        validation_details = {
            "total_missing_files": len(missing_files),
            "critical_issues": len([f for f in missing_files if f.severity.value == "critical"]),
            "warnings": len([f for f in missing_files if f.severity.value == "warning"]),
            "platform": request.detection_result.primary_language,
            "framework": request.detection_result.framework,
            "confidence_score": request.detection_result.confidence_score
        }
        
        return ValidationResponse(
            status=status,
            platform=request.detection_result.primary_language,
            missing_files=missing_files,
            suggestions=suggestions,
            available_actions=available_actions,
            version_options=version_options,
            validation_details=validation_details
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error but don't expose internal details
        raise HTTPException(
            status_code=500, 
            detail="Validation failed due to internal error"
        )


@router.post("/generate-template", response_model=TemplateGenerationResponse)
async def generate_template(request: TemplateGenerationRequest):
    """
    Generate a template file for a specific platform and file type
    
    This endpoint generates configuration files (pom.xml, package.json, etc.)
    based on the specified platform and version configuration.
    
    **Damage Containment:**
    - Template rendering only, no file system writes
    - No code execution
    - Stateless operation
    
    Args:
        request: Template generation request with platform, file type, and config
    
    Returns:
        TemplateGenerationResponse with generated content
    
    Raises:
        HTTPException: 400 for invalid input, 500 for generation errors
    """
    try:
        # Generate template content
        content = template_engine.render_template(
            platform=request.platform,
            file_type=request.file_type,
            config=request.version_config,
            context=request.project_context
        )
        
        # Get recommended file name
        file_name = template_engine.get_recommended_file_name(
            platform=request.platform,
            file_type=request.file_type,
            context=request.project_context
        )
        
        # Prepare metadata
        metadata = {
            "platform": request.platform.value,
            "file_type": request.file_type.value,
            "runtime_version": request.version_config.runtime_version,
            "generated_at": "2026-02-18T06:58:25Z"  # Would use actual timestamp
        }
        
        return TemplateGenerationResponse(
            success=True,
            file_type=request.file_type.value,
            content=content,
            file_name=file_name,
            metadata=metadata
        )
    
    except ValueError as e:
        return TemplateGenerationResponse(
            success=False,
            file_type=request.file_type.value,
            file_name=str(request.file_type.value),
            error=str(e)
        )
    except Exception as e:
        return TemplateGenerationResponse(
            success=False,
            file_type=request.file_type.value,
            file_name=str(request.file_type.value),
            error="Template generation failed due to internal error"
        )


@router.get("/version-options/{platform}", response_model=Dict[str, Any])
async def get_version_options(platform: str):
    """
    Get available version options for a specific platform
    
    Args:
        platform: Platform name (Java, Node.js, Python, .NET, Go)
    
    Returns:
        Dictionary of version options
    
    Raises:
        HTTPException: 400 for unsupported platform
    """
    try:
        # Normalize platform
        platform_map = {
            "java": LanguageType.JAVA,
            "nodejs": LanguageType.NODEJS,
            "node.js": LanguageType.NODEJS,
            "python": LanguageType.PYTHON,
            "dotnet": LanguageType.DOTNET,
            ".net": LanguageType.DOTNET,
            "go": LanguageType.GO
        }
        
        platform_enum = platform_map.get(platform.lower())
        if not platform_enum:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {platform}"
            )
        
        # Get version options
        version_options = validator.version_options.get(platform_enum, {})
        
        return {
            "platform": platform_enum.value,
            "version_options": {
                key: [opt.dict() for opt in opts]
                for key, opts in version_options.items()
            }
        }
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve version options"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Build Orchestrator Service
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "build-orchestrator",
        "version": "1.0.0"
    }
