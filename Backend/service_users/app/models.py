from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from sqlalchemy import JSON as SAJSON
from typing import List, Optional
import uuid
from datetime import datetime


def gen_uuid():
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    hashed_password: str = Field(nullable=False)
    name: Optional[str] = Field(default=None)
    roles: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
