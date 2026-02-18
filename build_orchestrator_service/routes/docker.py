"""
Docker Routes

Endpoints for Dockerfile detection, validation, and generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from models.request_models import (
    DockerOptionsRequest,
    TemplateGenerationRequest,
    FileType,
    VersionConfig
)
from models.response_models import (
    DockerOptionsResponse,
    TemplateGenerationResponse
)
from services.docker_generator import DockerGenerator
from services.suggestion_engine import SuggestionEngine

router = APIRouter(prefix="/api", tags=["docker"])

# Initialize services
docker_generator = DockerGenerator()
suggestion_engine = SuggestionEngine()


@router.post("/docker-options", response_model=DockerOptionsResponse)
async def get_docker_options(request: DockerOptionsRequest):
    """
    Get Dockerfile options for a project
    
    This endpoint checks if a Dockerfile exists, validates it if present,
    and provides options for Dockerfile handling.
    
    **Damage Containment:**
    - Read-only access to project files
    - No Docker commands executed
    - No container operations
    
    Args:
        request: Docker options request with project path and platform
    
    Returns:
        DockerOptionsResponse with Dockerfile status and available options
    
    Raises:
        HTTPException: 400 for invalid input, 500 for internal errors
    """
    try:
        # Check Dockerfile status
        dockerfile_status, dockerfile_path = docker_generator.check_dockerfile_status(
            project_path=request.project_path
        )
        
        # Get available Docker options
        options = docker_generator.get_docker_options(
            platform=request.platform,
            dockerfile_status=dockerfile_status
        )
        
        # Get generation configuration
        generation_config = docker_generator.get_generation_config(
            platform=request.platform
        )
        
        # Generate Dockerfile suggestions
        dockerfile_suggestions = suggestion_engine.generate_dockerfile_suggestions(
            platform=request.platform,
            dockerfile_exists=(dockerfile_status.value == "exists")
        )
        
        return DockerOptionsResponse(
            dockerfile_status=dockerfile_status,
            dockerfile_path=dockerfile_path,
            options=options,
            can_generate=True,
            generation_config=generation_config,
            platform=request.platform.value
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve Docker options"
        )


@router.post("/generate-dockerfile", response_model=TemplateGenerationResponse)
async def generate_dockerfile(request: TemplateGenerationRequest):
    """
    Generate a Dockerfile for a specific platform
    
    This endpoint generates an optimized, production-ready Dockerfile
    based on the platform and configuration.
    
    **Damage Containment:**
    - Template rendering only, no file system writes
    - No Docker build execution
    - No container operations
    - Stateless operation
    
    Args:
        request: Template generation request with platform and config
    
    Returns:
        TemplateGenerationResponse with Dockerfile content
    
    Raises:
        HTTPException: 400 for invalid input, 500 for generation errors
    """
    try:
        # Validate that file_type is Dockerfile
        if request.file_type != FileType.DOCKERFILE:
            raise ValueError("This endpoint is for Dockerfile generation only")
        
        # Generate Dockerfile
        dockerfile_content = docker_generator.generate_dockerfile(
            platform=request.platform,
            config=request.version_config,
            context=request.project_context
        )
        
        # Prepare metadata
        metadata = {
            "platform": request.platform.value,
            "file_type": "Dockerfile",
            "runtime_version": request.version_config.runtime_version,
            "multistage": docker_generator.docker_options.get(
                request.platform, {}
            ).get("supports_multistage", False),
            "generated_at": "2026-02-18T06:58:25Z"
        }
        
        return TemplateGenerationResponse(
            success=True,
            file_type="Dockerfile",
            content=dockerfile_content,
            file_name="Dockerfile",
            metadata=metadata
        )
    
    except ValueError as e:
        return TemplateGenerationResponse(
            success=False,
            file_type="Dockerfile",
            file_name="Dockerfile",
            error=str(e)
        )
    except Exception as e:
        return TemplateGenerationResponse(
            success=False,
            file_type="Dockerfile",
            file_name="Dockerfile",
            error="Dockerfile generation failed due to internal error"
        )


@router.get("/base-images/{platform}")
async def get_base_images(platform: str):
    """
    Get available Docker base images for a platform
    
    Args:
        platform: Platform name (Java, Node.js, Python, .NET, Go)
    
    Returns:
        List of available base images with versions
    
    Raises:
        HTTPException: 400 for unsupported platform
    """
    try:
        from ..models.request_models import LanguageType
        
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
        
        # Get base images
        platform_config = docker_generator.docker_options.get(platform_enum, {})
        base_images = platform_config.get("base_images", [])
        
        return {
            "platform": platform_enum.value,
            "base_images": base_images,
            "default_port": platform_config.get("default_port", 8080),
            "supports_multistage": platform_config.get("supports_multistage", False)
        }
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve base images"
        )
