from pydantic import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str = "CHANGE_ME_SECRET"

settings = Settings()
