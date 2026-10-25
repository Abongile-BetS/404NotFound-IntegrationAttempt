import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.customer.api.customer_router import router as customer_router
from app.modules.identity_access.api.auth_router import router as auth_router
from app.modules.kyc.api.kyc_router import router as kyc_router
from app.modules.risk_scoring.api.risk_scoring_router import router as risk_scoring_router
from app.modules.screening.api.screening_router import router as screening_router
from app.modules.alerts.api.alerts_router import router as alerts_router
from app.modules.investigations.api.investigations_router import router as investigations_router
from app.modules.reporting.api.reporting_router import router as reporting_router
from app.modules.transaction_monitoring.api.transaction_monitoring_router import router as transaction_monitoring_router
from app.modules.network_intelligence.api.network_intelligence_router import router as network_intelligence_router

app = FastAPI(
    title="AML Risk Intelligence Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
):
    app.include_router(module_router, prefix="/api/v1")

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


# Additive enterprise intelligence extension (existing routers unchanged)
from app.modules.enterprise_extension.router import router as enterprise_intelligence_router
app.include_router(enterprise_intelligence_router, prefix="/api/v1")

# Additive intelligence engine: existing application routes remain unchanged.
from app.modules.enterprise_extension.api_extension import router as aml_engine_router
app.include_router(aml_engine_router, prefix="/api/v1")
