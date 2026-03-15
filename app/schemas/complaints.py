from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplaintCreate(BaseModel):
    name: str
    phone: str
    category: str
    description: str

class ComplaintResponse(BaseModel):
    id: int
    name: str
    phone: str
    category: str
    description: str
    status: str
    department: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True