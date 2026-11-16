import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "telemetry.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                air_quality_ppm INTEGER NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_reading(data: dict) -> dict:
    received_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO telemetry (device_id, temperature_c, humidity_pct, air_quality_ppm, received_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["device_id"],
                data["temperature_c"],
                data["humidity_pct"],
                data["air_quality_ppm"],
                received_at,
            ),
        )
        conn.commit()
        row_id = cursor.lastrowid

    return {
        "id": row_id,
        **data,
        "received_at": received_at,
    }


def fetch_readings(limit: int = 10, device_id: Optional[str] = None) -> list:
    with get_connection() as conn:
        if device_id:
            cursor = conn.execute(
                "SELECT * FROM telemetry WHERE device_id = ? ORDER BY id DESC LIMIT ?",
                (device_id, limit),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM telemetry ORDER BY id DESC LIMIT ?",
                (limit,),
            )
        return [dict(row) for row in cursor.fetchall()]


def create_alert(device_id: str, metric: str, value: float, message: str) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO alerts (device_id, metric, value, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (device_id, metric, value, message, created_at),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "device_id": device_id,
            "metric": metric,
            "value": value,
            "message": message,
            "created_at": created_at,
        }


def fetch_alerts(limit: int = 20) -> list:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


def fetch_device_summary(device_id: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                device_id,
                COUNT(*) AS total_readings,
                ROUND(AVG(temperature_c), 2) AS avg_temp_c,
                MIN(temperature_c) AS min_temp_c,
                MAX(temperature_c) AS max_temp_c,
                ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
                ROUND(AVG(air_quality_ppm), 0) AS avg_air_ppm,
                MAX(received_at) AS last_seen
            FROM telemetry
            WHERE device_id = ?
            """,
            (device_id,),
        ).fetchone()

        if not row or row["total_readings"] == 0:
            return None
        return dict(row)