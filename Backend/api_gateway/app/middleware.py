from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging
from .logging import request_id_ctx

logger = logging.getLogger("gateway")


class XRequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            # attach request_id to current OpenTelemetry span if available
            try:
                from opentelemetry import trace as otel_trace
                span = otel_trace.get_current_span()
                if span is not None:
                    span.set_attribute("request_id", request_id)
            except Exception:
                pass
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = request_id
        logger.info("request", extra={"path": request.url.path})
        return response
