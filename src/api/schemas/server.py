from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.common.enums import ServerUserRole
from typing import Literal, Annotated


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


class FileCreate(BaseModel):
    type: Literal["file"]
    path: str
    content: str


class FolderCreate(BaseModel):
    type: Literal["folder"]
    path: str


FileCreateRequest = Annotated[FileCreate | FolderCreate, Field(discriminator="type")]


class FileUpdate(BaseModel):
    type: Literal["file"]
    path: str
    new_path: str | None = None
    new_content: str | None = None


class FolderUpdate(BaseModel):
    type: Literal["folder"]
    path: str
    new_path: str


FileUpdateRequest = Annotated[FileUpdate | FolderUpdate, Field(discriminator="type")]
