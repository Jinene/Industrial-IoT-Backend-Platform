from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SensorDataCreate(BaseModel):
    device_id: str = Field(..., min_length=2, max_length=64)
    temperature_c: float | None = None
    pressure_bar: float | None = None
    vibration_mm_s: float | None = None
    ts: datetime


class SensorDataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    temperature_c: float | None
    pressure_bar: float | None
    vibration_mm_s: float | None
    ts: datetime
    ingested_at: datetime
    source_topic: str | None

