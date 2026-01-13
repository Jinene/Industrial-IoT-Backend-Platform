from fastapi import FastAPI

from app.api.v1.devices import router as devices_router
from app.api.v1.data import router as data_router
from app.api.v1.health import router as health_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.core.mqtt_client import MqttConsumer


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Industrial IoT backend: MQTT ingestion, processing, SQL persistence, REST APIs.",
    )

    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(devices_router, prefix="/api/v1", tags=["devices"])
    app.include_router(data_router, prefix="/api/v1", tags=["data"])

    mqtt_consumer = MqttConsumer()

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        mqtt_consumer.start()

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        mqtt_consumer.stop()

    return app


app = create_app()

