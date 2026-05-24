"""Charge distribution protocol — stub for future electrostatics."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ChargeDistribution(Protocol):
    """Future: volume (rho), surface (sigma), line (lambda) evaluators."""

    def total_charge(self) -> float: ...
