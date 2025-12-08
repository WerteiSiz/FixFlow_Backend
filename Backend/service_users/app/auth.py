from passlib.context import CryptContext
import jwt
from .config import settings
from datetime import datetime, timedelta

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str):
    return pwd_ctx.hash(raw)

def verify_password(raw: str, hashed: str):
    return pwd_ctx.verify(raw, hashed)

def create_access_token(user_id: str, email: str, roles: list):
    payload = {"sub": user_id, "email": email, "roles": roles, "exp": datetime.utcnow() + timedelta(hours=8)}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token
