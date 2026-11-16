import json
import random
import time
from urllib import error, request

API_URL = "http://127.0.0.1:8000/telemetry"

DEVICES = {
    "esp32-room-01": {"temp": 24.5, "hum": 50.0, "air": 420},
    "esp32-lab-02": {"temp": 26.0, "hum": 55.0, "air": 510},
    "esp32-server-03": {"temp": 29.5, "hum": 42.0, "air": 610},
}

print("Starting multi-device IoT simulator (Press Ctrl+C to stop)...")

try:
    while True:
        for device_id, s in DEVICES.items():
            s["temp"] = round(max(18.0, min(42.0, s["temp"] + random.uniform(-0.4, 0.5))), 1)
            s["hum"] = round(max(30.0, min(85.0, s["hum"] + random.uniform(-1.0, 1.0))), 1)
            s["air"] = int(max(350, min(1500, s["air"] + random.randint(-20, 25))))

            payload = {
                "device_id": device_id,
                "temperature_c": s["temp"],
                "humidity_pct": s["hum"],
                "air_quality_ppm": s["air"],
            }

            req = request.Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=5) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    row_id = body["data"]["id"]
                    print(f"[#{row_id}] {device_id} -> {s['temp']}C | {s['hum']}% | {s['air']} ppm")
            except error.URLError as exc:
                print(f"[ERROR] {device_id}: {exc}")

        print("-" * 50)
        time.sleep(2)
except KeyboardInterrupt:
    print("\nSimulator stopped.")