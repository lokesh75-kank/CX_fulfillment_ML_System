"""
FastAPI main application

Main entry point for the CX-Fulfillment Agent API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import incidents, rca, recommendations, metrics

app = FastAPI(
    title="CX-Fulfillment Agent API",
    description="API for CX-Fulfillment Agent - Incident detection and root cause analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(rca.router, prefix="/api/rca", tags=["rca"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CX-Fulfillment Agent API",
        "version": "1.0.0",
        "endpoints": {
            "incidents": "/api/incidents",
            "rca": "/api/rca",
            "recommendations": "/api/recommendations",
            "metrics": "/api/metrics"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

