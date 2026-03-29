from bson import ObjectId
from fastapi import HTTPException
from app.db.mongo import get_db
from app.models.log_model import LOG_LEVELS
from app.schemas.log_schema import LogIngest


def ingest_log(payload: LogIngest):
    if payload.log_level not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid log level")

    device = get_db().devices.find_one({"_id": ObjectId(payload.device_id)})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    doc = payload.model_dump()
    doc["device_id"] = ObjectId(payload.device_id)
    result = get_db().logs.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "timestamp": payload.timestamp,
        "device_id": payload.device_id,
        "log_level": payload.log_level,
        "message": payload.message,
    }


def list_logs():
    items = []
    for log in get_db().logs.find().sort("timestamp", -1):
        items.append({
            "id": str(log["_id"]),
            "timestamp": log["timestamp"],
            "device_id": str(log["device_id"]),
            "log_level": log["log_level"],
            "message": log["message"],
        })
    return items


def get_log(log_id: str):
    log = get_db().logs.find_one({"_id": ObjectId(log_id)})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return {
        "id": str(log["_id"]),
        "timestamp": log["timestamp"],
        "device_id": str(log["device_id"]),
        "log_level": log["log_level"],
        "message": log["message"],
    }
