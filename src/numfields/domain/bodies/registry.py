"""Body type registry — register factories for UI and serialization."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from numfields.domain.types import Dimension

if TYPE_CHECKING:
    from numfields.domain.bodies.base import GeometricBody

BodyFactory = Callable[..., "GeometricBody"]

_REGISTRY: dict[str, tuple[Dimension, BodyFactory, str]] = {}


def register_body(
    type_id: str,
    *,
    dimension: Dimension,
    display_name: str | None = None,
) -> Callable[[BodyFactory], BodyFactory]:
    def decorator(factory: BodyFactory) -> BodyFactory:
        _REGISTRY[type_id] = (dimension, factory, display_name or type_id.title())
        return factory

    return decorator


def create_body(type_id: str, **kwargs: object) -> "GeometricBody":
    if type_id not in _REGISTRY:
        raise KeyError(f"Unknown body type: {type_id}")
    _, factory, _ = _REGISTRY[type_id]
    return factory(**kwargs)


def list_body_types() -> list[tuple[str, Dimension, str]]:
    return [(tid, dim, name) for tid, (dim, _, name) in sorted(_REGISTRY.items())]


def body_types_by_dimension() -> dict[Dimension, list[tuple[str, str]]]:
    result: dict[Dimension, list[tuple[str, str]]] = {
        Dimension.VOLUME: [],
        Dimension.SURFACE: [],
        Dimension.LINE: [],
    }
    for type_id, dimension, display_name in list_body_types():
        result[dimension].append((type_id, display_name))
    return result
