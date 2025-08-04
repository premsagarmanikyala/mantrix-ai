"""
Mantrix FastAPI Application
Main entry point for the backend API server.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import api_router, setup_routes
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Mantrix API server...")
    yield
    # Shutdown
    print("👋 Shutting down Mantrix API server...")


app = FastAPI(
    title="Mantrix API",
    description="A comprehensive full-stack application API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up and include API routes
setup_routes()
app.include_router(api_router, prefix="/api")

# Register auth routes separately for proper routing
from api.auth import auth_router
app.include_router(auth_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Welcome to Mantrix API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mantrix-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )