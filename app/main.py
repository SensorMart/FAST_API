from fastapi import FastAPI,Request,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from typing import List

app = FastAPI()

class SensorData(BaseModel):
    sr_no: int
    X: float
    Y: float
    Z: float

#in memory storage
data_storage : List[SensorData] = []
templates = Jinja2Templates(directory="app/templates")

#store copnnected web socket clients
clients : list[WebSocket] = []

@app.post("/data/")
async def receive_data(data: SensorData):
    data_storage.append(data)
    # await broadcast_data(data)
    return {"message": "Data received and saved"}


@app.get("/data/", response_model=list[SensorData])
async def get_data():
    return data_storage

@app.get("/",response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html",{"request":request, "data":data_storage})

# web socket is implemented here
@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    clients.append(websocket)
    # data_storage.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)  # Parse JSON data
            sensor_data = SensorData(**data_dict)  # Create SensorData instance
            data_storage.append(sensor_data)  # Store data in memory
            await broadcast_data(sensor_data)
            await websocket.send_text(f"Data received: {data_dict}")  # Confirm reception
    except WebSocketDisconnect:
        clients.remove(websocket)
        # data_storage.remove(websocket)
        print("WebSocket connection closed")
    except json.JSONDecodeError:
        await websocket.send_text("Error: Invalid JSON data")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

async def broadcast_data(data: SensorData):
    message = json.dumps(data.model_dump())
    for client in clients:
        await client.send_text(message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.31.104", port=8000)
