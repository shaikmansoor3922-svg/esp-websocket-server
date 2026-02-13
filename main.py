from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Store all historical data
all_data = []
latest_data = []

class SensorData(BaseModel):
    values: List[float]

# Dashboard page
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Upload data from ESP
@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data, all_data
    latest_data = data.values
    all_data.append(data.values)
    print("Received:", latest_data)
    return {"message": "Data received successfully"}

# Latest values (for live dashboard)
@app.get("/latest")
def get_latest():
    return {"values": latest_data}

# All historical values (for table button)
@app.get("/history")
def get_history():
    return {"data": all_data}
