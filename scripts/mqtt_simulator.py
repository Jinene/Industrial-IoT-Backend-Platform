
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


MQTT_HOST = "localhost"
MQTT_PORT = 1883

DEVICE_IDS = ["machine_01", "machine_02", "press_07", "line_A_sensorhub"]
TOPICS = [
    "factory/machine_01/sensors",
    "factory/machine_02/sensors",
    "factory/press_07/sensors",
    "factory/line_A/sensors",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            device_id = random.choice(DEVICE_IDS)
            topic = random.choice(TOPICS)
            payload = {
                "device_id": device_id,
                "temperature_c": round(random.uniform(15.0, 95.0), 2),
                "pressure_bar": round(random.uniform(0.8, 8.5), 3),
                "vibration_mm_s": round(random.uniform(0.0, 25.0), 3),
                "ts": now_iso(),
            }
            client.publish(topic, json.dumps(payload), qos=1)
            print(f"Published to {topic}: {payload}")
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
