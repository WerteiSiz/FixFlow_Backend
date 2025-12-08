from pydantic import BaseSettings

class Settings(BaseSettings):
    USERS_URL: str = "http://service_users:8001"
    ORDERS_URL: str = "http://service_orders:8002"
    JWT_SECRET: str = "CHANGE_ME_SECRET"
    RATE_LIMIT: str = "100/minute"

settings = Settings()
