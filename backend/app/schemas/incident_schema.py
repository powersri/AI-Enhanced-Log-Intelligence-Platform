from datetime import datetime
from pydantic import BaseModel, Field


class AIReport(BaseModel):
    summary: str
    probable_cause: str
    severity: str
    recommended_actions: list[str]
    supporting_evidence: list[str]
    uncertainties: list[str]
    follow_up_questions: list[str]


class IncidentCreate(BaseModel):
    status: str = "open"
    severity: str = "Low"


class IncidentPublic(BaseModel):
    id: str
    created_by: str
    created_at: datetime
    status: str
    severity: str
    linked_logs: list[str]
    ai_report: dict | None = None
