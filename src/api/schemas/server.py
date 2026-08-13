from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ServerInfoResponse(BaseModel):
    uuid: UUID
    created_at: datetime
    display_name: str
    role: str

class ServerCreated(BaseModel):
    uuid: UUID
    daemon_key: str
    created_at: datetime

class ServerDeletedResponse(BaseModel):
    uuid: UUID
    daemon_key_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
