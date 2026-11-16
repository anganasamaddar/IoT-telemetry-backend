from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from database import (
    create_alert,
    fetch_alerts,
    fetch_device_summary,
    fetch_readings,
    init_db,
    insert_reading,
)

app = FastAPI(title="IoT Telemetry Backend")

init_db()

TEMP_THRESHOLD_C = 30.0
AIR_THRESHOLD_PPM = 800


class TelemetryReading(BaseModel):
    device_id: str = Field(..., min_length=3)
    temperature_c: float = Field(..., ge=-40.0, le=85.0)
    humidity_pct: float = Field(..., ge=0.0, le=100.0)
    air_quality_ppm: int = Field(..., ge=0, le=5000)


@app.get("/")
def root():
    return {
        "message": "IoT Telemetry Backend is running",
        "docs": "/docs",
        "health": "/health",
        "telemetry": "/telemetry",
        "alerts": "/alerts",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "iot-telemetry-backend"}


@app.post("/telemetry", status_code=status.HTTP_201_CREATED)
def ingest_telemetry(reading: TelemetryReading):
    saved = insert_reading(reading.model_dump())
    triggered_alerts = []

    if reading.temperature_c > TEMP_THRESHOLD_C:
        triggered_alerts.append(
            create_alert(
                reading.device_id,
                "temperature_c",
                reading.temperature_c,
                f"High temperature ({reading.temperature_c} C > {TEMP_THRESHOLD_C} C)",
            )
        )

    if reading.air_quality_ppm > AIR_THRESHOLD_PPM:
        triggered_alerts.append(
            create_alert(
                reading.device_id,
                "air_quality_ppm",
                reading.air_quality_ppm,
                f"Poor air quality ({reading.air_quality_ppm} ppm > {AIR_THRESHOLD_PPM} ppm)",
            )
        )

    return {
        "message": "Telemetry saved to SQLite",
        "data": saved,
        "alerts_triggered": triggered_alerts,
    }


@app.get("/telemetry")
def get_telemetry(
    limit: int = Query(10, ge=1, le=100),
    device_id: Optional[str] = None,
):
    readings = fetch_readings(limit=limit, device_id=device_id)
    return {"count": len(readings), "readings": readings}


@app.get("/alerts")
def get_alerts(limit: int = Query(20, ge=1, le=100)):
    alerts = fetch_alerts(limit=limit)
    return {"count": len(alerts), "alerts": alerts}


@app.get("/devices/{device_id}/summary")
def get_device_summary(device_id: str):
    summary = fetch_device_summary(device_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found",
        )
    return summary