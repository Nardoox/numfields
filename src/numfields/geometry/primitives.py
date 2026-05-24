"""Procedural mesh builders — body-local space."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from numfields.domain.bodies.base import MeshSpec
from numfields.geometry.mesh_data import MeshData


def build_mesh(spec: MeshSpec) -> MeshData:
    builders = {
        "uv_sphere": uv_sphere,
        "cylinder": cylinder,
        "box": box,
        "disk": disk,
        "rectangle": rectangle,
        "segment": segment,
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
