import os
from typing import List


class Settings:
    # Gateway URLs for downstream services (used in tests/local compose)
    USERS_URL: str = os.getenv("USERS_URL", "http://service_users:8001")
    ORDERS_URL: str = os.getenv("ORDERS_URL", "http://service_orders:8002")

    # Security
    # JWT secret can be provided directly or via a file (useful for Docker secrets)
    _jwt_file = os.getenv("JWT_SECRET_FILE")
    if _jwt_file and _jwt_file.strip() and os.path.exists(_jwt_file):
        with open(_jwt_file, "r", encoding="utf-8") as f:
            JWT_SECRET: str = f.read().strip()
    else:
        JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")

    # Rate limiting (slowapi format)
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/minute")

    # CORS origins (comma separated or single * for all)
    _cors = os.getenv("CORS_ORIGINS", "*")
    if _cors.strip() == "*":
        CORS_ORIGINS: List[str] = ["*"]
    else:
        CORS_ORIGINS: List[str] = [s.strip() for s in _cors.split(",") if s.strip()]

    # Optional observability
    OTEL_COLLECTOR_URL: str | None = os.getenv("OTEL_COLLECTOR_URL")
    # Password hashing algorithm for consistency across services (not used by gateway)
    HASH_ALGORITHM: str = os.getenv("HASH_ALGORITHM", "pbkdf2_sha256")


settings = Settings()
