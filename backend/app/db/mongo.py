import os

from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "netops_copilot")

_client = MongoClient(MONGODB_URL)
_db = _client[MONGODB_DB]


def get_db():
    return _db
