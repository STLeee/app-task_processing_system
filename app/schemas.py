from pydantic import BaseModel
from datetime import datetime
from typing import Optional

TASK_STATUS_PENDING     = "pending"
TASK_STATUS_PROCESSING  = "processing"
TASK_STATUS_COMPLETED   = "completed"
TASK_STATUS_CANCELED    = "canceled"

class TaskCreate(BaseModel):
    content: str

class TaskResponse(BaseModel):
    id: str
    content: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
