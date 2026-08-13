from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ServerInfoResponse(BaseModel):
    uuid: UUID
    created_at: datetime
    display_name: str
    role: str

class ServerCreated(BaseModel):
    id: int
    uuid: UUID
    daemon_key: str
