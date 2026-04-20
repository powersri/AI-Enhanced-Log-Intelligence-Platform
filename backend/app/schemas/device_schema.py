from pydantic import BaseModel, Field
from pydantic.networks import IPv4Address


class DeviceCreate(BaseModel):
    hostname: str = Field(min_length=2, max_length=100)
    ip_address: IPv4Address
    type: str = Field(min_length=2, max_length=50)
    location: str = Field(min_length=2, max_length=100)
    status: str


class DeviceUpdate(BaseModel):
    hostname: str | None = Field(default=None, min_length=2, max_length=100)
    ip_address: IPv4Address | None = None
    type: str | None = Field(default=None, min_length=2, max_length=50)
    location: str | None = Field(default=None, min_length=2, max_length=100)
    status: str | None = None


class DevicePublic(BaseModel):
    id: str
    hostname: str
    ip_address: str
    type: str
    location: str
    status: str