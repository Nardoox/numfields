"""Procedural mesh builders — body-local space."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from numfields.domain.bodies.base import MeshSpec
from numfields.geometry.expression_eval import evaluate_expression
from numfields.geometry.mesh_data import MeshData


def build_mesh(spec: MeshSpec) -> MeshData:
    builders = {
        "uv_sphere": uv_sphere,
        "cylinder": cylinder,
        "box": box,
        "disk": disk,
        "rectangle": rectangle,
        "segment": segment,
        "circle_loop": circle_loop,
        "rect_outline": rect_outline,
        "parametric_curve": parametric_curve,
        "coil": coil,
    }
    fn = builders.get(spec.builder)
    if fn is None:
        raise ValueError(f"Unknown mesh builder: {spec.builder}")
    return fn(**spec.args)


def uv_sphere(
    radius: float = 1.0,
    stacks: int = 32,
    slices: int = 48,
    **_: Any,
) -> MeshData:
    positions: list[list[float]] = []
    normals: list[list[float]] = []
    indices: list[int] = []

    for i in range(stacks + 1):
        v = i / stacks
        phi = v * math.pi
        for j in range(slices + 1):
            u = j / slices
            theta = u * 2.0 * math.pi
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            n = [x, y, z]
            normals.append(n)
            positions.append([x * radius, y * radius, z * radius])

    for i in range(stacks):
        for j in range(slices):
            a = i * (slices + 1) + j
            b = a + slices + 1
            indices.extend([a, b, a + 1, a + 1, b, b + 1])

    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def cylinder(
    radius: float = 0.5,
    height: float = 2.0,
    segments: int = 48,
    **_: Any,
) -> MeshData:
    half_h = height * 0.5
    positions: list[list[float]] = []
    normals: list[list[float]] = []
    indices: list[int] = []

    for i in range(segments):
        a0 = 2.0 * math.pi * i / segments
        a1 = 2.0 * math.pi * (i + 1) / segments
        x0, z0 = math.cos(a0) * radius, math.sin(a0) * radius
        x1, z1 = math.cos(a1) * radius, math.sin(a1) * radius
        n0 = [math.cos(a0), 0.0, math.sin(a0)]
        n1 = [math.cos(a1), 0.0, math.sin(a1)]
        v = len(positions)
        positions.extend(
            [
                [x0, -half_h, z0],
                [x1, -half_h, z1],
                [x1, half_h, z1],
                [x0, half_h, z0],
            ]
        )
        normals.extend([n0, n1, n1, n0])
        indices.extend([v, v + 1, v + 2, v, v + 2, v + 3])

    def cap(y: float, ny: float) -> None:
        center_i = len(positions)
        positions.append([0.0, y, 0.0])
        normals.append([0.0, ny, 0.0])
        ring_start = len(positions)
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            positions.append([math.cos(a) * radius, y, math.sin(a) * radius])
            normals.append([0.0, ny, 0.0])
        for i in range(segments):
            i1 = ring_start + ((i + 1) % segments)
            i0 = ring_start + i
            if ny > 0:
                indices.extend([center_i, i0, i1])
            else:
                indices.extend([center_i, i1, i0])

    cap(half_h, 1.0)
    cap(-half_h, -1.0)

    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def box(
    size_x: float = 1.0,
    size_y: float = 1.0,
    size_z: float = 1.0,
    **_: Any,
) -> MeshData:
    hx, hy, hz = size_x * 0.5, size_y * 0.5, size_z * 0.5
    faces = [
        ([0, 0, 1], [hx, hy, hz], [hx, -hy, hz], [-hx, -hy, hz], [-hx, hy, hz]),
        ([0, 0, -1], [hx, hy, -hz], [-hx, hy, -hz], [-hx, -hy, -hz], [hx, -hy, -hz]),
        ([0, 1, 0], [-hx, hy, hz], [hx, hy, hz], [hx, hy, -hz], [-hx, hy, -hz]),
        ([0, -1, 0], [-hx, -hy, hz], [-hx, -hy, -hz], [hx, -hy, -hz], [hx, -hy, hz]),
        ([1, 0, 0], [hx, hy, hz], [hx, hy, -hz], [hx, -hy, -hz], [hx, -hy, hz]),
        ([-1, 0, 0], [-hx, hy, hz], [-hx, -hy, hz], [-hx, -hy, -hz], [-hx, hy, -hz]),
    ]
    positions: list[list[float]] = []
    normals: list[list[float]] = []
    indices: list[int] = []
    for n, *verts in faces:
        base = len(positions)
        for v in verts:
            positions.append(v)
            normals.append(list(n))
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])
    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def disk(radius: float = 1.0, slices: int = 64, **_: Any) -> MeshData:
    positions = [[0.0, 0.0, 0.0]]
    normals = [[0.0, 0.0, 1.0]]
    indices: list[int] = []
    for i in range(slices):
        a = 2.0 * math.pi * i / slices
        positions.append([math.cos(a) * radius, math.sin(a) * radius, 0.0])
        normals.append([0.0, 0.0, 1.0])
    for i in range(1, slices + 1):
        i1 = 1 if i == slices else i + 1
        indices.extend([0, i, i1])
    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def rectangle(width: float = 2.0, height: float = 1.0, **_: Any) -> MeshData:
    hw, hh = width * 0.5, height * 0.5
    positions = [
        [-hw, -hh, 0.0],
        [hw, -hh, 0.0],
        [hw, hh, 0.0],
        [-hw, hh, 0.0],
    ]
    normals = [[0.0, 0.0, 1.0]] * 4
    indices = [0, 1, 2, 0, 2, 3]
    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def segment(
    length: float = 2.0,
    radius: float = 0.01,
    segments: int = 16,
    **_: Any,
) -> MeshData:
    data = cylinder(radius=radius, height=length, segments=segments)
    pos = data.positions.copy()
    nrm = data.normals.copy()
    new_pos = np.empty_like(pos)
    new_nrm = np.empty_like(nrm)
    new_pos[:, 0] = pos[:, 1]
    new_pos[:, 1] = -pos[:, 0]
    new_pos[:, 2] = pos[:, 2]
    new_nrm[:, 0] = nrm[:, 1]
    new_nrm[:, 1] = -nrm[:, 0]
    new_nrm[:, 2] = nrm[:, 2]
    return MeshData(positions=new_pos, normals=new_nrm, indices=data.indices)


def _merge_meshes(parts: list[MeshData]) -> MeshData:
    positions: list[np.ndarray] = []
    normals: list[np.ndarray] = []
    indices: list[np.ndarray] = []
    offset = 0
    for part in parts:
        positions.append(part.positions)
        normals.append(part.normals)
        indices.append(part.indices + offset)
        offset += len(part.positions)
    return MeshData(
        positions=np.vstack(positions),
        normals=np.vstack(normals),
        indices=np.concatenate(indices),
    )


def _rotation_y_to_direction(direction: np.ndarray) -> np.ndarray:
    y = np.array([0.0, 1.0, 0.0], dtype="f8")
    d = direction / np.linalg.norm(direction)
    if np.allclose(d, y):
        return np.eye(3)
    if np.allclose(d, -y):
        return np.diag([1.0, -1.0, -1.0])
    v = np.cross(y, d)
    s = np.linalg.norm(v)
    c = float(np.dot(y, d))
    vx = np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
    return np.eye(3) + vx + vx @ vx * ((1.0 - c) / (s * s))


def _tube_segment(
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    radius: float,
    segments: int = 12,
) -> MeshData:
    delta = np.array(p1, dtype="f8") - np.array(p0, dtype="f8")
    length = float(np.linalg.norm(delta))
    if length < 1e-8:
        return MeshData(
            positions=np.zeros((0, 3), dtype="f4"),
            normals=np.zeros((0, 3), dtype="f4"),
            indices=np.zeros(0, dtype="u4"),
        )

    data = cylinder(radius=radius, height=length, segments=segments)
    rot = _rotation_y_to_direction(delta)
    pos = data.positions @ rot.T
    nrm = data.normals @ rot.T
    mid = (np.array(p0, dtype="f8") + np.array(p1, dtype="f8")) * 0.5
    pos += mid
    return MeshData(positions=pos.astype("f4"), normals=nrm.astype("f4"), indices=data.indices)


def circle_loop(
    radius: float = 1.0,
    slices: int = 64,
    tube_radius: float = 0.005,
    **_: Any,
) -> MeshData:
    positions: list[list[float]] = []
    normals: list[list[float]] = []
    indices: list[int] = []
    major = max(radius, 0.01)
    minor = max(tube_radius, 0.001)
    tube_slices = max(8, slices // 4)

    for i in range(slices + 1):
        u = 2.0 * math.pi * i / slices
        for j in range(tube_slices + 1):
            v = 2.0 * math.pi * j / tube_slices
            x = (major + minor * math.cos(v)) * math.cos(u)
            y = (major + minor * math.cos(v)) * math.sin(u)
            z = minor * math.sin(v)
            nx = math.cos(v) * math.cos(u)
            ny = math.cos(v) * math.sin(u)
            nz = math.sin(v)
            positions.append([x, y, z])
            normals.append([nx, ny, nz])

    row = tube_slices + 1
    for i in range(slices):
        for j in range(tube_slices):
            a = i * row + j
            b = a + row
            indices.extend([a, b, a + 1, a + 1, b, b + 1])

    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=np.array(normals, dtype="f4"),
        indices=np.array(indices, dtype="u4"),
    )


def rect_outline(
    width: float = 2.0,
    height: float = 1.0,
    tube_radius: float = 0.005,
    **_: Any,
) -> MeshData:
    hw, hh = width * 0.5, height * 0.5
    corners = [
        (-hw, -hh, 0.0),
        (hw, -hh, 0.0),
        (hw, hh, 0.0),
        (-hw, hh, 0.0),
    ]
    parts = [
        _tube_segment(corners[i], corners[(i + 1) % 4], tube_radius)
        for i in range(4)
    ]
    return _merge_meshes(parts)


def coil(
    length: float = 2.0,
    radius: float = 0.5,
    windings: float = 3.0,
    segments: int = 96,
    **_: Any,
) -> MeshData:
    turns = max(1.0, windings)
    t_max = 2.0 * math.pi * turns
    count = max(48, segments)
    ts = np.linspace(0.0, t_max, count + 1)
    points = [
        (radius * math.cos(t), radius * math.sin(t), length * t / t_max)
        for t in ts
    ]
    span = max(
        (math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)),
        default=0.01,
    )
    tube_radius = max(0.005, span * 0.15)
    parts = [
        _tube_segment(points[i], points[i + 1], tube_radius)
        for i in range(len(points) - 1)
    ]
    return _merge_meshes(parts)


def parametric_curve(
    expr_x: str,
    expr_y: str,
    expr_z: str,
    t_min: float,
    t_max: float,
    segments: int,
    variables: dict[str, float] | None = None,
    **_: Any,
) -> MeshData:
    vars_map = dict(variables or {})
    count = max(3, segments)
    ts = np.linspace(t_min, t_max, count + 1)
    points: list[tuple[float, float, float]] = []
    try:
        for t in ts:
            ctx = {"t": float(t), **vars_map}
            points.append(
                (
                    evaluate_expression(expr_x, ctx),
                    evaluate_expression(expr_y, ctx),
                    evaluate_expression(expr_z, ctx),
                )
            )
    except Exception:
        return segment(length=1.0, radius=0.01, segments=8)

    if len(points) < 2:
        return segment(length=1.0, radius=0.01, segments=8)

    span = max(
        (
            math.dist(points[i], points[i + 1])
            for i in range(len(points) - 1)
        ),
        default=0.01,
    )
    tube_radius = max(0.005, span * 0.15)
    parts = [
        _tube_segment(points[i], points[i + 1], tube_radius)
        for i in range(len(points) - 1)
    ]
    return _merge_meshes(parts)


def grid_lines(size: float = 10.0, divisions: int = 20) -> MeshData:
    positions: list[list[float]] = []
    step = size / divisions
    half = size * 0.5
    for i in range(divisions + 1):
        z = -half + i * step
        positions.extend([[-half, 0.0, z], [half, 0.0, z]])
        x = -half + i * step
        positions.extend([[x, 0.0, -half], [x, 0.0, half]])
    n = len(positions)
    normals = np.tile([0.0, 1.0, 0.0], (n, 1)).astype("f4")
    indices = np.arange(n, dtype="u4")
    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=normals,
        indices=indices,
    )


def axis_lines(length: float = 2.0) -> MeshData:
    positions = [
        [0.0, 0.0, 0.0],
        [length, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, length, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, length],
    ]
    normals = np.ones((6, 3), dtype="f4")
    indices = np.arange(6, dtype="u4")
    return MeshData(
        positions=np.array(positions, dtype="f4"),
        normals=normals,
        indices=indices,
    )
