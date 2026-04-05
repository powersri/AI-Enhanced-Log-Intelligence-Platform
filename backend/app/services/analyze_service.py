
# Import FastAPI exception for error handling
from fastapi import HTTPException
# Import ObjectId and error for MongoDB ID validation
from bson import ObjectId
from bson.errors import InvalidId
# Import database connection utility
from app.db.mongo import get_db
# Import AIReport schema for validation
from app.schemas.incident_schema import AIReport
# Import valid incident severities
from app.models.incident_model import INCIDENT_SEVERITIES



# Helper function to safely parse a string as a MongoDB ObjectId
# Raises HTTP 400 if invalid
def parse_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")



# Analyze an incident by generating a placeholder AI report based on linked logs
def analyze_incident(incident_id: str):
    db = get_db()  # Get MongoDB database connection

    # Parse and validate the incident ObjectId
    incident_object_id = parse_object_id(incident_id, "incident_id")
    # Retrieve the incident document from the database
    incident = db.incidents.find_one({"_id": incident_object_id})
    if not incident:
        # If not found, raise 404 error
        raise HTTPException(status_code=404, detail="Incident not found")

    # Get the list of linked log IDs from the incident
    linked_logs = incident.get("linked_logs", [])
    logs = []  # Will hold the actual log documents

    # For each linked log ID, try to fetch the log document
    for log_id in linked_logs:
        try:
            log_object_id = parse_object_id(log_id, "log_id")
            log = db.logs.find_one({"_id": log_object_id})
            if log:
                logs.append(log)
        except HTTPException:
            # Skip invalid log IDs
            continue

    # If no logs are linked, cannot analyze
    if not logs:
        raise HTTPException(status_code=400, detail="No linked logs found for analysis")

    # Prepare the AI report data (placeholder logic)
    report_data = {
        "summary": "Multiple operational log events suggest a service issue requiring review.",
        "probable_cause": "Possible interface instability or device-side service degradation.",
        # Use the incident's severity if valid, else default to 'medium'
        "severity": incident["severity"] if incident["severity"] in INCIDENT_SEVERITIES else "medium",
        "recommended_actions": [
            "Review latest device logs",
            "Verify device reachability and interface status",
            "Escalate if repeated errors continue",
        ],
        # Use up to 3 log messages as supporting evidence
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

    # Validate and structure the report using the AIReport schema
    validated = AIReport(**report_data)

    # Save the AI report to the incident document in the database
    db.incidents.update_one(
        {"_id": incident_object_id},
        {"$set": {"ai_report": validated.model_dump()}},
    )

    # Return the AI report as a dictionary
    return validated.model_dump()