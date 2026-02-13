from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

latest_data = []
data_history = []
last_received_time = 0

class SensorData(BaseModel):
    values: List[float]

@app.get("/")
def home():
    return {"status": "Server Running"}

@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data, data_history, last_received_time
    latest_data = data.values
    data_history.append(data.values)
    last_received_time = time.time()   # store current time
    print("Received:", latest_data)
    return {"message": "Data received successfully"}

@app.get("/latest")
def get_latest():
    return {"values": latest_data}

@app.get("/history")
def get_history():
    return {"history": data_history}

@app.get("/status")
def get_status():
    # If no data for more than 5 seconds → disconnected
    if time.time() - last_received_time > 5:
        return {"device": "disconnected"}
    else:
        return {"device": "connected"}
