"""GeometricBody ABC — extensible scene objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from numfields.domain.charge import ChargeInputMode, HomogeneousCharge
from numfields.domain.types import BodyId, Dimension, Transform, new_body_id


@dataclass(frozen=True)
class MeshSpec:
    builder: str
    args: dict[str, Any]


class GeometricBody(ABC):
    def __init__(
        self,
        name: str,
        *,
        body_id: BodyId | None = None,
        transform: Transform | None = None,
        charge: HomogeneousCharge | None = None,
    ) -> None:
        self.id = body_id or new_body_id()
        self.name = name
        self.transform = transform or Transform()
        self._charge = charge or HomogeneousCharge()

    @property
    @abstractmethod
    def type_id(self) -> str: ...

    @property
    @abstractmethod
    def dimension(self) -> Dimension: ...

    @abstractmethod
    def parameters(self) -> dict[str, float]: ...

    @abstractmethod
    def set_parameter(self, key: str, value: float) -> None: ...

    @abstractmethod
    def mesh_spec(self) -> MeshSpec: ...

    def charge(self) -> HomogeneousCharge:
        return self._charge

    def measure(self) -> float:
        from numfields.geometry.measure import body_measure

        return body_measure(self)

    def set_charge_density(self, value: float) -> None:
        self._charge.set_density(self, value)

    def set_total_charge(self, value: float) -> None:
        self._charge.set_total_charge(self, value)

    def set_charge_mode(self, mode: ChargeInputMode) -> None:
        self._charge.set_mode(self, mode)

    def sync_charge_after_geometry_change(self) -> None:
        self._charge.sync_after_geometry_change(self)

    def parameter_keys(self) -> list[str]:
        return list(self.parameters().keys())

    def mesh_cache_key(self) -> tuple[Any, ...]:
        params = tuple(sorted(self.parameters().items()))
        spec = self.mesh_spec()
        spec_key = (spec.builder, tuple(sorted((k, v) for k, v in spec.args.items())))
        return (self.type_id, params, spec_key)
