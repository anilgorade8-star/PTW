from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class FarmLocation(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: Optional[str] = Field(default="")
    district: Optional[str] = Field(default="")
    state: Optional[str] = Field(default="")

class FarmCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    location: FarmLocation
    cropTypes: List[str] = Field(default=["tomato"], min_length=1)
    sizeInAcres: Optional[float] = Field(default=None, ge=0.01)

class FarmUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    location: Optional[FarmLocation] = None
    cropTypes: Optional[List[str]] = None
    sizeInAcres: Optional[float] = None

class FarmResponse(BaseModel):
    id: str
    ownerUserId: str
    name: str
    location: FarmLocation
    cropTypes: List[str]
    sizeInAcres: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime
