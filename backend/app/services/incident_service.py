from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException
from app.db.mongo import get_db
from app.models.incident_model import INCIDENT_STATUSES, INCIDENT_SEVERITIES
from app.schemas.incident_schema import IncidentCreate


def create_incident(payload: IncidentCreate, current_user: dict):
    if payload.status not in INCIDENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid incident status")
    if payload.severity not in INCIDENT_SEVERITIES:
        raise HTTPException(status_code=400, detail="Invalid incident severity")

    doc = {
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc),
        "status": payload.status,
        "severity": payload.severity,
        "linked_logs": [],
        "ai_report": None,
    }
    result = get_db().incidents.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


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


def get_incident(incident_id: str):
    incident = get_db().incidents.find_one({"_id": ObjectId(incident_id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "id": str(incident["_id"]),
        "created_by": incident["created_by"],
        "created_at": incident["created_at"],
        "status": incident["status"],
        "severity": incident["severity"],
        "linked_logs": incident.get("linked_logs", []),
        "ai_report": incident.get("ai_report"),
    }


def link_log_to_incident(incident_id: str, log_id: str):
    db = get_db()
    incident = db.incidents.find_one({"_id": ObjectId(incident_id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    log = db.logs.find_one({"_id": ObjectId(log_id)})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    db.incidents.update_one(
        {"_id": ObjectId(incident_id)},
        {"$addToSet": {"linked_logs": log_id}},
    )
    return get_incident(incident_id)
