
# Import Any type for flexible data field
from typing import Any
# Import Pydantic base class for data validation
from pydantic import BaseModel


# Standard API response schema for consistent responses
class APIResponse(BaseModel):
    success: bool  # Indicates if the API call was successful
    message: str   # Human-readable message for the response
    data: Any | None = None  # Optional data payload (can be any type or None)
