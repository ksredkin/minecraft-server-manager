from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.backup_service import BackupService, get_backup_service
from src.api.utils.logger import Logger

logger = Logger(__name__)
backups_router = APIRouter(prefix="/backups")


@backups_router.get("/", description="Просмотреть список резервных копий.")
def get_backups(
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backups = backup_service.get_backups()
    return JSONResponse({"success": True, "data": {"backups": backups}}, 200)


@backups_router.post("/", description="Создать резервную копию сервера.")
def create_backup(
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backup_name = backup_service.create_backup()
    logger.info(f"Создана резервная копия сервера: {backup_name}")
    return JSONResponse({"success": True, "data": {"backup": backup_name}}, 201)


@backups_router.post(
    "/restore/{backup}", description="Восстановить сервер из резервной копии."
)
def restore_backup(
    backup: str,
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backup_service.restore_backup(backup)
    logger.info(f"Сервер восстановлен из резервной копии: {backup}")
    return JSONResponse({"success": True, "data": {"backup": backup}}, 200)


@backups_router.delete("/{backup}", description="Удалить резервную копию сервера.")
def delete_backup(
    backup: str,
    backup_service: BackupService = Depends(get_backup_service),
) -> JSONResponse:
    backup_service.delete_backup(backup)
    logger.info(f"Удалена резервная копия сервера: {backup}")
    return JSONResponse({"success": True, "data": {"backup": backup}}, 200)
