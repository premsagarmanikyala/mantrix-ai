"""
Authentication service for user management and JWT token operations.
"""

import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.config import settings

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Service for user authentication and JWT token management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create a JWT access token for a user."""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    @staticmethod
    def create_user(db: Session, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            db: Database session
            email: User email address
            password: Plain text password
            
        Returns:
            Dictionary with user info and access token
            
        Raises:
            Exception: If user creation fails or email already exists
        """
        try:
            # Check if user already exists
            check_sql = text("SELECT id FROM users WHERE email = :email")
            existing_user = db.execute(check_sql, {"email": email}).fetchone()
            
            if existing_user:
                raise Exception("User with this email already exists")
            
            # Hash password
            hashed_password = AuthService.hash_password(password)
            
            # Insert new user (let database generate ID)
            # Generate username from email (before @ symbol)
            username = email.split('@')[0]
            # Use username as full_name initially
            full_name = username.replace('.', ' ').replace('_', ' ').title()
            
            insert_sql = text("""
                INSERT INTO users (email, username, full_name, password_hash, created_at, is_active)
                VALUES (:email, :username, :full_name, :password_hash, :created_at, :is_active)
                RETURNING id
            """)
            
            result = db.execute(insert_sql, {
                "email": email,
                "username": username,
                "full_name": full_name,
                "password_hash": hashed_password,
                "created_at": datetime.utcnow(),
                "is_active": True
            })
            user_record = result.fetchone()
            user_id = str(user_record[0])  # Convert to string for consistency
            db.commit()
            
            # Create access token
            access_token = AuthService.create_access_token(user_id, email)
            
            logger.info(f"Created new user: {email}")
            
            return {
                "user_id": user_id,
                "email": email,
                "access_token": access_token
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise e
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email address
            password: Plain text password
            
        Returns:
            Dictionary with user info and access token, or None if authentication fails
        """
        try:
            # Get user from database
            select_sql = text("""
                SELECT id, email, password_hash
                FROM users 
                WHERE email = :email
            """)
            
            user_record = db.execute(select_sql, {"email": email}).fetchone()
            
            if not user_record:
                logger.warning(f"User not found: {email}")
                return None
            
            # Verify password
            if not AuthService.verify_password(password, user_record[2]):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            # Create access token
            access_token = AuthService.create_access_token(str(user_record[0]), user_record[1])
            
            logger.info(f"User authenticated successfully: {email}")
            
            return {
                "user_id": str(user_record[0]),
                "email": user_record[1],
                "access_token": access_token
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error authenticating user: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with user info, or None if not found
        """
        try:
            select_sql = text("""
                SELECT id, email, created_at
                FROM users 
                WHERE id = :user_id
            """)
            
            user_record = db.execute(select_sql, {"user_id": user_id}).fetchone()
            
            if not user_record:
                return None
            
            return {
                "user_id": str(user_record[0]),
                "email": user_record[1],
                "created_at": user_record[2].isoformat() if user_record[2] else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None