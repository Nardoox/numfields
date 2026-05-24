"""Inspector — transform and body parameters."""

from __future__ import annotations

import glm
from imgui_bundle import imgui

from numfields.domain.scene import Scene
from numfields.domain.types import Dimension


class InspectorPanel:
    def draw(self, scene: Scene) -> None:
        expanded, _ = imgui.begin("Inspector")
        if not expanded:
            imgui.end()
            return

        body = scene.selected()
        if body is None:
            imgui.text_disabled("No selection")
            imgui.end()
            return

        changed = False
        name_changed, new_name = imgui.input_text("Name", body.name)
        if name_changed:
            body.name = new_name
            changed = True

        dim_name = {Dimension.VOLUME: "Volume", Dimension.SURFACE: "Surface", Dimension.LINE: "Line"}
        imgui.text(f"Type: {body.type_id}  |  {dim_name[body.dimension]}")

        imgui.separator()
        imgui.text("Transform")
        pos = [body.transform.position.x, body.transform.position.y, body.transform.position.z]
        pos_changed, pos = imgui.drag_float3("Position", pos, 0.05)
        if pos_changed:
            body.transform.position = glm.vec3(*pos)
            changed = True

        euler = list(body.transform.euler_degrees())
        rot_changed, euler = imgui.drag_float3("Rotation (deg)", euler, 1.0)
        if rot_changed:
            body.transform.set_euler_degrees(euler[0], euler[1], euler[2])
            changed = True

        scale = body.transform.scale
        scale_changed, scale = imgui.drag_float("Scale", scale, 0.02, 0.01, 100.0)
        if scale_changed:
            body.transform.scale = max(0.01, scale)
            changed = True

        imgui.separator()
        imgui.text("Shape")
        for key, value in body.parameters().items():
            label = key.replace("_", " ").title()
            p_changed, v = imgui.drag_float(label, value, 0.02, 0.01, 100.0)
            if p_changed:
                body.set_parameter(key, max(0.01, v))
                changed = True

        imgui.separator()
        imgui.text_disabled("Charge (coming soon)")

        if changed:
            scene.mark_dirty()

        imgui.end()
