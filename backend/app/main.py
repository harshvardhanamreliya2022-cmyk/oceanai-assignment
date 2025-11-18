"""
FastAPI main application for QA Agent.

This module initializes the FastAPI application with CORS middleware,
health check endpoint, and API routers.
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI(
    title="QA Agent API",
    version="1.0.0",
    description="Autonomous QA Agent for Test Case and Script Generation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default port
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # TODO: Initialize ChromaDB
    # TODO: Load embedding model
    # TODO: Setup logging
    print("🚀 QA Agent API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("👋 QA Agent API shutting down...")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "QA Agent API"
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API welcome message and available endpoints
    """
    return {
        "message": "Welcome to QA Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# API Routes will be added here
# TODO: Add document upload routes
# TODO: Add knowledge base routes
# TODO: Add test case generation routes
# TODO: Add Selenium script generation routes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
