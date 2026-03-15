import logging
import os
import time

import requests
from geopy.geocoders import Nominatim

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "..", "dataset", "kumbh_rag_dataset", "maps", "nashik_pois.txt")
)
OVERPASS_QUERY = """
[out:json][timeout:60];
(
  node["amenity"="hospital"](19.85,73.70,20.10,73.95);
  node["amenity"="police"](19.85,73.70,20.10,73.95);
  node["amenity"="fire_station"](19.85,73.70,20.10,73.95);
  node["amenity"="place_of_worship"](19.85,73.70,20.10,73.95);
  node["tourism"="attraction"](19.85,73.70,20.10,73.95);
  node["railway"="station"](19.85,73.70,20.10,73.95);
);
out body;
"""

geolocator = Nominatim(user_agent="kumbh_rag_2027")


def get_address(lat: float, lon: float) -> str:
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        if location and location.address:
            return location.address
        return "Address not found"
    except Exception as exc:
        logger.warning("Reverse geocoding failed for (%s, %s): %s", lat, lon, exc)
        return "Address not found"


def main() -> int:
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    logger.info("Fetching Nashik POIs from OpenStreetMap...")

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": OVERPASS_QUERY},
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch POIs from Overpass API: %s", exc)
        return 1

    elements = response.json().get("elements", [])
    logger.info("Got %s POIs; starting reverse geocoding.", len(elements))

    lines = ["NASHIK POI DATA - OpenStreetMap + Reverse Geocoding"]

    for i, element in enumerate(elements, start=1):
        tags = element.get("tags", {})
        name = tags.get("name", tags.get("name:en", "Unknown"))
        kind = tags.get("amenity") or tags.get("tourism") or tags.get("railway") or "misc"
        lat = element.get("lat", "")
        lon = element.get("lon", "")
        phone = tags.get("phone", tags.get("contact:phone", ""))

        address = get_address(lat, lon)
        time.sleep(1)

        entry = (
            f"City        : Nashik\n"
            f"Name        : {name}\n"
            f"Type        : {kind}\n"
            f"Address     : {address}\n"
            + (f"Phone       : {phone}\n" if phone else "")
            + f"Coordinates : {lat}, {lon}\n"
            f"---"
        )
        lines.append(entry)
        logger.info("[%s/%s] %s - %s", i, len(elements), name, kind)

    with open(SAVE_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    logger.info("Saved %s POIs to %s", len(elements), SAVE_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())