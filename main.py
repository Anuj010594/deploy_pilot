from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scan import router as scan_router

app = FastAPI(
    title="Project Detection API",
    description="MVP backend service for detecting project platforms and build tools",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scan_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Project Detection API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/api/scan",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
