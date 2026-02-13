from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Store latest sensor values
latest_data = []

class SensorData(BaseModel):
    values: List[float]

@app.get("/")
def home():
    return {"status": "Server Running"}

@app.post("/upload")
def upload_data(data: SensorData):
    global latest_data
    latest_data = data.values
    print("Received:", latest_data)
    return {"message": "Data received successfully"}

@app.get("/latest")
def get_latest():
    return {"values": latest_data if latest_data else [0]*16}

