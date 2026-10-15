"""ExportIQ — Product and destination country schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    hs_code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class DestinationCountryRead(BaseModel):
    id: int
    iso_code: str
    iso_code_2: str
    name: str
    region: Optional[str] = None
    trade_bloc: Optional[str] = None

    model_config = {"from_attributes": True}
