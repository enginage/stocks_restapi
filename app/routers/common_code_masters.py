from typing import List

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.schemas import CommonCodeMasterOut
from supabase_client import get_supabase_client, schema_basic

router = APIRouter()


@router.get("", response_model=List[CommonCodeMasterOut])
async def read_common_code_masters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client: Client = Depends(get_supabase_client),
):
    res = (
        client.schema(schema_basic())
        .table("common_code_master")
        .select("id,code,code_name,remark")
        .order("id")
        .range(skip, skip + limit - 1)
        .execute()
    )
    rows = res.data or []
    return [CommonCodeMasterOut.model_validate(r) for r in rows]
