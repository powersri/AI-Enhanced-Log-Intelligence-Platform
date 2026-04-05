
# Import datetime for timestamp fields
from datetime import datetime
# Import Pydantic base classes for data validation
from pydantic import BaseModel, Field



# Schema for the AI-generated incident analysis report
class AIReport(BaseModel):
    summary: str  # Short summary of the incident
    probable_cause: str  # Most likely cause identified by AI
    severity: str  # Severity level (e.g., low, medium, high, critical)
    recommended_actions: list[str]  # List of recommended actions
    supporting_evidence: list[str]  # Evidence supporting the analysis
    uncertainties: list[str]  # Uncertainties or unknowns in the analysis
    follow_up_questions: list[str]  # Questions for further investigation



# Schema for creating a new incident
class IncidentCreate(BaseModel):
    status: str = "open"  # Initial status (default: open)
    severity: str = "low"  # Initial severity (default: low)



# Public-facing schema for incident data returned by the API
class IncidentPublic(BaseModel):
    id: str  # Unique identifier for the incident
    created_by: str  # User who created the incident
    created_at: datetime  # Timestamp when the incident was created
    status: str  # Current status of the incident
    severity: str  # Current severity of the incident
    linked_logs: list[str]  # List of log IDs linked to this incident
    ai_report: dict | None = None  # Optional AI analysis report (if available)
