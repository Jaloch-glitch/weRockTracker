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

def change_password(user_id, current_password, new_password):
    """
    Change a user's password
    
    Args:
        user_id: The user's ID
        current_password: The current password
        new_password: The new password
        
    Returns:
        bool: True if password was changed successfully, False otherwise
    """
    db = get_db()
    user = db.users.find_one({"user_id": user_id})
    
    if not user:
        return False, "User not found"
    
    if user["password_hash"] != hash_password(current_password):
        return False, "Current password is incorrect"
    
    # Update the password
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"password_hash": hash_password(new_password)}}
    )
    
    return True, "Password changed successfully"

def get_all_users():
    """
    Get all users
    
    Returns:
        list: List of all users
    """
    db = get_db()
    users = list(db.users.find({}, {"password_hash": 0}))  # Exclude password hash
    return users

def add_user(email, name, password):
    """
    Add a new user
    
    Args:
        email: The user's email
        name: The user's name
        password: The user's password
        
    Returns:
        tuple: (success, message) where success is a boolean
    """
    db = get_db()
    
    # Check if user already exists
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return False, "User with this email already exists"
    
    # Create new user
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Insert user
    db.users.insert_one(user)
    return True, "User added successfully"

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
                "password_hash": hash_password("password123"),
                "name": "Brian Guru",
                "created_at": datetime.datetime.now().isoformat()
            },
            {
                "user_id": str(uuid.uuid4()),
                "email": "felix@werock.com",
                "password_hash": hash_password("password456"),
                "name": "Felix",
                "created_at": datetime.datetime.now().isoformat()
            },
            {
                "user_id": str(uuid.uuid4()),
                "email": "angie@werock.com",
                "password_hash": hash_password("password789"),
                "name": "Angie",
                "created_at": datetime.datetime.now().isoformat()
            }
        ]
        
        # Insert users
        db.users.insert_many(users)
        st.success("Default users initialized")