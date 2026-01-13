import json
import logging
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.services.ingestion_service import ingest_sensor_payload

logger = logging.getLogger(__name__)


@dataclass
class MqttMessage:
    topic: str
    payload: Dict[str, Any]


class MqttConsumer:
    """
    MQTT consumer runs in background thread.
    On message -> parse JSON -> call ingestion service -> store to DB.
    """

    def __init__(self) -> None:
        self._client: Optional[mqtt.Client] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="mqtt-consumer", daemon=True)
        self._thread.start()
        logger.info("MQTT consumer started", extra={"topic": settings.mqtt_topic})

    def stop(self) -> None:
        self._stop_event.set()
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                logger.exception("Failed to disconnect MQTT client")
        if self._thread is not None:
            self._thread.join(timeout=5)
        logger.info("MQTT consumer stopped")

    def _run(self) -> None:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client = client

        def on_connect(c: mqtt.Client, userdata: Any, flags: Dict[str, Any], reason_code: int, properties: Any) -> None:
            if reason_code == 0:
                logger.info("Connected to MQTT broker", extra={"host": settings.mqtt_host, "port": settings.mqtt_port})
                c.subscribe(settings.mqtt_topic, qos=1)
                logger.info("Subscribed to MQTT topic", extra={"topic": settings.mqtt_topic})
            else:
                logger.error("MQTT connect failed", extra={"reason_code": reason_code})

        def on_message(c: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
            try:
                raw = msg.payload.decode("utf-8")
                data = json.loads(raw)
                message = MqttMessage(topic=msg.topic, payload=data)
                ingest_sensor_payload(message.topic, message.payload)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received", extra={"topic": msg.topic})
            except Exception:
                logger.exception("Error processing MQTT message", extra={"topic": msg.topic})

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=settings.mqtt_keepalive)
        client.loop_start()

        try:
            while not self._stop_event.is_set():
                self._stop_event.wait(timeout=1.0)
        finally:
            client.loop_stop()

