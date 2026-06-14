from fastapi import FastAPI
import uvicorn
from src.common.core.config import API_HOST, API_PORT
from src.api.services.process_service import ProcessService

app = FastAPI()
process_service = ProcessService()

@app.post("/start")
async def start():
    return process_service.start()

@app.post("/stop")
async def stop():
    return process_service.stop()

@app.post("/restart")
async def restart():
    return process_service.restart()

@app.get("/status")
async def status():
    return {"status": process_service.status()}

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
