import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.modules.alerts.api.alerts_router import router as alerts_router
from app.modules.customer.api.customer_router import router as customer_router
from app.modules.enterprise_extension.api_extension import (
    router as aml_engine_router,
)
from app.modules.enterprise_extension.router import (
    router as enterprise_intelligence_router,
)
from app.modules.identity_access.api.auth_router import router as auth_router
from app.modules.investigations.api.investigations_router import (
    router as investigations_router,
)
from app.modules.kyc.api.kyc_router import router as kyc_router
from app.modules.network_intelligence.api.network_intelligence_router import (
    router as network_intelligence_router,
)
from app.modules.reporting.api.reporting_router import router as reporting_router
from app.modules.risk_scoring.api.risk_scoring_router import (
    router as risk_scoring_router,
)
from app.modules.screening.api.screening_router import router as screening_router
from app.modules.transaction_monitoring.api.transaction_monitoring_router import (
    router as transaction_monitoring_router,
)
from app.shared.auth.dependencies import get_current_user
from app.shared.config import get_settings
from app.shared.database.connection import dispose_engine

logger = logging.getLogger("aml.api")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        yield
    finally:
        dispose_engine()


app = FastAPI(
    title="AML Risk Intelligence Platform",
    version="0.1.0",
    description="Versioned API for the AML/KYC Risk Intelligence Platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

api_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)],
)

for module_router in (
    auth_router,
    customer_router,
    kyc_router,
    screening_router,
    alerts_router,
    investigations_router,
    reporting_router,
    risk_scoring_router,
    transaction_monitoring_router,
    network_intelligence_router,
    enterprise_intelligence_router,
    aml_engine_router,
):
    api_router.include_router(module_router)

app.include_router(api_router)


@app.middleware("http")
async def add_response_headers_and_log_request(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    request_id = uuid4().hex
    started_at = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"

    route = request.scope.get("route")
    route_template = getattr(route, "path", "unmatched")
    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "route": route_template,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
            },
            separators=(",", ":"),
        )
    )
    return response


@app.get("/")
async def root():
    return {
        "name": "AML Risk Intelligence Platform",
        "status": "ok",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }
