from sqlmodel import SQLModel, Field
from typing import List
import uuid
from datetime import datetime
def gen_uuid():
    return str(uuid.uuid4())

class Order(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    user_id: str = Field(index=True)
    items: str  # JSON string of positions; for simplicity
    status: str = Field(default="created")
    total: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
