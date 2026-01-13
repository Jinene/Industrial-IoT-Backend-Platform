from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select, and_

from app.core.database import get_session
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import SensorDataCreate, SensorDataOut
from app.services.ingestion_service import ingest_rest_payload

router = APIRouter()


@router.post("/data/ingest", response_model=SensorDataOut, status_code=201)
def ingest_data(payload: SensorDataCreate) -> SensorDataOut:
    """
    Manual ingestion endpoint (useful for testing or non-MQTT clients).
    """
    row = ingest_rest_payload(payload)
    return SensorDataOut.model_validate(row)


@router.get("/data", response_model=list[SensorDataOut])
def list_data(
    device_id: Optional[str] = None,
    ts_from: Optional[datetime] = Query(default=None),
    ts_to: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[SensorDataOut]:
    with get_session() as session:
        conditions = []
        if device_id:
            conditions.append(SensorData.device_id == device_id)
        if ts_from:
            conditions.append(SensorData.ts >= ts_from)
        if ts_to:
            conditions.append(SensorData.ts <= ts_to)

        stmt = select(SensorData).order_by(SensorData.ts.desc()).limit(limit)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        rows = session.execute(stmt).scalars().all()
        return [SensorDataOut.model_validate(r) for r in rows]
