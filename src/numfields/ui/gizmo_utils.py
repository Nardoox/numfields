"""ImGuizmo helpers — matrix conversion matching imgui_bundle demo_gizmo.py."""

from __future__ import annotations

import glm
from imgui_bundle import imguizmo

GizmoMatrix16 = imguizmo.im_guizmo.Matrix16


def glm_to_matrix16(matrix: glm.mat4) -> GizmoMatrix16:
    values = (
        matrix[0].to_list()
        + matrix[1].to_list()
        + matrix[2].to_list()
        + matrix[3].to_list()
    )
    return GizmoMatrix16(values)


def sync_transform_from_gizmo(
    transform: object,
    model: GizmoMatrix16,
) -> None:
    comps = imguizmo.im_guizmo.decompose_matrix_to_components(model)
    transform.position = glm.vec3(*comps.translation.values)  # type: ignore[attr-defined]
    transform.set_euler_degrees(*comps.rotation.values)  # type: ignore[attr-defined]
    transform.scale = comps.scale.values[0]  # type: ignore[attr-defined]
