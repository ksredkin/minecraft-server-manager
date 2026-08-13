from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ServerUserResponse(BaseModel):
    id: int
    server_id: int
    uuid: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
