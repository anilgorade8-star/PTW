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
        Retrieves weather for farm coordinates using Redis cache-aside and Open-Meteo API.
        Returns: (normalized_data, quality_metadata)
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

        # 2. Fetch from Open-Meteo
        logger.info(f"Weather cache miss. Fetching from Open-Meteo for ({latitude}, {longitude})...")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(settings.WEATHER_API_BASE_URL, params=params)
                resp.raise_for_status()
                raw = resp.json()
                current = raw.get("current", {})

                temp = float(current.get("temperature_2m", 25.0))
                humidity = float(current.get("relative_humidity_2m", 65.0))
                precipitation = float(current.get("precipitation", 0.0))
                wind_speed = float(current.get("wind_speed_10m", 5.0))
                weather_code = int(current.get("weather_code", 0))

                desc = WEATHER_CODE_DESCRIPTIONS.get(weather_code, "Partly cloudy")

                # Epidemiological risk indicators based on microclimate
                is_fungal_risk = (humidity >= 80.0) and (14.0 <= temp <= 30.0)
                is_bacterial_risk = (humidity >= 80.0) and (precipitation > 0.1 or humidity >= 90.0) and (temp >= 24.0)
                is_vector_risk = (temp >= 28.0) and (humidity < 60.0)

                normalized = {
                    "temperature_c": temp,
                    "relative_humidity_pct": humidity,
                    "precipitation_mm": precipitation,
                    "wind_speed_kmh": wind_speed,
                    "weather_code": weather_code,
                    "weather_description": desc,
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
            # Fallback safe default climate estimate without crashing assessment
            fallback_norm = {
                "temperature_c": 26.0,
                "relative_humidity_pct": 70.0,
                "precipitation_mm": 0.0,
                "wind_speed_kmh": 6.0,
                "weather_code": 1,
                "weather_description": "Data unavailable (using seasonal baseline)",
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
