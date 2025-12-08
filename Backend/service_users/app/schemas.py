from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    roles: List[str]

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
