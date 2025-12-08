from fastapi import FastAPI, Depends, HTTPException, Header
from .db import init_db, get_session
from .models import Order
from .schemas import OrderCreate, OrderOut
from .auth import get_current_user
from .events import publish_order_created, publish_order_status_changed
from sqlmodel import select
import json

app = FastAPI(title="Orders Service")

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/v1/orders", response_model=dict)
def create_order(payload: OrderCreate, user=Depends(get_current_user)):
    session = next(get_session())
    order = Order(user_id=user["sub"], items=json.dumps(payload.items), total=payload.total)
    session.add(order)
    session.commit()
    session.refresh(order)
    publish_order_created(order)
    return {"success": True, "data": {"id": order.id}}

@app.get("/v1/orders/{order_id}", response_model=dict)
def get_order(order_id: str, user=Depends(get_current_user)):
    session = next(get_session())
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    if order.user_id != user["sub"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"success": True, "data": {
        "id": order.id,
        "user_id": order.user_id,
        "items": json.loads(order.items),
        "status": order.status,
        "total": order.total
    }}

@app.get("/v1/orders", response_model=dict)
def list_orders(limit: int = 10, offset: int = 0, sort: str = "created_at", user=Depends(get_current_user)):
    session = next(get_session())
    q = select(Order).where(Order.user_id == user["sub"]).offset(offset).limit(limit)
    orders = session.exec(q).all()
    items = []
    for o in orders:
        items.append({"id": o.id, "items": json.loads(o.items), "status": o.status, "total": o.total})
    return {"success": True, "data": {"items": items, "limit": limit, "offset": offset}}

@app.patch("/v1/orders/{order_id}/status", response_model=dict)
def update_status(order_id: str, payload: dict, user=Depends(get_current_user)):
    session = next(get_session())
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    if order.user_id != user["sub"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Forbidden")
    new_status = payload.get("status")
    if new_status not in ["created", "in_work", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    order.status = new_status
    session.add(order)
    session.commit()
    publish_order_status_changed(order)
    return {"success": True, "data": {"id": order.id, "status": order.status}}

@app.delete("/v1/orders/{order_id}", response_model=dict)
def cancel_order(order_id: str, user=Depends(get_current_user)):
    session = next(get_session())
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    if order.user_id != user["sub"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Forbidden")
    order.status = "cancelled"
    session.add(order)
    session.commit()
    publish_order_status_changed(order)
    return {"success": True, "data": {"id": order.id, "status": order.status}}
