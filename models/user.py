import hashlib
import uuid
import datetime
import streamlit as st
from models.database import get_db

def hash_password(password):
    """
    Create a SHA-256 hash of the password
    
    Args:
        password: The plaintext password
        
    Returns:
        str: The hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_credentials(email, password):
    """
    Check if the user credentials are valid
    
    Args:
        email: The user's email
        password: The user's plaintext password
        
    Returns:
        tuple: (valid, user) where valid is a boolean and user is the user document
    """
    db = get_db()
    user = db.users.find_one({"email": email})
    
    if user and user["password_hash"] == hash_password(password):
        return True, user
    return False, None

def initialize_users():
    """
    Initialize the users if they don't exist
    """
    db = get_db()
    
    # Check if users already exist
    existing_users = list(db.users.find({}))
    
    if not existing_users:
        # Create default users
        users = [
            {
                "user_id": str(uuid.uuid4()),
                "email": "brianGuru@werock.com",
                "password_hash": hash_password("password123"),  # Replace with a secure password
                "name": "Brian Guru",
                "created_at": datetime.datetime.now().isoformat()  # Store as ISO string
            },
            {
                "user_id": str(uuid.uuid4()),
                "email": "felix@werock.com",
                "password_hash": hash_password("password456"),  # Replace with a secure password
                "name": "Felix",
                "created_at": datetime.datetime.now().isoformat()  # Store as ISO string
            },
            {
                "user_id": str(uuid.uuid4()),
                "email": "angie@werock.com",
                "password_hash": hash_password("password456"),  # Replace with a secure password
                "name": "Angie",
                "created_at": datetime.datetime.now().isoformat()  # Store as ISO string
            }
        ]
        
        # Insert users
        db.users.insert_many(users)
        st.success("Default users initialized")