from sqlmodel import SQLModel, create_engine, Session
from typing import Optional
from pathlib import Path
DB_FILE = "/data/users.db"
engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
