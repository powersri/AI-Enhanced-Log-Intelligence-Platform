from pymongo import MongoClient
from app.config import settings

_client = MongoClient(settings.MONGODB_URL)
_db = _client[settings.MONGODB_DB]


def get_db():
    return _db