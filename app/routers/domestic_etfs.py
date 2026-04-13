from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.schemas import DomesticETFsOut
from supabase_client import get_supabase_client, schema_stock

router = APIRouter()


@router.get("", response_model=List[DomesticETFsOut])
async def read_domestic_etfs(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    etf_type: Optional[str] = None,
    etf_tax_type: Optional[str] = None,
    client: Client = Depends(get_supabase_client),
):
    q = (
        client.schema(schema_stock())
        .table("domestic_etfs")
        .select(
            "id,ticker,name,etf_type,etf_tax_type,base_index,asset_manager,compensation,"
            "latest_close,latest_volume,rsi18,rsi30,obv,macd_12_26,macd_signal_9,macd_histogram,"
            "bb_width,bb_percent_b"
        )
    )
    if etf_type:
        q = q.eq("etf_type", etf_type)
    if etf_tax_type:
        q = q.eq("etf_tax_type", etf_tax_type)
    q = q.order("id").range(skip, skip + limit - 1)
    res = q.execute()
    rows = res.data or []
    return [DomesticETFsOut.model_validate(r) for r in rows]


@router.get("/{etf_id}", response_model=DomesticETFsOut)
async def read_domestic_etf(
    etf_id: int,
    client: Client = Depends(get_supabase_client),
):
    res = (
        client.schema(schema_stock())
        .table("domestic_etfs")
        .select(
            "id,ticker,name,etf_type,etf_tax_type,base_index,asset_manager,compensation,"
            "latest_close,latest_volume,rsi18,rsi30,obv,macd_12_26,macd_signal_9,macd_histogram,"
            "bb_width,bb_percent_b"
        )
        .eq("id", etf_id)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    if not rows:
        raise HTTPException(status_code=404, detail="ETF not found")
    return DomesticETFsOut.model_validate(rows[0])
