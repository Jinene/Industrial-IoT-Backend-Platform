
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.database import get_session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceOut

router = APIRouter()


@router.post("/devices", response_model=DeviceOut, status_code=201)
def create_device(payload: DeviceCreate) -> DeviceOut:
    with get_session() as session:
        existing = session.execute(select(Device).where(Device.device_id == payload.device_id)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="device_id already exists")

        device = Device(
            device_id=payload.device_id,
            name=payload.name,
            location=payload.location,
            description=payload.description,
        )
        session.add(device)
        session.flush()  # assign PK
        return DeviceOut.model_validate(device)


@router.get("/devices", response_model=list[DeviceOut])
def list_devices() -> list[DeviceOut]:
    with get_session() as session:
        rows = session.execute(select(Device).order_by(Device.created_at.desc())).scalars().all()
        return [DeviceOut.model_validate(d) for d in rows]


@router.get("/devices/{device_id}", response_model=DeviceOut)
def get_device(device_id: str) -> DeviceOut:
    with get_session() as session:
        device = session.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return DeviceOut.model_validate(device)
