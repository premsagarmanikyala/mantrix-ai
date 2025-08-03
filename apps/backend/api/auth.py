"""
Authentication API endpoints for user signup, login, and profile management.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from middleware.auth_guard import get_current_user
from core.database import get_db

logger = logging.getLogger(__name__)

# Create router for auth endpoints
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication operations."""
    user_id: str
    email: str
    access_token: str


class UserResponse(BaseModel):
    """Response model for user information."""
    user_id: str
    email: str
    created_at: str = None


@auth_router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Create a new user account.
    
    Args:
        request: Signup request with email and password
        db: Database session
        
    Returns:
        User information with access token
        
    Raises:
        HTTPException: If signup fails or email already exists
    """
    try:
        logger.info(f"Signup attempt for email: {request.email}")
        
        # Create new user
        user_data = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        logger.info(f"User signup successful: {request.email}")
        
        return AuthResponse(
            user_id=user_data["user_id"],
            email=user_data["email"],
            access_token=user_data["access_token"]
        )
        
    except Exception as e:
        logger.error(f"Signup failed for {request.email}: {str(e)}")
        
        # Handle specific error cases
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )


@auth_router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate user and return access token.
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        User information with access token
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Authenticate user
        user_data = AuthService.authenticate_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        if not user_data:
            logger.warning(f"Login failed for {request.email}: Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"User login successful: {request.email}")
        
        return AuthResponse(
            user_id=user_data["user_id"],
            email=user_data["email"],
            access_token=user_data["access_token"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        Current user information
    """
    try:
        logger.debug(f"Getting user info for: {current_user['user_id']}")
        
        return UserResponse(
            user_id=current_user["user_id"],
            email=current_user["email"],
            created_at=current_user.get("created_at")
        )
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@auth_router.get("/health")
async def auth_health_check():
    """Health check endpoint for authentication service."""
    return {
        "status": "healthy",
        "service": "authentication",
        "jwt_enabled": True
    }