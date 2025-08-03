"""
Authentication middleware for protecting API endpoints.
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from core.database import get_db

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class AuthGuard:
    """Authentication guard for protecting endpoints."""
    
    @staticmethod
    def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> str:
        """
        Extract and validate user ID from JWT token.
        
        Args:
            credentials: HTTP Bearer token credentials
            db: Database session
            
        Returns:
            User ID from validated token
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            # Extract token
            token = credentials.credentials
            
            # Decode token
            payload = AuthService.decode_access_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verify user still exists
            user = AuthService.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            logger.debug(f"Authenticated user: {user_id}")
            return user_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Get complete current user information from JWT token.
        
        Args:
            credentials: HTTP Bearer token credentials
            db: Database session
            
        Returns:
            Dictionary with user information
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            # Get user ID
            user_id = AuthGuard.get_current_user_id(credentials, db)
            
            # Get full user information
            user = AuthService.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user information",
                headers={"WWW-Authenticate": "Bearer"}
            )


# Convenience functions for dependency injection
def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """Dependency to get current user ID."""
    return AuthGuard.get_current_user_id(credentials, db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency to get current user information."""
    return AuthGuard.get_current_user(credentials, db)