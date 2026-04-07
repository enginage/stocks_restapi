from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.schemas import CommonCodeDetailOut
from supabase_client import get_supabase_client, schema_basic

router = APIRouter()


@router.get("/", response_model=List[CommonCodeDetailOut])
async def read_common_code_details(
    master_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    client: Client = Depends(get_supabase_client),
):
    q = (
        client.schema(schema_basic())
        .table("common_code_detail")
        .select("id,master_id,detail_code,detail_code_name,order_no")
    )
    if master_id is not None:
        q = q.eq("master_id", master_id)
    q = q.order("order_no").range(skip, skip + limit - 1)
    res = q.execute()
    rows = res.data or []
    return [CommonCodeDetailOut.model_validate(r) for r in rows]
