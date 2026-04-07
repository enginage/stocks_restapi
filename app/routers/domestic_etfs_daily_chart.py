from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.schemas import DomesticETFsDailyChartOut
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


@router.get("/etf/{etf_id}/latest", response_model=DomesticETFsDailyChartOut)
async def get_latest_chart(
    etf_id: int,
    client: Client = Depends(get_supabase_client),
):
    res = (
        client.schema(schema_stock())
        .table("domestic_etfs_daily_chart")
        .select("id,etf_id,date,open,high,low,close,volume")
        .eq("etf_id", etf_id)
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    if not rows:
        raise HTTPException(status_code=404, detail="Chart data not found")
    return DomesticETFsDailyChartOut.model_validate(rows[0])


@router.get("/etf/{etf_id}/period", response_model=Optional[DomesticETFsDailyChartOut])
async def get_chart_by_period(
    etf_id: int,
    months_ago: int = Query(12, ge=1, le=120),
    client: Client = Depends(get_supabase_client),
):
    """
    N개월 전(30일 근사) 기준일에 가장 가까운 일봉 1건.
    EarlyRetireLab domestic_etfs_daily_chart.get_chart_by_period 와 동일 개념.
    """
    target_date = datetime.now().date() - timedelta(days=months_ago * 30)
    start_date = target_date - timedelta(days=30)
    end_date = target_date + timedelta(days=30)

    res = (
        client.schema(schema_stock())
        .table("domestic_etfs_daily_chart")
        .select("id,etf_id,date,open,high,low,close,volume")
        .eq("etf_id", etf_id)
        .gte("date", start_date.isoformat())
        .lte("date", end_date.isoformat())
        .execute()
    )
    charts = res.data or []
    if not charts:
        return None

    closest = min(
        charts,
        key=lambda x: abs((_parse_date(x["date"]) - target_date).days),
    )
    return DomesticETFsDailyChartOut.model_validate(closest)
