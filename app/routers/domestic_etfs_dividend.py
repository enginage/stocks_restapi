from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.schemas import DomesticETFsDividendOut
from supabase_client import get_supabase_client, schema_stock

router = APIRouter()


def _parse_date(value) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise ValueError(f"bad date: {value!r}")


@router.get("/etf/{etf_id}/period", response_model=List[DomesticETFsDividendOut])
async def get_dividends_by_period(
    etf_id: int,
    months_ago: int = Query(12, ge=1, le=120),
    client: Client = Depends(get_supabase_client),
):
    """
    payment_date >= (오늘 - months_ago * 30일) 인 배당만, record_date 내림차순.
    """
    target_date = datetime.now().date() - timedelta(days=months_ago * 30)

    res = (
        client.schema(schema_stock())
        .table("domestic_etfs_dividend")
        .select("id,etf_id,record_date,payment_date,dividend_amt,taxable_amt")
        .eq("etf_id", etf_id)
        .gte("payment_date", target_date.isoformat())
        .order("record_date", desc=True)
        .limit(1000)
        .execute()
    )
    rows = res.data or []
    # 백엔드와 동일하게 record_date 기준 내림차순 보장
    rows.sort(key=lambda r: _parse_date(r["record_date"]), reverse=True)
    return [DomesticETFsDividendOut.model_validate(r) for r in rows]


@router.get("/etf/{etf_id}", response_model=List[DomesticETFsDividendOut])
async def get_dividends_by_etf(
    etf_id: int,
    client: Client = Depends(get_supabase_client),
):
    """ETF 전체 배당 (최대 1000건, record_date desc)."""
    res = (
        client.schema(schema_stock())
        .table("domestic_etfs_dividend")
        .select("id,etf_id,record_date,payment_date,dividend_amt,taxable_amt")
        .eq("etf_id", etf_id)
        .order("record_date", desc=True)
        .limit(1000)
        .execute()
    )
    rows = res.data or []
    return [DomesticETFsDividendOut.model_validate(r) for r in rows]
