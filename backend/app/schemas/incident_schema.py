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


class IncidentLinkedLog(BaseModel):
    id: str
    device_id: str
    timestamp: datetime
    log_level: str
    message: str


class IncidentCreate(BaseModel):
    status: str = "open"
    severity: str = "low"
    linked_logs: list[str] = Field(default_factory=list)


class IncidentPublic(BaseModel):
    id: str
    created_by: str
    created_at: datetime
    status: str
    severity: str
    linked_log_ids: list[str] = Field(default_factory=list)
    linked_logs: list[IncidentLinkedLog] = Field(default_factory=list)
    ai_report: AIReport | None = None