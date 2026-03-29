from datetime import datetime
from pydantic import BaseModel, Field


class LogIngest(BaseModel):
    timestamp: datetime
    device_id: str
    log_level: str
    message: str = Field(min_length=1, max_length=2000)


class LogPublic(BaseModel):
    id: str
    timestamp: datetime
    device_id: str
    log_level: str
    message: str
