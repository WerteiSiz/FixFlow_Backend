from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserOut(BaseModel):
    id: str
    email: str
    name: str
    roles: List[str]

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
