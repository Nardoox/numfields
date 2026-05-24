"""Scene snapshot capture and restore for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass

import glm

from numfields.domain.bodies.base import GeometricBody
from numfields.domain.bodies.registry import create_body
from numfields.domain.charge import ChargeInputMode, HomogeneousCharge
from numfields.domain.types import BodyId, Transform


@dataclass(frozen=True)
class TransformSnapshot:
    px: float
    py: float
    pz: float
    qx: float
    qy: float
    qz: float
    qw: float
    scale: float


@dataclass(frozen=True)
class BodySnapshot:
    body_id: str
    type_id: str
    name: str
    transform: TransformSnapshot
    parameters: tuple[tuple[str, float], ...]
    expressions: tuple[tuple[str, str], ...]
    charge_mode: str
    charge_density: float
    total_charge: float


@dataclass(frozen=True)
class SceneSnapshot:
    bodies: tuple[BodySnapshot, ...]
    selected_id: str | None


def _capture_transform(transform: Transform) -> TransformSnapshot:
    p = transform.position
    q = transform.rotation
    return TransformSnapshot(p.x, p.y, p.z, q.x, q.y, q.z, q.w, transform.scale)


def _restore_transform(snap: TransformSnapshot) -> Transform:
    return Transform(
        position=glm.vec3(snap.px, snap.py, snap.pz),
        rotation=glm.quat(snap.qw, snap.qx, snap.qy, snap.qz),
        scale=snap.scale,
    )


def _capture_body(body: GeometricBody) -> BodySnapshot:
    expressions: tuple[tuple[str, str], ...] = ()
    if hasattr(body, "expression_parameters"):
        expressions = tuple(sorted(body.expression_parameters().items()))  # type: ignore[attr-defined]
    charge = body.charge()
    return BodySnapshot(
        body_id=str(body.id),
        type_id=body.type_id,
        name=body.name,
        transform=_capture_transform(body.transform),
        parameters=tuple(sorted(body.parameters().items())),
        expressions=expressions,
        charge_mode=charge.mode.value,
        charge_density=charge.density,
        total_charge=charge.total_charge,
    )


def _restore_body(snap: BodySnapshot) -> GeometricBody:
    charge = HomogeneousCharge(
        mode=ChargeInputMode(snap.charge_mode),
        density=snap.charge_density,
        total_charge=snap.total_charge,
    )
    kwargs: dict[str, object] = {
        "name": snap.name,
        "body_id": BodyId(snap.body_id),
        "transform": _restore_transform(snap.transform),
        "charge": charge,
    }
    for key, value in snap.parameters:
        kwargs[key] = value
    for key, value in snap.expressions:
        if key == "x(t)":
            kwargs["expr_x"] = value
        elif key == "y(t)":
            kwargs["expr_y"] = value
        elif key == "z(t)":
            kwargs["expr_z"] = value
    return create_body(snap.type_id, **kwargs)


def capture_scene(scene: object) -> SceneSnapshot:
    selected = scene.selected_id()  # type: ignore[attr-defined]
    return SceneSnapshot(
        bodies=tuple(_capture_body(body) for body in scene.bodies()),  # type: ignore[attr-defined]
        selected_id=str(selected) if selected is not None else None,
    )


def restore_scene(scene: object, snapshot: SceneSnapshot) -> None:
    scene._bodies = [_restore_body(body) for body in snapshot.bodies]  # type: ignore[attr-defined]
    scene._selected_id = (  # type: ignore[attr-defined]
        BodyId(snapshot.selected_id) if snapshot.selected_id is not None else None
    )
