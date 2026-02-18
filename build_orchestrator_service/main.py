"""
Build Orchestrator Service

A microservice responsible for:
- Validation of build files for all supported platforms
- Generation of missing configuration files
- Dockerfile assistance and generation
- Stateless orchestration intelligence

DAMAGE CONTAINMENT:
- Read-only access to project files
- No code execution
- No build commands
- No Docker operations
- Path traversal protection
- Isolated failure domain
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from routes.validation import router as validation_router
from routes.docker import router as docker_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Build Orchestrator Service",
    description="""
    Microservice for build orchestration, validation, and Dockerfile generation.
    
    ## Features
    
    * **Platform Validation**: Validate build files for Java, Node.js, Python, .NET, and Go
    * **Template Generation**: Auto-generate build configuration files
    * **Dockerfile Management**: Detect, validate, and generate Dockerfiles
    * **Version Configuration**: Select runtime versions and dependencies
    * **Suggestion Engine**: Intelligent recommendations for missing files
    
    ## Security & Isolation
    
    * Read-only access to project files
    * No code execution or build commands
    * Path traversal protection
    * Stateless operations
    * Isolated from Detection Service
    
    ## Supported Platforms
    
    * ☕ Java (Maven, Gradle)
    * 🟨 Node.js (npm, yarn, pnpm)
    * 🐍 Python (pip, poetry, pipenv)
    * 🟪 .NET (dotnet)
    * 🐹 Go (go modules)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for graceful error handling
    Ensures service doesn't crash on unexpected errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "The Build Orchestrator Service encountered an error",
            "service": "build-orchestrator"
        }
    )

# Include routers
app.include_router(validation_router)
app.include_router(docker_router)

@app.get("/")
async def root():
    """
    Root endpoint with service information
    """
    return {
        "service": "Build Orchestrator Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Microservice for build validation and orchestration",
        "architecture": "microservice",
        "isolation": {
            "damage_containment": True,
            "read_only_operations": True,
            "stateless": True,
            "no_code_execution": True
        },
        "endpoints": {
            "validation": "/api/validate",
            "template_generation": "/api/generate-template",
            "docker_options": "/api/docker-options",
            "dockerfile_generation": "/api/generate-dockerfile",
            "version_options": "/api/version-options/{platform}",
            "base_images": "/api/base-images/{platform}",
            "health": "/api/health",
            "documentation": "/docs"
        },
        "supported_platforms": [
            "Java",
            "Node.js",
            "Python",
            ".NET",
            "Go"
        ]
    }

@app.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint (can be extended with Prometheus metrics)
    """
    return {
        "service": "build-orchestrator",
        "uptime": "operational",
        "platforms_supported": 5,
        "endpoints_active": 7,
        "status": "healthy"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    logger.info("Build Orchestrator Service starting up...")
    logger.info("Service isolation: ENABLED")
    logger.info("Code execution: DISABLED")
    logger.info("Read-only mode: ENABLED")
    logger.info("Supported platforms: Java, Node.js, Python, .NET, Go")
    logger.info("Build Orchestrator Service is ready")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info("Build Orchestrator Service shutting down...")
    logger.info("Build Orchestrator Service stopped")

if __name__ == "__main__":
    import uvicorn
    
    # Run the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port from Detection Service (8000)
        log_level="info"
    )
