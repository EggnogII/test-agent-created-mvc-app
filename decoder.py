"""
decoder.py
-----------

Helper functions and data models used by the vehicle decoder application.

The module includes:
  * `Car`: a dataclass representing a vehicle with common attributes.
  * `decode_vin`: a helper that queries the NHTSA vPIC API to decode a VIN
    into a flat JSON dictionary【311902232095331†L68-L99】.
  * `parse_vin_result`: convert the raw vPIC result into a `Car`.
"""

from __future__ import annotations

# Note: Car is defined in models.py to follow MVC separation.
from dataclasses import dataclass, asdict  # kept for backward compatibility of old imports
from typing import Optional, Dict, Any

import requests

__all__ = [
    "decode_vin",
    "parse_vin_result",
]


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

