from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.common.enums import ServerUserRole


class ServerInfoResponse(BaseModel):
    uuid: UUID
    created_at: datetime
    display_name: str
    role: ServerUserRole


class ServerCreated(BaseModel):
    id: int
    uuid: UUID
    daemon_key: str
    created_at: datetime


class ServerDeletedResponse(BaseModel):
    uuid: UUID
    daemon_key_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
