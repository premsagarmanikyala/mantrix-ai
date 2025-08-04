#!/usr/bin/env python3
"""
Script to clear existing users and reset the database.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def clear_users():
    """Clear all users from the database."""
    try:
        from core.database import SessionLocal
        from models.database import User
        
        db = SessionLocal()
        
        # Get current users
        users = db.query(User).all()
        user_count = len(users)
        
        if user_count > 0:
            print(f"Found {user_count} existing users:")
            for user in users:
                print(f"  - {user.email} (ID: {user.id})")
            
            # Delete all users
            db.query(User).delete()
            db.commit()
            print(f"\n✅ Deleted {user_count} users from database.")
        else:
            print("No users found in database.")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you're running this from the backend directory.")

if __name__ == "__main__":
    print("🔄 Clearing users from database...")
    clear_users()
    print("✨ Done!")
