# Industrial IoT Backend (FastAPI + MQTT + SQL + Docker)

Backend Python for an industrial IoT platform:
- Ingest sensor data via MQTT (real-time)
- Validate + process data
- Store in PostgreSQL
- Expose REST APIs for devices + sensor data

## Stack
Python, FastAPI, SQLAlchemy, PostgreSQL, Docker, MQTT (Mosquitto), Linux

## Run (Docker)
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
API: http://localhost:8000
Docs: http://localhost:8000/docs

Publish MQTT test data
In another terminal:

bash
python scripts/mqtt_simulator.py
Endpoints
GET /api/v1/health

POST /api/v1/devices

GET /api/v1/devices

GET /api/v1/devices/{device_id}

POST /api/v1/data/ingest (manual ingest)

GET /api/v1/data (filterable)

yaml

---

## `docker/Dockerfile`
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
