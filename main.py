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
@app.get("/historypage", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


# ------------------------
# RECEIVE DATA
# ------------------------
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
def get_history():
    return {"history": history_data}


# ------------------------
# DEVICE STATUS
# ------------------------
@app.get("/status")
def device_status():
    if last_update_time == 0:
        return {"device": "disconnected"}

    # If no data for 5 seconds → disconnected
    if time.time() - last_update_time > 5:
        return {"device": "disconnected"}
    else:
        return {"device": "connected"}

