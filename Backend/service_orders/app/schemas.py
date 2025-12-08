from pydantic import BaseModel
from typing import List, Dict

class OrderCreate(BaseModel):
    items: List[Dict]  # e.g. [{"product_id": "...", "quantity": 2}]
    total: float

class OrderOut(BaseModel):
    id: str
    user_id: str
    items: List[Dict]
    status: str
    total: float
