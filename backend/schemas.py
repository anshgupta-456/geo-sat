from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegionBase(BaseModel):
    name: str
    admin_level: Optional[str]=None

class RegionCreate(RegionBase):
    latitude: float
    longitude: float

class RegionResponse(RegionBase):
    id: int
    model_config={"from_attributes": True}
class WeatherBase(BaseModel):
    region_id: int
    source: str
    rainfall: float
    temp: float
    humidity: float
class WeatherCreate(WeatherBase):
    pass 
class WeatherResponse(WeatherBase):
    id: int
    timestamp: datetime
    model_config={"from_attributes": True}
