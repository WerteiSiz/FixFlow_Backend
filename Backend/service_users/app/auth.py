from passlib.context import CryptContext
import jwt
from .config import settings
from datetime import datetime, timedelta
import logging

# Determine hashing schemes based on configured algorithm and availability of bcrypt
_schemes = ["pbkdf2_sha256"]
_use_bcrypt = False
if settings.HASH_ALGORITHM and settings.HASH_ALGORITHM.lower() == "bcrypt":
    try:
        import bcrypt  # type: ignore
        _schemes = ["bcrypt", "pbkdf2_sha256"]
        _use_bcrypt = True
    except Exception:
        logging.warning("HASH_ALGORITHM=bcrypt requested but 'bcrypt' package not available; falling back to pbkdf2_sha256")

pwd_ctx = CryptContext(schemes=_schemes, deprecated="auto")


def _limit_password(raw: str) -> str:
    if not isinstance(raw, str):
        raw = str(raw)
    # bcrypt has a 72-byte input limitation; keep safe default limits
    limit = 72 if _use_bcrypt else 256
    return raw[:limit]


def hash_password(raw: str):
    return pwd_ctx.hash(_limit_password(raw))


def verify_password(raw: str, hashed: str):
    return pwd_ctx.verify(_limit_password(raw), hashed)


def create_access_token(user_id: str, email: str, roles: list):
    payload = {"sub": user_id, "email": email, "roles": roles, "exp": datetime.utcnow() + timedelta(hours=8)}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token
