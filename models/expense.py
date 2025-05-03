import datetime
from models.database import get_db, serialize_date_for_mongo, deserialize_mongo_date
import pandas as pd

def add_expense(user_id, amount, description, category, date=None, payment_method=None, notes=None):
    """
    Add a new expense entry to the database
    
    Args:
        user_id: The user's ID
        amount: Expense amount
        description: Expense description
        category: Expense category
        date: Date of expense (datetime.date or datetime.datetime)
        payment_method: Method of payment
        notes: Additional notes
        
    Returns:
        dict: The created expense document
    """
    db = get_db()
    
    if date is None:
        date = datetime.datetime.now()
            
    # Get the next ID by counting existing expenses for this user
    count = db.expenses.count_documents({"user_id": user_id})
    
    # Create expense document
    expense = {
        "id": count + 1,
        "user_id": user_id,
        "amount": float(amount),
        "description": description,
        "category": category,
        "date": serialize_date_for_mongo(date),
        "payment_method": payment_method,
        "notes": notes,
        "timestamp": serialize_date_for_mongo(datetime.datetime.now())
    }
    
    # Insert into database
    result = db.expenses.insert_one(expense)
    
    # Return the expense document with MongoDB ID
    expense["_id"] = result.inserted_id
    return expense

def get_all_expenses(user_id):
    """
    Get all expenses for a user as a DataFrame
    
    Args:
        user_id: The user's ID
        
    Returns:
        DataFrame: A pandas DataFrame of all expenses
    """
    db = get_db()
    expenses = list(db.expenses.find({"user_id": user_id}))
    
    if not expenses:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    
    # Convert date strings to datetime objects
    df['date'] = df['date'].apply(deserialize_mongo_date)
    
    return df