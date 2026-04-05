
# Import datetime for log timestamps
from datetime import datetime, timezone
# Import ObjectId and error for MongoDB ID validation
from bson import ObjectId
from bson.errors import InvalidId
# Import FastAPI exception for error handling
from fastapi import HTTPException
# Import database connection utility
from app.db.mongo import get_db
# Import valid log levels
from app.models.log_model import LOG_LEVELS
# Import log schema class
from app.schemas.log_schema import LogIngest



# Helper function to safely parse a string as a MongoDB ObjectId
# Raises HTTP 400 if invalid
def parse_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")



# Ingest a new log entry for a device
def ingest_log(payload: LogIngest):
    # Validate the log level
    if payload.log_level not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid log level")

    # Parse and validate the device ObjectId
    device_object_id = parse_object_id(payload.device_id, "device_id")
    # Check if the device exists
    device = get_db().devices.find_one({"_id": device_object_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Prepare the log document for insertion
    doc = {
        "timestamp": datetime.now(timezone.utc),
        "device_id": device_object_id,
        "log_level": payload.log_level,
        "message": payload.message,
    }

    # Insert the log document into the database
    result = get_db().logs.insert_one(doc)

    # Return the public log info
    return {
        "id": str(result.inserted_id),
        "timestamp": doc["timestamp"],
        "device_id": str(doc["device_id"]),
        "log_level": doc["log_level"],
        "message": doc["message"],
    }



# List all logs in the database, sorted by timestamp (newest first)
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



# Get a single log entry by its ID
def get_log(log_id: str):
    log_object_id = parse_object_id(log_id, "log_id")
    log = get_db().logs.find_one({"_id": log_object_id})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # Return the public log info
    return {
        "id": str(log["_id"]),
        "timestamp": log["timestamp"],
        "device_id": str(log["device_id"]),
        "log_level": log["log_level"],
        "message": log["message"],
    }