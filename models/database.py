from pymongo import MongoClient
import datetime

# MongoDB connection setup
def get_database_connection():
    """
    Establishes a connection to MongoDB and returns the database object
    """
    USERNAME = "felixjdawn"
    PASSWORD = "MMPvV2w5IJXyY9we"
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