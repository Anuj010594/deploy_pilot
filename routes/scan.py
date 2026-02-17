from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import asyncio

from ..models.response_models import MultiDetectionResult, ScanRequest
from ..services.repo_handler import RepoHandler
from ..services.detector import ProjectDetector

router = APIRouter(prefix="/api", tags=["scan"])

@router.post("/scan", response_model=MultiDetectionResult)
async def scan_repository(
    github_url: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = File(None)
):
    """
    Scan a repository for platform detection
    
    Args:
        github_url: GitHub repository URL
        zip_file: ZIP file upload
    
    Returns:
        Detection results with confidence scores
    """
    
    if not github_url and not zip_file:
        raise HTTPException(
            status_code=400,
            detail="Either github_url or zip_file must be provided"
        )
    
    repo_handler = RepoHandler()
    detector = ProjectDetector()
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
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        # Cleanup
        if repo_path:
            repo_handler.cleanup_directory(repo_path)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "project-detector"}
