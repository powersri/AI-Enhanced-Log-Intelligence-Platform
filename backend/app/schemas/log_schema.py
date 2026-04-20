from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LogIngest(BaseModel):
    device_id: str
    log_level: str
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.lower()
        allowed = {"info", "warning", "error", "critical"}
        if normalized not in allowed:
            raise ValueError("Invalid log level")
        return normalized


class LogPublic(BaseModel):
    id: str
    timestamp: datetime
    device_id: str
    log_level: str
    message: str