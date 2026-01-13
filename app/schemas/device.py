from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DeviceCreate(BaseModel):
    device_id: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=2000)


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    name: str
    location: str | None
    description: str | None
    created_at: datetime

