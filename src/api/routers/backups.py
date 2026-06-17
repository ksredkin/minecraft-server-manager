from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.api.services.backup_service import BackupService, get_backup_service

backups_router = APIRouter(prefix="/backups")


@backups_router.get("/", description="Просмотреть список резервных копий.")
def get_backups(
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backups = backup_service.get_backups()
    if backups is not None:
        return JSONResponse({"success": True, "data": {"backups": backups}}, 201)
    else:
        raise HTTPException(500, {"success": False})


@backups_router.post("/", description="Создать резервную копию сервера.")
def create_backup(
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backup_name = backup_service.create_backup()
    return JSONResponse({"success": True, "data": {"name": backup_name}}, 201)
