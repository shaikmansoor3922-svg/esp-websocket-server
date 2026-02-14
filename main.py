from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import csv
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import time
from fastapi import Query
from fastapi.responses import StreamingResponse
from io import StringIO


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------------
# STORAGE
# ------------------------
latest_data = []
history_data = []
last_update_time = 0


# ------------------------
# MODEL
# ------------------------
class SensorData(BaseModel):
    values: List[float]


# ------------------------
# DASHBOARD PAGE
# ------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ------------------------
# HISTORY PAGE
# ------------------------
@app.get("/history_page", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


# ------------------------
# RECEIVE DATA
# ------------------------
upload_counter = 0

@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data, history_data, last_update_time, upload_counter

    latest_data = data.values

    history_data.append({
        "timestamp": data.timestamp,
        "values": data.values
    })

    last_update_time = time.time()

    return {"message": "Data received successfully"}

# ------------------------
# LATEST DATA
# ------------------------
@app.get("/latest")
def get_latest():
    return {"values": latest_data}


# ------------------------
# FULL HISTORY
# ------------------------
@app.get("/history")
def get_history(start: str = Query(None), end: str = Query(None)):

    if not start and not end:
        return {"history": history_data}

    filtered = []

    for record in history_data:

        record_time = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")

        if start:
            start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            if record_time < start_time:
                continue

        if end:
            end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            if record_time > end_time:
                continue

        filtered.append(record)

    return {"history": filtered}
# ------------------------
# download
# ------------------------

@app.get("/download")
def download_data(start: str = None, end: str = None):

    filtered = history_data

    # Filter by time if provided
    if start:
        filtered = [d for d in filtered if d["timestamp"] >= start]
    if end:
        filtered = [d for d in filtered if d["timestamp"] <= end]

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Header
    header = ["Timestamp"] + [f"Sensor {i}" for i in range(1, 17)]
    writer.writerow(header)

    # Rows
    for record in filtered:
        row = [record["timestamp"]] + record["values"]
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sensor_data.csv"
        },
    )


# ------------------------
# DEVICE STATUS
# ------------------------
@app.get("/status")
def device_status():
    global last_update_time

    if last_update_time == 0:
        return {"device": "disconnected"}

    current_time = time.time()
    diff = current_time - last_update_time

    # increase threshold to avoid render latency issue
    if diff > 10:
        return {"device": "disconnected"}
    else:
        return {"device": "connected"}


@app.get("/debug_time")
def debug_time():
    return {
        "last_update_time": last_update_time,
        "current_time": time.time(),
        "difference": time.time() - last_update_time
    }



