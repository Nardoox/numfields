"""GPU mesh cache keyed by body mesh_cache_key."""

from __future__ import annotations

from dataclasses import dataclass

import moderngl

from numfields.domain.bodies.base import GeometricBody
from numfields.domain.scene import Scene
from numfields.domain.types import BodyId
from numfields.geometry.mesh_data import MeshData
from numfields.geometry.primitives import build_mesh


@dataclass
class GpuMesh:
    vao: moderngl.VertexArray
    index_count: int
    mode: int


class MeshCache:
    def __init__(self, ctx: moderngl.Context, program: moderngl.Program) -> None:
        self._ctx = ctx
        self._program = program
        self._cache: dict[BodyId, tuple[tuple, GpuMesh]] = {}
        self._scene_version = -1

    def sync(self, scene: Scene) -> None:
        if scene.version == self._scene_version:
            return
        self._scene_version = scene.version
        alive = {b.id for b in scene.bodies()}
        for bid in list(self._cache):
            if bid not in alive:
                _, gpu = self._cache.pop(bid)
                gpu.vao.release()

        for body in scene.bodies():
            key = body.mesh_cache_key()
            if body.id in self._cache and self._cache[body.id][0] == key:
                continue
            if body.id in self._cache:
                self._cache[body.id][1].vao.release()
            mesh_data = build_mesh(body.mesh_spec())
            gpu = self._upload(mesh_data)
            self._cache[body.id] = (key, gpu)

    def get(self, body_id: BodyId) -> GpuMesh | None:
        entry = self._cache.get(body_id)
        return entry[1] if entry else None

    def _upload(self, data: MeshData) -> GpuMesh:
        vertices = data.interleaved_vertices()
        vbo = self._ctx.buffer(vertices.tobytes())
        ibo = self._ctx.buffer(data.indices.tobytes())
        vao = self._ctx.vertex_array(
            self._program,
            [(vbo, "3f 3f", "in_position", "in_normal")],
            ibo,
        )
        return GpuMesh(vao=vao, index_count=len(data.indices), mode=moderngl.TRIANGLES)

    def release(self) -> None:
        for _, gpu in self._cache.values():
            gpu.vao.release()
        self._cache.clear()


class LineMeshCache:
    """Separate cache for grid/axes line programs."""

    def __init__(self, ctx: moderngl.Context, program: moderngl.Program) -> None:
        self._ctx = ctx
        self._program = program
        self._meshes: dict[str, GpuMesh] = {}

    def get_or_create(self, key: str, data: MeshData, *, mode: int | None = None) -> GpuMesh:
        if key not in self._meshes:
            vertices = data.interleaved_vertices()
            vbo = self._ctx.buffer(vertices.tobytes())
            draw_mode = mode if mode is not None else moderngl.LINES
            if draw_mode == moderngl.LINES:
                vao = self._ctx.vertex_array(
                    self._program,
                    [(vbo, "3f 12x", "in_position")],
                )
                count = data.vertex_count
            else:
                ibo = self._ctx.buffer(data.indices.tobytes())
                vao = self._ctx.vertex_array(
                    self._program,
                    [(vbo, "3f 12x", "in_position")],
                    ibo,
                )
                count = len(data.indices)
            self._meshes[key] = GpuMesh(vao=vao, index_count=count, mode=draw_mode)
        return self._meshes[key]

    def release(self) -> None:
        for gpu in self._meshes.values():
            gpu.vao.release()
        self._meshes.clear()
