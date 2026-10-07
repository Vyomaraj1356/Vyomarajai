"""Provider-neutral geospatial capability boundary.

Adapters must return provenance and must never invent location data.
"""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class GeoResult:
    source: str
    latitude: float | None
    longitude: float | None
    accuracy_m: float | None
    timestamp: str
    provenance: str

class GeoProvider(Protocol):
    name: str
    def locate(self, target: str, authorization_id: str) -> GeoResult: ...

class GeospatialGateway:
    def __init__(self, providers: list[GeoProvider]):
        self.providers = providers

    def locate_authorized(self, target: str, authorization_id: str) -> GeoResult:
        if not authorization_id:
            raise PermissionError("location authorization required")
        for provider in self.providers:
            result = provider.locate(target, authorization_id)
            if result.latitude is not None and result.longitude is not None:
                return result
        raise RuntimeError("no authorized location provider returned a result")
