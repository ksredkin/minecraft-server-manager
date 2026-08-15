from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServerUserResponse(BaseModel):
    id: int
    server_id: int
    uuid: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
