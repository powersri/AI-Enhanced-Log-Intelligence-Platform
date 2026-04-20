from datetime import datetime, timezone

from fastapi import HTTPException

from app.db.mongo import get_db, parse_object_id
from app.models.log_model import LOG_LEVELS
from app.schemas.log_schema import LogIngest


def ingest_log(payload: LogIngest):
    db = get_db()

    log_level_value = payload.log_level.lower()
    if log_level_value not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid log level")

    device_object_id = parse_object_id(payload.device_id)
    device = db.devices.find_one({"_id": device_object_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    doc = {
        "timestamp": datetime.now(timezone.utc),
        "device_id": device_object_id,
        "log_level": log_level_value,
        "message": payload.message,
    }

    result = db.logs.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "timestamp": doc["timestamp"],
        "device_id": str(doc["device_id"]),
        "log_level": doc["log_level"],
        "message": doc["message"],
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
    log_object_id = parse_object_id(log_id)
    log = get_db().logs.find_one({"_id": log_object_id})

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    return {
        "id": str(log["_id"]),
        "timestamp": log["timestamp"],
        "device_id": str(log["device_id"]),
        "log_level": log["log_level"],
        "message": log["message"],
    }