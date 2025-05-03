import datetime
from models.database import get_db, serialize_date_for_mongo, deserialize_mongo_date
import pandas as pd

def add_asset(user_id, name, asset_type, current_value, purchase_value=None, purchase_date=None, location=None, notes=None):
    """
    Add a new asset to the database
    
    Args:
        user_id: The user's ID
        name: Asset name
        asset_type: Type of asset
        current_value: Current value of the asset
        purchase_value: Purchase value of the asset (optional)
        purchase_date: Date of purchase (datetime.date or datetime.datetime)
        location: Asset location (optional)
        notes: Additional notes (optional)
        
    Returns:
        dict: The created asset document
    """
    db = get_db()
    
    if purchase_date is None:
        purchase_date = datetime.datetime.now()
            
    # Get the next ID by counting existing assets for this user
    count = db.assets.count_documents({"user_id": user_id})
    
    # Create asset document
    asset = {
        "id": count + 1,
        "user_id": user_id,
        "name": name,
        "type": asset_type,
        "current_value": float(current_value),
        "purchase_value": float(purchase_value) if purchase_value else 0,
        "purchase_date": serialize_date_for_mongo(purchase_date),
        "location": location,
        "notes": notes,
        "last_updated": serialize_date_for_mongo(datetime.datetime.now())
    }
    
    # Insert into database
    result = db.assets.insert_one(asset)
    
    # Return the asset document with MongoDB ID
    asset["_id"] = result.inserted_id
    return asset

def get_all_assets(user_id):
    """
    Get all assets for a user as a DataFrame
    
    Args:
        user_id: The user's ID
        
    Returns:
        DataFrame: A pandas DataFrame of all assets
    """
    db = get_db()
    assets = list(db.assets.find({"user_id": user_id}))
    
    if not assets:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(assets)
    
    # Convert date strings to datetime objects
    df['purchase_date'] = df['purchase_date'].apply(deserialize_mongo_date)
    df['last_updated'] = df['last_updated'].apply(deserialize_mongo_date)
    
    return df