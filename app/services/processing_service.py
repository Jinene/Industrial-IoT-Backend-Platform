import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and sanitize incoming telemetry payload.

    Expected keys (example):
      device_id, temperature_c, pressure_bar, vibration_mm_s, ts
    """
    out: Dict[str, Any] = {}

    # Required
    out["device_id"] = str(payload.get("device_id", "")).strip()

    # Optional numeric fields
    for key in ("temperature_c", "pressure_bar", "vibration_mm_s"):
        val = payload.get(key)
        if val is None:
            out[key] = None
            continue
        try:
            out[key] = float(val)
        except (TypeError, ValueError):
            logger.warning("Invalid numeric field", extra={"field": key, "value": val})
            out[key] = None

    # Timestamp: accept ISO string or datetime
    ts = payload.get("ts")
    if isinstance(ts, datetime):
        out["ts"] = ts
    else:
        # Attempt parse ISO string
        try:
            out["ts"] = datetime.fromisoformat(str(ts))
        except Exception:
            # fallback: server time
            out["ts"] = datetime.utcnow()

    return out


def detect_anomalies(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple anomaly flags (demo). In a real project, rules might be configurable.
    """
    anomalies = []

    t = data.get("temperature_c")
    if t is not None and (t < -10 or t > 120):
        anomalies.append("temperature_out_of_range")

    p = data.get("pressure_bar")
    if p is not None and (p < 0 or p > 20):
        anomalies.append("pressure_out_of_range")

    v = data.get("vibration_mm_s")
    if v is not None and v > 40:
        anomalies.append("vibration_high")

    data["anomalies"] = anomalies
    return data

