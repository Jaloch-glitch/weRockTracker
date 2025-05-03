import datetime
from models.database import get_db, serialize_date_for_mongo, deserialize_mongo_date
import pandas as pd

def add_revenue(user_id, amount, description, category, date=None, source=None, notes=None):
    """
    Add a new revenue entry to the database
    
    Args:
        user_id: The user's ID
        amount: Revenue amount
        description: Revenue description
        category: Revenue category
        date: Date of revenue (datetime.date or datetime.datetime)
        source: Source of revenue
        notes: Additional notes
        
    Returns:
        dict: The created revenue document
    """
    db = get_db()
    
    if date is None:
        date = datetime.datetime.now()
            
    # Get the next ID by counting existing revenue entries for this user
    count = db.revenue.count_documents({"user_id": user_id})
    
    # Create revenue document
    revenue = {
        "id": count + 1,
        "user_id": user_id,
        "amount": float(amount),
        "description": description,
        "category": category,
        "date": serialize_date_for_mongo(date),
        "source": source,
        "notes": notes,
        "timestamp": serialize_date_for_mongo(datetime.datetime.now())
    }
    
    # Insert into database
    result = db.revenue.insert_one(revenue)
    
    # Return the revenue document with MongoDB ID
    revenue["_id"] = result.inserted_id
    return revenue

def get_all_revenue(user_id):
    """
    Get all revenue for a user as a DataFrame
    
    Args:
        user_id: The user's ID
        
    Returns:
        DataFrame: A pandas DataFrame of all revenue
    """
    db = get_db()
    revenue = list(db.revenue.find({"user_id": user_id}))
    
    if not revenue:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(revenue)
    
    # Convert date strings to datetime objects
    df['date'] = df['date'].apply(deserialize_mongo_date)
    
    return df