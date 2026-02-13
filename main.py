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

# -------------------------
# GLOBAL STORAGE
# -------------------------
latest_data = []
history_data = []
last_update_time = 0


# -------------------------
# DATA MODEL
# -------------------------
class SensorData(BaseModel):
    values: List[float]


# -------------------------
# ROOT (Dashboard Page)
# -------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html", "r") as f:
        return f.read()


# -------------------------
# HISTORY PAGE
# -------------------------
@app.get("/historypage", response_class=HTMLResponse)
def history_page():
    with open("history.html", "r") as f:
        return f.read()


# -------------------------
# RECEIVE DATA FROM ESP
# -------------------------
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


# -------------------------
# GET LATEST VALUES
# -------------------------
@app.get("/latest")
def get_latest():
    return {"values": latest_data}


# -------------------------
# GET FULL HISTORY
# -------------------------
@app.get("/history")
def get_history():
    return {"history": history_data}


# -------------------------
# DEVICE STATUS CHECK
# -------------------------
@app.get("/status")
def device_status():
    global last_update_time

    if time.time() - last_update_time < 3:
        return {"device": "connected"}
    else:
        return {"device": "disconnected"}


