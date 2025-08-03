"""
User service for handling user-related business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models.database import User
from models.schemas import UserCreate, UserUpdate


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users from database."""
        return db.query(User).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        existing_username = UserService.get_user_by_username(db, user.username)
        if existing_username:
            raise ValueError("User with this username already exists")
        
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user by ID."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user by ID."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True