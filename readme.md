# IoT Telemetry Ingestion & Analytics Backend

A lightweight, self-hosted IoT telemetry backend (inspired by ThingSpeak) built with **Python**, **FastAPI**, **SQLite**, and a **multi-device ESP32 telemetry simulator**. It ingests real-time sensor packets over REST, validates physical sensor bounds with Pydantic, persists time-series readings and threshold alerts in SQLite, and exposes per-device SQL aggregation endpoints.

## Features

- **Real-Time Telemetry Ingestion (`POST /telemetry`)**: Validates incoming JSON payloads (`device_id`, `temperature_c`, `humidity_pct`, `air_quality_ppm`) using Pydantic schemas and stores UTC-timestamped records in SQLite.
- **Automated Threshold Alert Engine (`GET /alerts`)**: Evaluates incoming readings against configurable safety thresholds (`> 30.0°C` temperature or `> 800 ppm` CO₂) and logs alert events automatically.
- **Per-Device SQL Analytics (`GET /devices/{device_id}/summary`)**: Computes `COUNT`, `AVG`, `MIN`, `MAX`, and `last_seen` metrics directly in SQLite with `404 Not Found` handling for unknown devices.
- **Multi-Device IoT Simulator (`simulator.py`)**: Simulates 3 concurrent ESP32 sensor nodes (`esp32-room-01`, `esp32-lab-02`, `esp32-server-03`) with realistic sensor drift using Python's standard library.

## Tech Stack

- **Backend Framework**: Python 3.9+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Database**: [SQLite3](https://docs.python.org/3/library/sqlite3.html) (parameterized queries, zero-config local persistence)
- **Device Simulation**: Python `urllib.request` multi-node HTTP telemetry client

## Project Structure

```text
iot-telemetry-backend/
├── main.py            # FastAPI application, Pydantic schemas, routes & alert logic
├── database.py        # SQLite connection helper, table initialization & SQL queries
├── simulator.py       # Active multi-device virtual ESP32 telemetry streamer
├── requirements.txt   # Pinned Python dependencies
├── .gitignore         # Ignored virtual environment, cache, and local SQLite files
└── README.md          # Project documentation
```

## API Endpoints

| Method | Endpoint                       | Description                                                                             |
| :----- | :----------------------------- | :-------------------------------------------------------------------------------------- |
| `GET`  | `/`                            | Root status and endpoint discovery                                                      |
| `GET`  | `/health`                      | Service health check (`200 OK`)                                                         |
| `POST` | `/telemetry`                   | Ingest a sensor reading, validate bounds, and evaluate threshold alerts (`201 Created`) |
| `GET`  | `/telemetry`                   | Fetch recent telemetry readings (`?limit=10&device_id=esp32-room-01`)                   |
| `GET`  | `/alerts`                      | Fetch triggered high-temperature and poor-air-quality alerts (`?limit=20`)              |
| `GET`  | `/devices/{device_id}/summary` | Get `COUNT`, `AVG`, `MIN`, `MAX`, and `last_seen` metrics for a specific device         |

## Quick Start

### 1. Clone & Set Up Virtual Environment

```powershell
git clone https://github.com/<your-username>/iot-telemetry-backend.git
cd iot-telemetry-backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

```powershell
.\venv\Scripts\python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` in your browser to explore and test all endpoints via Swagger UI.

### 3. Start the Multi-Device IoT Simulator

Open a second terminal in the project folder and run:

```powershell
.\venv\Scripts\python simulator.py
```

## Example Telemetry Payload

```json
{
  "device_id": "esp32-room-01",
  "temperature_c": 25.4,
  "humidity_pct": 52.0,
  "air_quality_ppm": 420
}
```
