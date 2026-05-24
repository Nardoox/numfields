"""Carve — reduce dimension by extracting the boundary of a body."""

from __future__ import annotations

from collections.abc import Callable

from numfields.domain.bodies.base import GeometricBody
from numfields.domain.bodies.line.circle import CircleBody
from numfields.domain.bodies.line.rect_outline import RectOutlineBody
from numfields.domain.bodies.surface.box_shell import BoxShellBody
from numfields.domain.bodies.surface.cylinder_shell import CylinderShellBody
from numfields.domain.bodies.surface.sphere_shell import SphereShellBody
from numfields.domain.bodies.volume.box import BoxBody
from numfields.domain.bodies.volume.cylinder import CylinderBody
from numfields.domain.bodies.volume.sphere import SphereBody
from numfields.domain.types import Dimension
from numfields.domain.bodies.surface.disk import DiskBody
from numfields.domain.bodies.surface.rectangle import RectangleBody

CarveFactory = Callable[[GeometricBody], GeometricBody]


def _carve_sphere(body: GeometricBody) -> GeometricBody:
    assert isinstance(body, SphereBody)
    return SphereShellBody(body.name, radius=body.radius)


def _carve_box(body: GeometricBody) -> GeometricBody:
    assert isinstance(body, BoxBody)
    return BoxShellBody(
        body.name,
        size_x=body.size_x,
        size_y=body.size_y,
        size_z=body.size_z,
    )


def _carve_cylinder(body: GeometricBody) -> GeometricBody:
    assert isinstance(body, CylinderBody)
    return CylinderShellBody(body.name, radius=body.radius, height=body.height)


def _carve_disk(body: GeometricBody) -> GeometricBody:
    assert isinstance(body, DiskBody)
    return CircleBody(body.name, radius=body.radius)


def _carve_rectangle(body: GeometricBody) -> GeometricBody:
    assert isinstance(body, RectangleBody)
    return RectOutlineBody(body.name, width=body.width, height=body.height)


_CARVE_MAP: dict[tuple[str, Dimension], CarveFactory] = {
    ("sphere", Dimension.VOLUME): _carve_sphere,
    ("box", Dimension.VOLUME): _carve_box,
    ("cylinder", Dimension.VOLUME): _carve_cylinder,
    ("disk", Dimension.SURFACE): _carve_disk,
    ("rectangle", Dimension.SURFACE): _carve_rectangle,
}


def can_carve(body: GeometricBody) -> bool:
    return (body.type_id, body.dimension) in _CARVE_MAP


def carve_body(body: GeometricBody) -> GeometricBody:
    if body.dimension == Dimension.LINE:
        raise ValueError("Cannot carve a 1D object")

    factory = _CARVE_MAP.get((body.type_id, body.dimension))
    if factory is None:
        raise ValueError(f"Cannot carve body type: {body.type_id}")

    return factory(body)
