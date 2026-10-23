import json
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.redis_client import RedisManager

WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog and depositing rime fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm"
}

class WeatherService:
    @staticmethod
    def _cache_key(lat: float, lon: float) -> str:
        # Rounded to 2 decimals (~1.1 km resolution) for optimal spatial cache reuse
        return f"kg:weather:v1:{round(lat, 2)}:{round(lon, 2)}"

    @classmethod
    async def get_farm_weather(cls, latitude: float, longitude: float) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Retrieves weather and agricultural soil moisture parameters for farm coordinates
        using Redis cache-aside and Open-Meteo API.
        """
        cache_key = cls._cache_key(latitude, longitude)
        redis_client = RedisManager.get_client()

        # 1. Cache-aside check
        if redis_client is not None:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    payload = json.loads(cached)
                    logger.info("Weather cache hit in Redis", extra={"extra_data": {"cache_key": cache_key}})
                    payload["quality_metadata"]["is_cached"] = True
                    return payload["normalized_data"], payload["quality_metadata"]
            except Exception as e:
                logger.warning(f"Weather cache retrieval failed: {e}")

        # 2. Fetch from Open-Meteo with comprehensive soil moisture & rain parameters
        logger.info(f"Weather cache miss. Fetching from Open-Meteo for ({latitude}, {longitude})...")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,relative_humidity_2m,rain,soil_moisture_3_to_9cm,soil_moisture_0_to_1cm,precipitation,precipitation_probability",
            "timezone": "auto"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(settings.WEATHER_API_BASE_URL, params=params)
                resp.raise_for_status()
                raw = resp.json()
                current = raw.get("current", {})
                hourly = raw.get("hourly", {})

                temp = float(current.get("temperature_2m", 25.0))
                humidity = float(current.get("relative_humidity_2m", 65.0))
                precipitation = float(current.get("precipitation", 0.0))
                wind_speed = float(current.get("wind_speed_10m", 5.0))
                weather_code = int(current.get("weather_code", 0))

                desc = WEATHER_CODE_DESCRIPTIONS.get(weather_code, "Partly cloudy")

                # Extract hourly soil moisture and precipitation probability
                soil_surf: Optional[float] = None
                soil_root: Optional[float] = None
                precip_prob: Optional[float] = None
                rain_mm: Optional[float] = None

                if hourly:
                    surf_list = hourly.get("soil_moisture_0_to_1cm", [])
                    root_list = hourly.get("soil_moisture_3_to_9cm", [])
                    prob_list = hourly.get("precipitation_probability", [])
                    rain_list = hourly.get("rain", [])

                    if surf_list and len(surf_list) > 0:
                        soil_surf = float(surf_list[0])
                    if root_list and len(root_list) > 0:
                        soil_root = float(root_list[0])
                    if prob_list and len(prob_list) > 0:
                        precip_prob = float(prob_list[0])
                    if rain_list and len(rain_list) > 0:
                        rain_mm = float(rain_list[0])

                # Epidemiological risk indicators based on microclimate + soil moisture
                is_high_soil_wetness = soil_root is not None and soil_root > 0.35
                is_fungal_risk = (humidity >= 80.0 or is_high_soil_wetness) and (14.0 <= temp <= 30.0)
                is_bacterial_risk = (humidity >= 80.0 or (precip_prob is not None and precip_prob > 60)) and (precipitation > 0.1 or humidity >= 88.0) and (temp >= 24.0)
                is_vector_risk = (temp >= 28.0) and (humidity < 60.0)

                normalized = {
                    "temperature_c": temp,
                    "relative_humidity_pct": humidity,
                    "precipitation_mm": precipitation,
                    "wind_speed_kmh": wind_speed,
                    "weather_code": weather_code,
                    "weather_description": desc,
                    "soil_moisture_surface_m3": soil_surf,
                    "soil_moisture_root_zone_m3": soil_root,
                    "precipitation_probability_pct": precip_prob,
                    "rain_mm": rain_mm,
                    "is_risk_favorable_for_fungal": is_fungal_risk,
                    "is_risk_favorable_for_bacterial": is_bacterial_risk,
                    "is_risk_favorable_for_vector": is_vector_risk
                }

                quality = {
                    "provider": "open-meteo",
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation": raw.get("elevation", 0),
                    "is_cached": False,
                    "cache_ttl_seconds": settings.WEATHER_CACHE_TTL_SECONDS,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                }

                # 3. Store in Redis
                if redis_client is not None:
                    try:
                        to_cache = {"normalized_data": normalized, "quality_metadata": quality}
                        await redis_client.set(cache_key, json.dumps(to_cache), ex=settings.WEATHER_CACHE_TTL_SECONDS)
                    except Exception as e:
                        logger.warning(f"Failed to store weather in Redis: {e}")

                return normalized, quality

        except Exception as e:
            logger.error(f"Open-Meteo weather fetch error: {e}")
            fallback_norm = {
                "temperature_c": 26.0,
                "relative_humidity_pct": 70.0,
                "precipitation_mm": 0.0,
                "wind_speed_kmh": 6.0,
                "weather_code": 1,
                "weather_description": "Data unavailable (using seasonal baseline)",
                "soil_moisture_surface_m3": None,
                "soil_moisture_root_zone_m3": None,
                "precipitation_probability_pct": None,
                "rain_mm": None,
                "is_risk_favorable_for_fungal": False,
                "is_risk_favorable_for_bacterial": False,
                "is_risk_favorable_for_vector": False
            }
            fallback_qual = {
                "provider": "fallback_baseline",
                "is_cached": False,
                "error": str(e),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            return fallback_norm, fallback_qual
