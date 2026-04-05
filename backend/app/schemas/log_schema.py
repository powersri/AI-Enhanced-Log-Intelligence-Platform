
# Import datetime for log timestamps
from datetime import datetime
# Import Pydantic base classes for data validation
from pydantic import BaseModel, Field



# Schema for ingesting a new log entry
class LogIngest(BaseModel):
    device_id: str  # ID of the device that generated the log
    log_level: str = Field(pattern="^(info|warning|error|critical)$")  # Log severity level (validated)
    message: str = Field(min_length=1, max_length=2000)  # Log message content (1-2000 chars)



# Public-facing schema for log data returned by the API
class LogPublic(BaseModel):
    id: str  # Unique identifier for the log entry
    timestamp: datetime  # Time when the log was created
    device_id: str  # ID of the device that generated the log
    log_level: str  # Log severity level
    message: str  # Log message content
