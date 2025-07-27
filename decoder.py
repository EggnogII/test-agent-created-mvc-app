"""
decoder.py
---------------

This module contains helper functions and the Car data model used by
the vehicle decoder application.  Separating these elements into a
dedicated module makes it easier to maintain and test the core
decoding logic independently of the Flask web application layer.

The module includes:
  * `Car`: a dataclass representing a vehicle with common
    attributes.
  * `decode_vin`: a helper that queries the NHTSA vPIC API to
    decode a VIN into a flat JSON dictionary【311902232095331†L68-L99】.
  * `decode_plate`: a helper that queries the CarsXE Plate
    Decoder API.  The CarsXE documentation requires `plate`, `state`,
    `format` and `key` parameters for the request【545417615960480†L75-L86】.
  * `parse_vin_result`: convert the raw vPIC result into a `Car`.
  * `parse_plate_result`: convert the CarsXE result into a `Car`.

To enable licence‑plate decoding, set the `CARSXE_API_KEY`
environment variable before importing this module or pass your API
key explicitly when calling `decode_plate`.
"""

from __future__ import annotations

import os
# Note: Car is defined in models.py to follow MVC separation.
from dataclasses import dataclass, asdict  # kept for backward compatibility of old imports
from typing import Optional, Dict, Any

import requests

__all__ = [
    "decode_vin",
    "decode_plate",
    "parse_vin_result",
    "parse_plate_result",
]


# Read the CarsXE API key from the environment.  If undefined the
# `decode_plate` function will return an error message instead of
# making a request.
CARSXE_API_KEY: Optional[str] = os.environ.get("CARSXE_API_KEY")


# Import the Car dataclass from the models module.  Keeping the import
# here prevents circular dependencies and ensures that callers can
# continue to import Car from decoder for backward compatibility.  If
# `models.py` isn't available (e.g., running as a standalone script),
# define a minimal Car dataclass locally as a fallback.
try:
    from .models import Car  # type: ignore
except Exception:
    @dataclass
    class Car:  # type: ignore
        """Fallback Car dataclass when models isn't available."""

        vin: Optional[str] = None
        year: Optional[str] = None
        make: Optional[str] = None
        model: Optional[str] = None
        body_style: Optional[str] = None
        engine: Optional[str] = None
        assembly: Optional[str] = None
        description: Optional[str] = None

        def to_dict(self) -> Dict[str, Any]:
            return {k: v for k, v in asdict(self).items() if v not in (None, "")}


def decode_vin(vin: str, model_year: Optional[str] = None) -> Dict[str, Any]:
    """Decode a VIN using the NHTSA vPIC API.

    Args:
        vin: A 17‑character vehicle identification number.
        model_year: Optional model year to improve decoding accuracy.

    Returns:
        A flat dictionary representing decoded values from the vPIC
        API【311902232095331†L68-L99】.

    Raises:
        requests.RequestException: on network failures.
        ValueError: if the API returns an unexpected result.
    """
    base_url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"
    url = f"{base_url}{vin}"
    params: Dict[str, str] = {"format": "json"}
    if model_year:
        params["modelyear"] = model_year
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    results = data.get("Results", [])
    if not results:
        raise ValueError("Unexpected response structure from NHTSA API")
    return results[0]


def decode_plate(plate: str, state: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Decode a licence plate using the CarsXE Plate Decoder API.

    Args:
        plate: The licence plate number (letters and digits).
        state: Two‑letter state or province code.
        api_key: API key for CarsXE; defaults to the module‑level key.

    Returns:
        A dictionary returned by the CarsXE API, or a dict with an
        `error` key if no API key is configured or the request fails.
    """
    key = api_key or CARSXE_API_KEY
    if not key:
        return {
            "error": (
                "License plate decoding requires a CarsXE API key. "
                "Set the CARSXE_API_KEY environment variable to enable this feature."
            )
        }
    url = "https://api.carsxe.com/platedecoder"
    params = {
        "plate": plate,
        "state": state,
        "format": "json",
        "key": key,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
    except Exception as exc:
        return {"error": str(exc)}
    if response.status_code != 200:
        return {"error": f"CarsXE API returned status {response.status_code}: {response.text}"}
    try:
        return response.json()
    except Exception:
        return {"error": "CarsXE API returned an unreadable response"}


def parse_vin_result(vin: str, result: Dict[str, Any]) -> Car:
    """Convert a vPIC response into a `Car` object."""
    car = Car()
    car.vin = vin
    car.year = result.get("ModelYear") or None
    car.make = result.get("Make") or None
    car.model = result.get("Model") or None
    car.body_style = result.get("BodyClass") or None
    # Build a simple engine description
    cylinders = result.get("EngineCylinders") or ""
    disp_l = result.get("DisplacementL") or ""
    fuel = result.get("FuelTypePrimary") or ""
    parts: list[str] = []
    if cylinders:
        parts.append(f"{cylinders}-cyl")
    if disp_l:
        parts.append(f"{disp_l}L")
    if fuel:
        parts.append(fuel)
    car.engine = " ".join(parts) if parts else None
    car.assembly = result.get("PlantCountry") or None
    description = result.get("Series") or result.get("Trim") or None
    car.description = description
    return car


def parse_plate_result(data: Dict[str, Any]) -> Any:
    """Convert a CarsXE response into a `Car`.

    If the CarsXE response indicates an error (e.g., success=false), the
    original dictionary is returned unchanged.
    """
    if not isinstance(data, dict) or not data.get("success", False):
        return data
    car = Car()
    car.vin = data.get("vin")
    car.year = data.get("RegistrationYear")
    car.make = data.get("CarMake")
    car.model = data.get("CarModel")
    car.body_style = data.get("BodyStyle")
    car.engine = data.get("EngineSize")
    car.assembly = data.get("assembly")
    car.description = data.get("Description")
    return car