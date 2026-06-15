from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.common.core.config import API_HOST, API_PORT
from src.api.services.process_service import ProcessService

app = FastAPI(title="Minecraft Server Manager", description="API для управления Minecraft сервером.")
process_service = ProcessService()

@app.post("/start", description="Запустить сервер.")
async def start():
    result = process_service.start()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/stop", description="Остановить сервер.")
async def stop():
    result = process_service.stop()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/restart", description="Перезапустить сервер.")
async def restart():
    result = process_service.restart()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.get("/status", description="Получить текущий статус работы сервера.")
async def status():
    status = process_service.status()
    if status:
        return JSONResponse({"success": True, "data": {"status": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
