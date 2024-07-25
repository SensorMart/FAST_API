from fastapi import FastAPI,Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()

class SensorData(BaseModel):
    sr_no: int
    X: float
    Y: float
    Z: float

#in memory storage
data_storage = []
templates =Jinja2Templates(directory="app/templates")


@app.post("/data/")
async def receive_data(data: SensorData):
    data_storage.append(data)
    return {"message": "Data received and saved"}


@app.get("/data/", response_model=list[SensorData])
async def get_data():
    return data_storage

@app.get("/",response_class=HTMLResponse)
async def get_webpage(request: Request):
    return templates.TemplateResponse("index.html",{"request":request, "data":data_storage})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.31.104", port=8000)
