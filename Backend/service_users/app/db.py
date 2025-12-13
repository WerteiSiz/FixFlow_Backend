from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path
from .config import settings

DB_FILE = settings.DB_FILE
Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///./{DB_FILE}", connect_args={"check_same_thread": False})

def init_db():
    # ensure clean schema for test runs (drops existing tables then recreates)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
