"""Scene renderer — dimension passes, grid, axes."""

from __future__ import annotations

import glm
import moderngl

from numfields.domain.scene import Scene
from numfields.domain.types import Dimension
from numfields.geometry.primitives import axis_lines, grid_lines
from numfields.rendering.camera import OrbitCamera
from numfields.rendering.mesh_cache import LineMeshCache, MeshCache


DIMENSION_TINT = {
    Dimension.VOLUME: glm.vec3(0.35, 0.55, 0.95),
    Dimension.SURFACE: glm.vec3(0.35, 0.85, 0.55),
    Dimension.LINE: glm.vec3(0.95, 0.55, 0.25),
}

DIMENSION_ALPHA = {
    Dimension.VOLUME: 0.35,
    Dimension.SURFACE: 0.55,
    Dimension.LINE: 1.0,
}

AXIS_COLORS = [
    glm.vec3(0.9, 0.25, 0.25),
    glm.vec3(0.25, 0.9, 0.35),
    glm.vec3(0.3, 0.45, 0.95),
]


class SceneRenderer:
    def __init__(
        self,
        ctx: moderngl.Context,
        solid_program: moderngl.Program,
        line_program: moderngl.Program,
    ) -> None:
        self._ctx = ctx
        self._solid = solid_program
        self._line = line_program
        self._mesh_cache = MeshCache(ctx, solid_program)
        self._line_cache = LineMeshCache(ctx, line_program)
        self._light_dir = glm.vec3(0.4, 0.8, 0.3)
        self.show_grid = True
        self.show_axes = True

    @property
    def mesh_cache(self) -> MeshCache:
        return self._mesh_cache

    def render(
        self,
        scene: Scene,
        camera: OrbitCamera,
        selected_id: str | None,
        *,
        translating: bool = False,
    ) -> None:
        self._mesh_cache.sync(scene)
        view = camera.view_matrix()
        proj = camera.projection_matrix()
        self._solid["u_view"].write(bytes(glm.transpose(view)))
        self._solid["u_proj"].write(bytes(glm.transpose(proj)))
        self._solid["u_light_dir"].write(bytes(self._light_dir))

        self._ctx.enable(moderngl.DEPTH_TEST)
        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        for dim in (Dimension.VOLUME, Dimension.SURFACE, Dimension.LINE):
            self._draw_pass(
                scene,
                dim,
                selected_id,
                double_sided=(dim == Dimension.SURFACE),
                translating=translating,
            )

        self._draw_helpers(camera, selected_id)

    def _draw_pass(
        self,
        scene: Scene,
        dimension: Dimension,
        selected_id: str | None,
        *,
        double_sided: bool,
        translating: bool,
    ) -> None:
        if double_sided:
            self._ctx.disable(moderngl.CULL_FACE)
        else:
            self._ctx.enable(moderngl.CULL_FACE)

        tint = DIMENSION_TINT[dimension]
        alpha = DIMENSION_ALPHA[dimension]

        for i, body in enumerate(scene.bodies()):
            if body.dimension != dimension:
                continue
            gpu = self._mesh_cache.get(body.id)
            if gpu is None:
                continue
            selected = 1 if selected_id is not None and body.id == selected_id else 0
            dragging = 1 if selected and translating else 0
            body_alpha = min(1.0, alpha + 0.15) if dragging else alpha
            model = body.transform.matrix()
            self._solid["u_model"].write(bytes(glm.transpose(model)))
            self._solid["u_tint"].write(bytes(tint))
            self._solid["u_alpha"].value = body_alpha
            self._solid["u_selected"].value = selected
            if "u_translating" in self._solid:
                self._solid["u_translating"].value = dragging
            if "u_body_id" in self._solid:
                self._solid["u_body_id"].value = i + 1
            gpu.vao.render(mode=gpu.mode)

    def _draw_helpers(self, camera: OrbitCamera, selected_id: str | None) -> None:
        if not self.show_grid and not self.show_axes:
            return
            
        del selected_id
        view = camera.view_matrix()
        proj = camera.projection_matrix()
        self._line["u_view"].write(bytes(glm.transpose(view)))
        self._line["u_proj"].write(bytes(glm.transpose(proj)))
        self._line["u_selected"].value = 0
        identity = bytes(glm.mat4(1.0))

        if self.show_grid:
            grid = self._line_cache.get_or_create("grid", grid_lines())
            self._line["u_model"].write(identity)
            self._line["u_tint"].write(bytes(glm.vec3(0.35, 0.38, 0.42)))
            grid.vao.render(mode=moderngl.LINES, vertices=grid.index_count)

        if self.show_axes:
            import numpy as np
            from numfields.geometry.primitives import cylinder
            import math
            
            # Using cylinders instead of lines for thicker axes
            # We want them to start at 0,0,0 and go along X, Y, Z for length 2.0
            radius = 0.02
            length = 2.0
            
            # Create the mesh only once (cylinder goes along Y from -1 to 1)
            # We will transform it to go from 0 to 2
            cyl = cylinder(radius=radius, height=length, segments=16)
            axis_mesh = self._mesh_cache._upload(cyl) if not hasattr(self, '_thick_axis') else self._thick_axis
            self._thick_axis = axis_mesh
            
            # We render with the solid shader
            self._solid["u_view"].write(bytes(glm.transpose(view)))
            self._solid["u_proj"].write(bytes(glm.transpose(proj)))
            
            # Transform to [0, 2] on Y axis
            base_tr = glm.translate(glm.mat4(1.0), glm.vec3(0, length / 2.0, 0))
            
            # X Axis (Red)
            # Rotate Y to X
            rot_x = glm.rotate(glm.mat4(1.0), math.radians(-90.0), glm.vec3(0, 0, 1))
            model_x = rot_x * base_tr
            self._solid["u_model"].write(bytes(glm.transpose(model_x)))
            self._solid["u_tint"].write(bytes(AXIS_COLORS[0]))
            self._solid["u_alpha"].value = 1.0
            self._solid["u_selected"].value = 0
            if "u_translating" in self._solid:
                self._solid["u_translating"].value = 0
            if "u_body_id" in self._solid:
                self._solid["u_body_id"].value = 0
            axis_mesh.vao.render(mode=axis_mesh.mode)
            
            # Y Axis (Green)
            model_y = base_tr
            self._solid["u_model"].write(bytes(glm.transpose(model_y)))
            self._solid["u_tint"].write(bytes(AXIS_COLORS[1]))
            axis_mesh.vao.render(mode=axis_mesh.mode)
            
            # Z Axis (Blue)
            # Rotate Y to Z
            rot_z = glm.rotate(glm.mat4(1.0), math.radians(90.0), glm.vec3(1, 0, 0))
            model_z = rot_z * base_tr
            self._solid["u_model"].write(bytes(glm.transpose(model_z)))
            self._solid["u_tint"].write(bytes(AXIS_COLORS[2]))
            axis_mesh.vao.render(mode=axis_mesh.mode)

    def release(self) -> None:
        self._mesh_cache.release()
        self._line_cache.release()
