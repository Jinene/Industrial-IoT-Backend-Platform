import logging
from typing import Any, Dict

from app.core.database import get_session
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import SensorDataCreate
from app.services.processing_service import normalize_payload, detect_anomalies
from app.services.sync_service import ensure_device_exists

logger = logging.getLogger(__name__)


def ingest_sensor_payload(topic: str, payload: Dict[str, Any]) -> None:
    """
    Called by MQTT consumer. Best effort ingestion:
    - normalize
    - ensure device exists
    - persist
    """
    normalized = normalize_payload(payload)
    normalized = detect_anomalies(normalized)

    device_id = normalized.get("device_id", "")
    if not device_id:
        logger.warning("Dropped message without device_id", extra={"topic": topic})
        return

    ensure_device_exists(device_id)

    with get_session() as session:
        row = SensorData(
            device_id=device_id,
            temperature_c=normalized.get("temperature_c"),
            pressure_bar=normalized.get("pressure_bar"),
            vibration_mm_s=normalized.get("vibration_mm_s"),
            ts=normalized.get("ts"),
            source_topic=topic,
        )
        session.add(row)
        session.flush()

        # Log anomalies for observability
        anomalies = normalized.get("anomalies", [])
        if anomalies:
            logger.warning("Anomalies detected", extra={"device_id": device_id, "anomalies": anomalies})


def ingest_rest_payload(payload: SensorDataCreate) -> SensorData:
    """
    Manual ingestion (REST). Reuses same pipeline logic.
    """
    d = payload.model_dump()
    normalized = normalize_payload(d)
    normalized = detect_anomalies(normalized)

    device_id = normalized.get("device_id", "")
    ensure_device_exists(device_id)

    with get_session() as session:
        row = SensorData(
            device_id=device_id,
            temperature_c=normalized.get("temperature_c"),
            pressure_bar=normalized.get("pressure_bar"),
            vibration_mm_s=normalized.get("vibration_mm_s"),
            ts=normalized.get("ts"),
            source_topic="rest/manual",
        )
        session.add(row)
        session.flush()
        session.refresh(row)
        return row

