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

app = FastAPI()
templates = Jinja2Templates(directory="templates")

latest_data = []
all_data = []
history_data = []
last_update_time = 0

class SensorData(BaseModel):
    values: List[float]

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ESP POSTS HERE
@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data, history_data, last_update_time

    latest_data = data.values
    history_data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "values": data.values
    })

    last_update_time = time.time()

    return {"message": "Data received successfully"}



# Dashboard fetches live data
@app.get("/latest")
def get_latest():
    return {"values": latest_data}


# Dashboard fetches full history
@app.get("/history")
def get_history():
    return {"history": history_data}


@app.get("/status")
def get_status():
    current_time = time.time()

    # Give 10 seconds tolerance
    if current_time - last_update_time < 10:
        return {"device": "connected"}
    else:
        return {"device": "disconnected"}

@app.get("/download")
def download_data(start: str, end: str):

    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M")
    end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M")

    filename = "filtered_data.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        header = ["Timestamp"] + [f"Sensor {i}" for i in range(1, 17)]
        writer.writerow(header)

        for row in history_data:
            row_time = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")

            if start_dt <= row_time <= end_dt:
                writer.writerow([row["timestamp"]] + row["values"])

    return FileResponse(filename, media_type="text/csv", filename="sensor_data.csv")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html") as f:
        return f.read()


@app.get("/history_page", response_class=HTMLResponse)
def history_page():
    with open("history.html") as f:
        return f.read()

