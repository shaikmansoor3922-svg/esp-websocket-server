from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

connected_clients = []

@app.get("/")
async def get():
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client Connected")

    try:
        while True:
            data = await websocket.receive_text()
            print("Received from ESP:", data)

            # Send to all connected browser clients
            for client in connected_clients:
                try:
                    await client.send_text(f"new_data:{data}")
                except:
                    pass

    except WebSocketDisconnect:
        print("Client Disconnected")
        connected_clients.remove(websocket)
    except Exception as e:
        print("WebSocket Error:", e)
        if websocket in connected_clients:
            connected_clients.remove(websocket)
