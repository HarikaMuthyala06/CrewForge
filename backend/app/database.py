# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# This variable holds the database connection
client = None
db = None

async def connect_db():
    """Called when FastAPI app starts — opens MongoDB connection"""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.DB_NAME}")

async def close_db():
    """Called when FastAPI app stops — closes MongoDB connection"""
    global client
    if client:
        client.close()
        print("🔴 MongoDB connection closed")

def get_db():
    """Returns the database instance — used in route handlers"""
    return db