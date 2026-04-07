from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DomesticETFsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str
    etf_type: Optional[str] = None
    etf_tax_type: Optional[str] = None


class CommonCodeMasterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    code_name: str
    remark: Optional[str] = None


class CommonCodeDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    master_id: int
    detail_code: str
    detail_code_name: str
    order_no: int


class DomesticETFsDailyChartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    etf_id: int
    date: date
    open: int
    high: int
    low: int
    close: int
    volume: int


class DomesticETFsDividendOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    etf_id: int
    record_date: date
    payment_date: date
    dividend_amt: int
    taxable_amt: int
