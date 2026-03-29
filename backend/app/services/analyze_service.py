from fastapi import HTTPException
from bson import ObjectId
from app.db.mongo import get_db
from app.schemas.incident_schema import AIReport
from app.models.incident_model import INCIDENT_SEVERITIES


def analyze_incident(incident_id: str):
    db = get_db()
    incident = db.incidents.find_one({"_id": ObjectId(incident_id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    linked_logs = incident.get("linked_logs", [])
    logs = []
    for log_id in linked_logs:
        log = db.logs.find_one({"_id": ObjectId(log_id)})
        if log:
            logs.append(log)

    if not logs:
        raise HTTPException(status_code=400, detail="No linked logs found for analysis")

    report_data = {
        "summary": "Multiple operational log events suggest a service issue requiring review.",
        "probable_cause": "Possible interface instability or device-side service degradation.",
        "severity": incident["severity"] if incident["severity"] in INCIDENT_SEVERITIES else "Medium",
        "recommended_actions": [
            "Review latest device logs",
            "Verify device reachability and interface status",
            "Escalate if repeated errors continue",
        ],
        "supporting_evidence": [log["message"] for log in logs[:3]],
        "uncertainties": [
            "No external knowledge base connected yet",
            "Root cause not fully confirmed from linked logs alone",
        ],
        "follow_up_questions": [
            "Did the device recently change configuration?",
            "Are similar logs appearing on related devices?",
        ],
    }

    validated = AIReport(**report_data)
    db.incidents.update_one(
        {"_id": ObjectId(incident_id)},
        {"$set": {"ai_report": validated.model_dump()}},
    )

    return validated.model_dump()
