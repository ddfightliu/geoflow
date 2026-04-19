"""
MongoDB database configuration using Motor (async).
Compatible with FastAPI async endpoints.
"""

import motor.motor_asyncio
from backend.auth.config import get_settings


settings = get_settings()

# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)
db = client.geoflow  # Explicit database name

users_collection = db.users
transactions_collection = db.transactions


async def init_db():
    """Initialize database indexes."""
    # Users collection indexes
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("provider_id", unique=True, sparse=True)
    
    # Transactions collection indexes
    await transactions_collection.create_index("user_id")
    await transactions_collection.create_index("created_at")
    print("MongoDB indexes created successfully")


async def get_user_by_username(username: str):
    user = await users_collection.find_one({"username": username})
    if user:
        user["id"] = user["_id"]
        user.pop("_id")
    return user


from bson import ObjectId

async def get_user_by_email(email: str):
    user = await users_collection.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id")
    return user


async def create_user(user_data: dict):
    result = await users_collection.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    user_data["id"] = str(result.inserted_id)
    del user_data["_id"]
    return user_data


async def get_user_by_id(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id")
    return user


async def update_user(user_id: str, update_data: dict):
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0


async def get_points_balance(user_id: str):
    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)},
        {"points": 1}
    )
    return user["points"] if user else 0.0


async def update_points(user_id: str, delta: float):
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"points": delta}}
    )
    return result.modified_count > 0


async def create_transaction(tx_data: dict):
    result = await transactions_collection.insert_one(tx_data)
    tx_data["_id"] = result.inserted_id
    tx_data["id"] = str(result.inserted_id)
    del tx_data["_id"]
    return tx_data


async def get_user_transactions(user_id: str, limit: int = 50):
    cursor = transactions_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    transactions = await cursor.to_list(length=limit)
    for tx in transactions:
        tx["id"] = str(tx["_id"])
        del tx["_id"]
    return transactions

