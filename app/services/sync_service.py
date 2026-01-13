import logging
from sqlalchemy import select

from app.core.database import get_session
from app.models.device import Device

logger = logging.getLogger(__name__)


def ensure_device_exists(device_id: str) -> None:
    """
    If telemetry arrives for an unknown device, auto-register it with a default name.
    This reflects real industrial pipelines where devices might appear dynamically.
    """
    if not device_id:
        return

    with get_session() as session:
        existing = session.execute(select(Device).where(Device.device_id == device_id)).scalar_one_or_none()
        if existing:
            return

        device = Device(
            device_id=device_id,
            name=f"Auto-registered {device_id}",
            location=None,
            description="Created automatically from MQTT ingestion.",
        )
        session.add(device)
        session.flush()
        logger.info("Auto-registered device", extra={"device_id": device_id})

