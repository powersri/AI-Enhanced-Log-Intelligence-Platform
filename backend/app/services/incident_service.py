
# Import datetime for timestamps
from datetime import datetime, timezone
# Import ObjectId and error for MongoDB ID validation
from bson import ObjectId
from bson.errors import InvalidId
# Import FastAPI exception for error handling
from fastapi import HTTPException
# Import database connection utility
from app.db.mongo import get_db
# Import valid incident statuses and severities
from app.models.incident_model import INCIDENT_STATUSES, INCIDENT_SEVERITIES
# Import incident schema class
from app.schemas.incident_schema import IncidentCreate



# Helper function to safely parse a string as a MongoDB ObjectId
# Raises HTTP 400 if invalid
def parse_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")



# Create a new incident in the database
def create_incident(payload: IncidentCreate, current_user: dict):
    # Validate the incident status
    if payload.status not in INCIDENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid incident status")

    # Validate the incident severity
    if payload.severity not in INCIDENT_SEVERITIES:
        raise HTTPException(status_code=400, detail="Invalid incident severity")

    # Prepare the incident document for insertion
    doc = {
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc),
        "status": payload.status,
        "severity": payload.severity,
        "linked_logs": [],
        "ai_report": None,
    }

    # Insert the incident document into the database
    result = get_db().incidents.insert_one(doc)

    # Return the public incident info
    return {
        "id": str(result.inserted_id),
        "created_by": doc["created_by"],
        "created_at": doc["created_at"],
        "status": doc["status"],
        "severity": doc["severity"],
        "linked_logs": doc["linked_logs"],
        "ai_report": doc["ai_report"],
    }



# List all incidents in the database, sorted by creation time (newest first)
def list_incidents():
    items = []
    for incident in get_db().incidents.find().sort("created_at", -1):
        items.append({
            "id": str(incident["_id"]),
            "created_by": incident["created_by"],
            "created_at": incident["created_at"],
            "status": incident["status"],
            "severity": incident["severity"],
            "linked_logs": incident.get("linked_logs", []),
            "ai_report": incident.get("ai_report"),
        })
    return items



# Get a single incident by its ID
def get_incident(incident_id: str):
    incident_object_id = parse_object_id(incident_id, "incident_id")
    incident = get_db().incidents.find_one({"_id": incident_object_id})

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Return the public incident info
    return {
        "id": str(incident["_id"]),
        "created_by": incident["created_by"],
        "created_at": incident["created_at"],
        "status": incident["status"],
        "severity": incident["severity"],
        "linked_logs": incident.get("linked_logs", []),
        "ai_report": incident.get("ai_report"),
    }



# Link a log entry to an incident by their IDs
def link_log_to_incident(incident_id: str, log_id: str):
    db = get_db()

    # Parse and validate the incident and log ObjectIds
    incident_object_id = parse_object_id(incident_id, "incident_id")
    log_object_id = parse_object_id(log_id, "log_id")

    # Check if the incident exists
    incident = db.incidents.find_one({"_id": incident_object_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Check if the log exists
    log = db.logs.find_one({"_id": log_object_id})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    # Add the log ID to the incident's linked_logs array (no duplicates)
    db.incidents.update_one(
        {"_id": incident_object_id},
        {"$addToSet": {"linked_logs": log_id}},
    )

    # Return the updated incident info
    return get_incident(incident_id)