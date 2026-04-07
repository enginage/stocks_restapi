"""
모듈 단일 Supabase 클라이언트 재사용 (Vercel 웜 인스턴스 내).
요청마다 create_client 하지 않음.
"""
import asyncio
import os
from typing import Optional

from fastapi import HTTPException
from supabase import Client, create_client

_supabase_client: Optional[Client] = None
_client_lock = asyncio.Lock()


async def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    async with _client_lock:
        if _supabase_client is not None:
            return _supabase_client

        url = os.getenv("SUPABASE_URL", "").strip()
        key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
            or os.getenv("SUPABASE_ANON_KEY", "").strip()
        )
        if not url or not key:
            raise HTTPException(
                status_code=500,
                detail="Supabase config missing: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)",
            )

        # create_client 는 동기 — 초기 1회만 실행
        _supabase_client = create_client(url, key)
        return _supabase_client


def schema_stock() -> str:
    return os.getenv("SUPABASE_SCHEMA_STOCK", "stock").strip() or "stock"


def schema_basic() -> str:
    return os.getenv("SUPABASE_SCHEMA_BASIC", "basic").strip() or "basic"
