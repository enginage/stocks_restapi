import os

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    common_code_details,
    common_code_masters,
    domestic_etfs,
    domestic_etfs_daily_chart,
    domestic_etfs_dividend,
)

app = FastAPI(
    title="Stocks Rest API",
    description="국내 ETF·공통코드·일봉·배당 REST API (Supabase, Vercel)",
    version="1.0.0",
)

_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins:
    _cors = [o.strip() for o in _origins.split(",") if o.strip()]
else:
    _cors = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 외부 URL: {ORIGIN}/api/v1/... (EarlyRetireLab 백엔드와 동일 경로)
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(domestic_etfs.router, prefix="/domestic-etfs", tags=["domestic-etfs"])
api_v1.include_router(
    domestic_etfs_daily_chart.router,
    prefix="/domestic-etfs-daily-chart",
    tags=["domestic-etfs-daily-chart"],
)
api_v1.include_router(
    domestic_etfs_dividend.router,
    prefix="/domestic-etfs-dividend",
    tags=["domestic-etfs-dividend"],
)
api_v1.include_router(
    common_code_masters.router,
    prefix="/common-code-masters",
    tags=["common-code-masters"],
)
api_v1.include_router(
    common_code_details.router,
    prefix="/common-code-details",
    tags=["common-code-details"],
)
app.include_router(api_v1)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
