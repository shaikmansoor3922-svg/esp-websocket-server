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
last_update_time = 0

class SensorData(BaseModel):
    values: List[float]

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ESP POSTS HERE
@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data, all_data, last_update_time

    latest_data = data.values
    all_data.append(data.values)
    last_update_time = time.time()

    return {"message": "Data received"}


# Dashboard fetches live data
@app.get("/latest")
def get_latest():
    return {"values": latest_data}


# Dashboard fetches full history
@app.get("/history")
def get_history():
    return {"history": all_data}


@app.get("/status")
def get_status():
    current_time = time.time()

    # Give 10 seconds tolerance
    if current_time - last_update_time < 10:
        return {"device": "connected"}
    else:
        return {"device": "disconnected"}

