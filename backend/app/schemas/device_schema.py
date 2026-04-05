from pydantic import BaseModel, Field  # Import Pydantic base classes for data validation
from pydantic.networks import IPv4Address  # Import IPv4Address type for IP validation

class DeviceCreate(BaseModel):
    # Hostname of the device (required, 2-100 chars)
    hostname: str = Field(min_length=2, max_length=100)
    # IPv4 address of the device (validated as IPv4)
    ip_address: IPv4Address
    # Type of device (e.g., router, switch)
    type: str = Field(min_length=2, max_length=50)
    # Physical or logical location of the device
    location: str = Field(min_length=2, max_length=100)
    # Status of the device (e.g., up, down)
    status: str


class DeviceUpdate(BaseModel):
    # Optional fields for updating a device; all are nullable
    hostname: str | None = None
    ip_address: str | None = None
    type: str | None = None
    location: str | None = None
    status: str | None = None


class DevicePublic(BaseModel):
    # Public-facing device model (as returned in API responses)
    id: str  # Device unique identifier (as string)
    hostname: str  # Hostname of the device
    ip_address: str  # IP address as string
    type: str  # Device type
    location: str  # Device location
    status: str  # Device status
