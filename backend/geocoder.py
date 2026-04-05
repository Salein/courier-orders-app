"""Async geocoder for Belarus addresses using Nominatim."""

import logging

import httpx
from models import OrderAddress

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "courier-app/1.0"


async def geocode_address(address: str, countrycodes: str = "by") -> OrderAddress | None:
    """
    Geocode an address and return OrderAddress.
    On failure, returns None.
    """
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": countrycodes or "by",
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                NOMINATIM_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return OrderAddress(raw=address, lat=lat, lon=lon)
            logger.warning("Address not found: %s", address)
            return None
    except httpx.HTTPStatusError as e:
        logger.error("Geocode HTTP %s for '%s': %s", e.response.status_code, address, e.response.text)
    except httpx.RequestError as e:
        logger.error("Geocode request error for '%s': %s", address, e)
    except Exception as e:
        logger.error("Geocode unexpected error for '%s': %s", address, e)
    return None
