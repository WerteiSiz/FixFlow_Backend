import os


class Settings:
    # JWT secret can be provided directly or via a file (useful for Docker secrets)
    _jwt_file = os.getenv("JWT_SECRET_FILE")
    if _jwt_file and _jwt_file.strip() and os.path.exists(_jwt_file):
        with open(_jwt_file, "r", encoding="utf-8") as f:
            JWT_SECRET: str = f.read().strip()
    else:
        JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_SECRET")
    # DB path for sqlite
    DB_FILE: str = os.getenv("ORDERS_DB_FILE", "data/orders.db")
    # Optional observability
    OTEL_COLLECTOR_URL: str | None = os.getenv("OTEL_COLLECTOR_URL")
    # Password hashing algorithm (kept for parity with users service)
    HASH_ALGORITHM: str = os.getenv("HASH_ALGORITHM", "pbkdf2_sha256")


settings = Settings()
