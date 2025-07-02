from motor.motor_asyncio import AsyncIOMotorClient
from oxeign.config import MONGO_URI
import os
from pymongo.errors import ConfigurationError

DEFAULT_DB_NAME = os.getenv("MONGO_DB_NAME", "oxeign")

client = AsyncIOMotorClient(MONGO_URI)
try:
    db = client.get_default_database()
except ConfigurationError:
    db = client[DEFAULT_DB_NAME]
