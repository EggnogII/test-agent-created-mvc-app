"""
models.py
-----------

Defines simple data models used by the vehicle decoder application.  In a
typical MVC architecture the models encapsulate data and business
logic while remaining independent from the controller (Flask app) and
view (HTML templates).  Here we provide a single `Car` data class
representing vehicle attributes.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict

__all__ = ["Car"]


@dataclass
class Car:
    """Representation of a vehicle.

    Each attribute is optional because not all decoding services
    return every possible field.  Use the `to_dict()` method to
    serialize an instance to a dict while omitting undefined fields.
    """

    vin: Optional[str] = None
    year: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    body_style: Optional[str] = None
    engine: Optional[str] = None
    assembly: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict containing only attributes that are not None or empty."""
        return {k: v for k, v in asdict(self).items() if v not in (None, "")}