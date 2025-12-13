from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from sqlmodel import select
from .db import init_db, get_session
from .models import User
from .schemas import UserCreate, UserOut, TokenOut
from .auth import hash_password, verify_password, create_access_token
from .events import publish_user_created
from .middleware import XRequestIDMiddleware
from .logging import setup_logging
from .tracing import setup_tracing
from typing import List, Optional
import logging

setup_logging()
logger = logging.getLogger("service_users")
app = FastAPI(title="Users Service")
app.add_middleware(XRequestIDMiddleware)
# optional tracing
tracer = setup_tracing(app, service_name="service_users")

# Ensure DB/tables exist on import for test environment
init_db()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/v1/auth/register", response_model=dict)
def register(body: UserCreate, request: Request):
    session = next(get_session())
    # DB span
    try:
        from opentelemetry import trace as otel_trace
        tracer_local = tracer or otel_trace.get_tracer(__name__)
        with tracer_local.start_as_current_span("users.create") as span:
            span.set_attribute("user.email", body.email)
            user_exists = session.exec(select(User).where(User.email == body.email)).first()
            if user_exists:
                raise HTTPException(status_code=400, detail="Email already registered")
            user = User(email=body.email, hashed_password=hash_password(body.password), name=body.name, roles=["user"])
            session.add(user)
            session.commit()
            session.refresh(user)
    except Exception:
        user_exists = session.exec(select(User).where(User.email == body.email)).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(email=body.email, hashed_password=hash_password(body.password), name=body.name, roles=["user"])
        session.add(user)
        session.commit()
        session.refresh(user)

    publish_user_created(user)
    return {"success": True, "data": {"id": user.id}}

@app.post("/v1/auth/login", response_model=dict)
def login(body: UserCreate):
    session = next(get_session())
    try:
        from opentelemetry import trace as otel_trace
        tracer_local = tracer or otel_trace.get_tracer(__name__)
        with tracer_local.start_as_current_span("users.authenticate") as span:
            span.set_attribute("user.email", body.email)
            user = session.exec(select(User).where(User.email == body.email)).first()
            if not user or not verify_password(body.password, user.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            token = create_access_token(user.id, user.email, user.roles)
    except Exception:
        user = session.exec(select(User).where(User.email == body.email)).first()
        if not user or not verify_password(body.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(user.id, user.email, user.roles)

    return {"success": True, "data": {"access_token": token, "token_type": "bearer"}}

import jwt
from .config import settings

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid scheme")
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token error")
    session = next(get_session())
    user = session.get(User, data["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/v1/users/me", response_model=dict)
def me(user: User = Depends(get_current_user)):
    out = {"id": user.id, "email": user.email, "name": user.name, "roles": user.roles}
    return {"success": True, "data": out}

@app.put("/v1/users/me", response_model=dict)
def update_profile(payload: dict, user: User = Depends(get_current_user)):
    session = next(get_session())
    db_user = session.get(User, user.id)
    if "name" in payload:
        db_user.name = payload["name"]
    session.add(db_user)
    session.commit()
    return {"success": True, "data": {"id": db_user.id}}

@app.get("/v1/users", response_model=dict)
def list_users(limit: int = 10, offset: int = 0, q: Optional[str] = None, current: User = Depends(get_current_user)):
    if "admin" not in current.roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    session = next(get_session())
    try:
        from opentelemetry import trace as otel_trace
        tracer_local = tracer or otel_trace.get_tracer(__name__)
        with tracer_local.start_as_current_span("users.list") as span:
            query = select(User)
            if q:
                query = query.where(User.email.contains(q) | User.name.contains(q))
            users = session.exec(query.offset(offset).limit(limit)).all()
    except Exception:
        query = select(User)
        if q:
            query = query.where(User.email.contains(q) | User.name.contains(q))
        users = session.exec(query.offset(offset).limit(limit)).all()

    data = [{"id": u.id, "email": u.email, "name": u.name, "roles": u.roles} for u in users]
    return {"success": True, "data": {"items": data, "limit": limit, "offset": offset}}
