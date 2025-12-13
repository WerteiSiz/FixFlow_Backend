from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from httpx import AsyncClient
from .config import settings
from .middleware import XRequestIDMiddleware
from .auth import get_current_user
from .logging import setup_logging
from .tracing import setup_tracing
import logging

app = FastAPI(title="API Gateway", openapi_prefix="/v1")
app.add_middleware(XRequestIDMiddleware)

# structured logging
setup_logging()
# tracing (optional)
tracer = setup_tracing(app, service_name="api_gateway")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limit (use setting if present)
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = logging.getLogger("gateway")
logger.setLevel(logging.INFO)

async_client = AsyncClient()

def json_ok(data=None):
    return {"success": True, "data": data}

@app.get("/health")
async def health():
    return json_ok({"status": "ok"})

# Proxy helper
async def proxy(request: Request, base_url: str, path: str):
    url = f"{base_url}/{path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.setdefault("X-Request-ID", request.state.request_id)
    body = await request.body()
    # optional tracing span around proxy call
    try:
        from opentelemetry import trace as otel_trace
        tracer_local = tracer or otel_trace.get_tracer(__name__)
        with tracer_local.start_as_current_span("gateway.proxy") as span:
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", url)
            span.set_attribute("request_id", request.state.request_id)
            resp = await async_client.request(method, url, headers=headers, content=body, params=request.query_params)
            try:
                span.set_attribute("http.status_code", resp.status_code)
                span.set_attribute("response_size", len(resp.content) if resp.content is not None else 0)
            except Exception:
                pass
    except Exception:
        resp = await async_client.request(method, url, headers=headers, content=body, params=request.query_params)

    content = resp.content
    return StreamingResponse(content=iter([content]), status_code=resp.status_code, media_type=resp.headers.get("content-type"))

# Open paths: registration and login on users
@app.api_route("/users/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
@limiter.limit("200/minute")
async def users_proxy(path: str, request: Request):
    if (request.method, path) not in [("POST", "auth/register"), ("POST", "auth/login")]:
        await get_current_user(request.headers.get("authorization"), request)
    return await proxy(request, settings.USERS_URL, path)

@app.api_route("/orders/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
@limiter.limit("200/minute")
async def orders_proxy(path: str, request: Request):
    await get_current_user(request.headers.get("authorization"), request)
    return await proxy(request, settings.ORDERS_URL, path)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"success": False, "error": {"code": "internal_error", "message": str(exc)}})
