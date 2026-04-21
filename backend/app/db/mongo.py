from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import MongoClient

from app.config import settings


client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB]


def get_db():
    return db


def parse_object_id(value: str, field_name: str = "id") -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format",
        )
    return ObjectId(value)