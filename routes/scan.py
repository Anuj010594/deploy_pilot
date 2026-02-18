from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import asyncio

from models.response_models import MultiDetectionResult, ScanRequest
from services.repo_handler import RepoHandler
from services.detector import ProjectDetector

router = APIRouter(prefix="/api", tags=["scan"])

@router.post("/scan", response_model=MultiDetectionResult)
async def scan_repository(
    github_url: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = File(None),
    min_confidence: Optional[float] = Form(0.45)
):
    """
    Scan a repository for platform detection
    
    Args:
        github_url: GitHub repository URL
        zip_file: ZIP file upload
        min_confidence: Minimum confidence threshold (default: 0.45, recommended: 0.45-0.80)
    
    Returns:
        Detection results with confidence scores
    
    Confidence Levels:
        - < 0.45: Unreliable (not recommended for automation)
        - 0.45-0.64: Moderate (proceed with caution)
        - 0.65-0.79: High (safe for most automation)
        - >= 0.80: Very High (fully automated)
    """
    
    if not github_url and not zip_file:
        raise HTTPException(
            status_code=400,
            detail="Either github_url or zip_file must be provided"
        )
    
    # Validate min_confidence
    if min_confidence is not None and not (0.0 <= min_confidence <= 1.0):
        raise HTTPException(
            status_code=400,
            detail="min_confidence must be between 0.0 and 1.0"
        )
    
    repo_handler = RepoHandler()
    detector = ProjectDetector(min_confidence=min_confidence or 0.45)
    repo_path = None
    
    try:
        # Process repository
        if zip_file:
            zip_content = await zip_file.read()
            repo_path = repo_handler.process_repository(zip_file=zip_content)
        else:
            repo_path = repo_handler.process_repository(github_url=github_url)
        
        # Perform detection
        results = detector.scan_project(repo_path)
        
        # Add project_path to results for Build Orchestrator
        results.project_path = repo_path
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
    # Note: We don't cleanup the repo_path here anymore because Build Orchestrator needs to access it
    # Cleanup should be handled separately (e.g., periodic cleanup job or after orchestration completes)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "project-detector"}
