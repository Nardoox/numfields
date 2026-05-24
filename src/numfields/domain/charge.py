"""Homogeneous charge distribution — density or total-charge input."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from numfields.domain.bodies.base import GeometricBody

_MEASURE_EPS = 1e-12


class ChargeInputMode(Enum):
    DENSITY = "density"
    TOTAL = "total"


@runtime_checkable
class ChargeDistribution(Protocol):
    def total_charge(self, body: GeometricBody) -> float: ...


@dataclass
class HomogeneousCharge:
    mode: ChargeInputMode = ChargeInputMode.DENSITY
    density: float = 0.0
    total_charge: float = 0.0

    def total_charge_value(self, body: GeometricBody) -> float:
        return self.density * body.measure()

    def set_density(self, body: GeometricBody, value: float) -> None:
        self.mode = ChargeInputMode.DENSITY
        self.density = value
        self.total_charge = self.total_charge_value(body)

    def set_total_charge(self, body: GeometricBody, value: float) -> None:
        self.mode = ChargeInputMode.TOTAL
        self.total_charge = value
        measure = body.measure()
        self.density = value / measure if measure > _MEASURE_EPS else 0.0

    def set_mode(self, body: GeometricBody, mode: ChargeInputMode) -> None:
        if self.mode == mode:
            return
        if mode == ChargeInputMode.TOTAL:
            self.total_charge = self.total_charge_value(body)
        else:
            self.density = self.density
            self.total_charge = self.total_charge_value(body)
        self.mode = mode

    def sync_after_geometry_change(self, body: GeometricBody) -> None:
        if self.mode == ChargeInputMode.TOTAL:
            measure = body.measure()
            self.density = self.total_charge / measure if measure > _MEASURE_EPS else 0.0
        else:
            self.total_charge = self.total_charge_value(body)
