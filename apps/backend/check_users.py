#!/usr/bin/env python3
"""
Quick script to check existing users in the database.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.database import User

def check_users():
    """Check existing users in the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users in the database:")
        
        if users:
            for user in users:
                print(f"  - Email: {user.email}")
                print(f"    ID: {user.id}")
                print(f"    Username: {user.username}")
                print(f"    Created: {user.created_at}")
                print(f"    Active: {user.is_active}")
                print()
        else:
            print("  No users found in the database.")
            
    except Exception as e:
        print(f"Error checking users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
