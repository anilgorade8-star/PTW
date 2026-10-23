from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class NormalizedWeatherData(BaseModel):
    temperature_c: float
    relative_humidity_pct: float
    precipitation_mm: float
    wind_speed_kmh: float
    weather_code: int
    weather_description: str
    soil_moisture_surface_m3: Optional[float] = None
    soil_moisture_root_zone_m3: Optional[float] = None
    precipitation_probability_pct: Optional[float] = None
    rain_mm: Optional[float] = None
    is_risk_favorable_for_fungal: bool = False
    is_risk_favorable_for_bacterial: bool = False
    is_risk_favorable_for_vector: bool = False

class WeatherSnapshotResponse(BaseModel):
    id: Optional[str] = None
    farmId: str
    provider: str = "open-meteo"
    fetchedAt: datetime
    validTime: datetime
    normalizedData: NormalizedWeatherData
    qualityMetadata: Dict[str, Any] = Field(default_factory=dict)
