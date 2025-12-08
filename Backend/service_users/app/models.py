from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid
from datetime import datetime

def gen_uuid():
    return str(uuid.uuid4())

class User(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    email: str = Field(index=True)
    hashed_password: str
    name: str
    roles: List[str] = Field(sa_column=None, default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
