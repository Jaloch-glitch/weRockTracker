import datetime
from models.database import get_db, serialize_date_for_mongo, deserialize_mongo_date

def initialize_cash_position(user_id):
    """
    Initialize cash position if it doesn't exist
    
    Args:
        user_id: The user's ID
    """
    db = get_db()
    cash = db.cash.find_one({"user_id": user_id})
    
    if not cash:
        cash_data = {
            "user_id": user_id,
            "in_hand": 0,
            "in_bank": 0,
            "last_updated": serialize_date_for_mongo(datetime.datetime.now())
        }
        db.cash.insert_one(cash_data)

def update_cash(user_id, cash_in_hand, cash_in_bank):
    """
    Update cash positions
    
    Args:
        user_id: The user's ID
        cash_in_hand: Cash in hand
        cash_in_bank: Cash in bank
        
    Returns:
        dict: The updated cash document
    """
    db = get_db()
    now = datetime.datetime.now()
    
    # Update document
    result = db.cash.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "in_hand": float(cash_in_hand),
                "in_bank": float(cash_in_bank),
                "last_updated": serialize_date_for_mongo(now)
            }
        },
        upsert=True
    )
    
    # Return updated document
    return get_cash_position(user_id)

def get_cash_position(user_id):
    """
    Get current cash position
    
    Args:
        user_id: The user's ID
        
    Returns:
        dict: The cash document
    """
    db = get_db()
    cash = db.cash.find_one({"user_id": user_id})
    
    if not cash:
        return {
            "in_hand": 0,
            "in_bank": 0,
            "last_updated": datetime.datetime.now().strftime('%Y-%m-%d')
        }
    
    # Format date for display
    if isinstance(cash["last_updated"], str):
        cash["last_updated"] = deserialize_mongo_date(cash["last_updated"]).strftime('%Y-%m-%d')
    elif isinstance(cash["last_updated"], datetime.datetime):
        cash["last_updated"] = cash["last_updated"].strftime('%Y-%m-%d')
            
    return cash