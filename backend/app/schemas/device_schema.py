from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    hostname: str = Field(min_length=2, max_length=100)
    ip_address: str
    type: str = Field(min_length=2, max_length=50)
    location: str = Field(min_length=2, max_length=100)
    status: str


class DeviceUpdate(BaseModel):
    hostname: str | None = None
    ip_address: str | None = None
    type: str | None = None
    location: str | None = None
    status: str | None = None


class DevicePublic(BaseModel):
    id: str
    hostname: str
    ip_address: str
    type: str
    location: str
    status: str
