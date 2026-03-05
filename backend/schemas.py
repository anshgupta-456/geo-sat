from pydantic import BaseModel
from typing import Optional

class RegionBase(BaseModel):
    name: str
    admin_level: Optional[str]=None

class RegionCreate(RegionBase):
    latitude: float
    longitude: float

class RegionResponse(RegionBase):
    id: int
    model_config={"from_attributes": True}