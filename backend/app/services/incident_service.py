from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import get_db, parse_object_id
from app.models.incident_model import INCIDENT_SEVERITIES, INCIDENT_STATUSES
from app.schemas.incident_schema import IncidentCreate


def invalidate_incident_analysis_cache(incident_object_id: ObjectId):
    db = get_db()
    db.incidents.update_one(
        {"_id": incident_object_id},
        {
            "$set": {
                "ai_report": None
            },
            "$unset": {
                "analysis_fingerprint": "",
                "analysis_generated_at": "",
                "analysis_source": "",
                "retrieved_doc_titles": ""
            }
        }
    )


def _serialize_linked_logs(linked_log_ids: list[str]) -> list[dict]:
    db = get_db()
    expanded_logs = []

    for log_id in linked_log_ids:
        try:
            log_object_id = parse_object_id(log_id, "log_id")
        except HTTPException:
            continue

        log = db.logs.find_one({"_id": log_object_id})
        if not log:
            continue

        expanded_logs.append({
            "id": str(log["_id"]),
            "device_id": str(log["device_id"]),
            "timestamp": log["timestamp"],
            "log_level": log["log_level"],
            "message": log["message"],
        })

    return expanded_logs


def _serialize_incident(incident: dict) -> dict:
    linked_log_ids = incident.get("linked_logs", [])

    return {
        "id": str(incident["_id"]),
        "created_by": incident["created_by"],
        "created_at": incident["created_at"],
        "status": incident["status"],
        "severity": incident["severity"],
        "linked_log_ids": linked_log_ids,
        "linked_logs": _serialize_linked_logs(linked_log_ids),
        "ai_report": incident.get("ai_report"),
    }


def create_incident(payload: IncidentCreate, current_user: dict):
    db = get_db()

    status_value = payload.status.lower()
    severity_value = payload.severity.lower()

    if status_value not in INCIDENT_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid incident status")

    if severity_value not in INCIDENT_SEVERITIES:
        raise HTTPException(status_code=400, detail="Invalid incident severity")

    linked_log_ids = []
    for log_id in payload.linked_logs or []:
        log_object_id = parse_object_id(log_id, "log_id")
        log = db.logs.find_one({"_id": log_object_id})
        if not log:
            raise HTTPException(status_code=404, detail=f"Log not found: {log_id}")
        linked_log_ids.append(log_id)

    doc = {
        "created_by": current_user["id"],
        "created_at": datetime.now(timezone.utc),
        "status": status_value,
        "severity": severity_value,
        "linked_logs": linked_log_ids,
        "ai_report": None,
    }

    result = db.incidents.insert_one(doc)
    incident = db.incidents.find_one({"_id": result.inserted_id})

    return _serialize_incident(incident)


def list_incidents():
    items = []
    for incident in get_db().incidents.find().sort("created_at", -1):
        items.append(_serialize_incident(incident))
    return items


def get_incident(incident_id: str):
    incident_object_id = parse_object_id(incident_id, "incident_id")
    incident = get_db().incidents.find_one({"_id": incident_object_id})

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return _serialize_incident(incident)


def link_log_to_incident(incident_id: str, log_id: str):
    db = get_db()

    incident_object_id = parse_object_id(incident_id, "incident_id")
    log_object_id = parse_object_id(log_id, "log_id")

    incident = db.incidents.find_one({"_id": incident_object_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    log = db.logs.find_one({"_id": log_object_id})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    update_result = db.incidents.update_one(
        {
            "_id": incident_object_id,
            "linked_logs": {"$ne": log_id}
        },
        {
            "$addToSet": {"linked_logs": log_id}
        },
    )

    if update_result.modified_count > 0:
        invalidate_incident_analysis_cache(incident_object_id)

    return get_incident(incident_id)