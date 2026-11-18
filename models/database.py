from pymongo import MongoClient
from urllib.parse import quote_plus
import datetime
import os
import subprocess

KEYCHAIN_SERVICE = "werocktracker-mongodb"


def _get_mongo_password(username):
    """
    Read the MongoDB password from the MONGODB_PASSWORD env var,
    falling back to the macOS Keychain (service: werocktracker-mongodb).
    """
    password = os.environ.get("MONGODB_PASSWORD")
    if password:
        return password
    try:
        return subprocess.run(
            ["security", "find-generic-password", "-a", username, "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise RuntimeError(
            "MongoDB password not found. Set MONGODB_PASSWORD or add it to the macOS Keychain: "
            f"security add-generic-password -a {username} -s {KEYCHAIN_SERVICE} -w"
        )


# MongoDB connection setup
def get_database_connection():
    """
    Establishes a connection to MongoDB and returns the database object
    """
    USERNAME = os.environ.get("MONGODB_USERNAME", "felixjdawn")
    PASSWORD = quote_plus(_get_mongo_password(USERNAME))
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@gikoshcluster.r6qxd.mongodb.net/?retryWrites=true&w=majority&appName=gikoshCluster"
    
    client = MongoClient(connection_string)
    db = client.finance_tracker_db
    return db

# Global database instance
_db = None

def initialize_db():
    """
    Initialize the database connection globally
    """
    global _db
    _db = get_database_connection()
    
def get_db():
    """
    Get the database instance
    """
    global _db
    if _db is None:
        _db = get_database_connection()
    return _db

def serialize_date_for_mongo(date_obj):
    """
    Convert date/datetime objects to ISO format strings for MongoDB storage
    
    Args:
        date_obj: A date or datetime object
        
    Returns:
        str: ISO format string representing the date/datetime
    """
    if isinstance(date_obj, datetime.date) and not isinstance(date_obj, datetime.datetime):
        # Convert date to datetime
        date_obj = datetime.datetime.combine(date_obj, datetime.datetime.min.time())
    
    # Return ISO format
    return date_obj.isoformat()
    
def deserialize_mongo_date(date_str):
    """
    Convert ISO format date strings from MongoDB back to datetime objects
    
    Args:
        date_str: An ISO format date string
        
    Returns:
        datetime.datetime: A datetime object
    """
    if isinstance(date_str, str):
        return datetime.datetime.fromisoformat(date_str)
    return date_str  # Already a datetime object