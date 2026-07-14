from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.api.services.metrics_service import MetricsService, get_metrics_service

metrics_router = APIRouter(prefix="/metrics")


@metrics_router.get("/ram")
def get_ram_usage(metrics_service: MetricsService = Depends(get_metrics_service)) -> JSONResponse:
    result = metrics_service.get_ram_usage()
    return JSONResponse({"success": True, "data": result}, 200)


@metrics_router.get("/cpu")
def get_cpu_percent(metrics_service: MetricsService = Depends(get_metrics_service)) -> JSONResponse:
    result = metrics_service.get_cpu_percent()
    return JSONResponse({"success": True, "data": result}, 200)
