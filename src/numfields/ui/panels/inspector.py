"""Inspector — transform and body parameters."""

from __future__ import annotations

import glm
from imgui_bundle import imgui

from numfields.domain.carve import can_carve
from numfields.domain.charge import ChargeInputMode
from numfields.domain.scene import Scene
from numfields.domain.types import Dimension


class InspectorPanel:
    def __init__(self) -> None:
        self._editing = False

    def draw(self, scene: Scene) -> None:
        expanded, _ = imgui.begin("Inspector")
        if not expanded:
            if self._editing:
                scene.history.end_group(scene)
                self._editing = False
            imgui.end()
            return

        body = scene.selected()
        if body is None:
            if self._editing:
                scene.history.end_group(scene)
                self._editing = False
            imgui.text_disabled("No selection")
            imgui.end()
            return

        changed = False
        geometry_changed = False
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
            geometry_changed = True

        imgui.separator()
        imgui.text("Shape")

        if hasattr(body, "expression_parameters"):
            imgui.text_disabled("Variables: t, R, pitch, pi, e, sin, cos, ...")
            for key, value in body.expression_parameters().items():  # type: ignore[attr-defined]
                changed_expr, new_value = imgui.input_text(key, value)
                if changed_expr:
                    body.set_expression_parameter(key, new_value)  # type: ignore[attr-defined]
                    changed = True
                    geometry_changed = True
            imgui.separator()

        for key, value in body.parameters().items():
            label = key.replace("_", " ").title()
            step = 1.0 if key == "segments" else 0.02
            vmin = 3.0 if key == "segments" else -1000.0
            vmax = 512.0 if key == "segments" else 1000.0
            p_changed, v = imgui.drag_float(label, value, step, vmin, vmax)
            if p_changed:
                body.set_parameter(key, v)
                changed = True
                geometry_changed = True

        if hasattr(body, "validate_expressions"):
            err = body.validate_expressions()  # type: ignore[attr-defined]
            if err:
                imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(1.0, 0.35, 0.35, 1.0))
                imgui.text_wrapped(err)
                imgui.pop_style_color()
            elif getattr(body, "last_error", None):
                imgui.text_disabled("Curve OK")

        if geometry_changed:
            body.sync_charge_after_geometry_change()

        imgui.separator()
        imgui.text("Charge")
        charge = body.charge()
        density_labels = {
            Dimension.LINE: "Line Density (\u03bb, C/m)",
            Dimension.SURFACE: "Surface Density (\u03c3, C/m^2)",
            Dimension.VOLUME: "Volume Density (\u03c1, C/m^3)",
        }
        density_label = density_labels[body.dimension]
        mode_is_density = charge.mode == ChargeInputMode.DENSITY

        if imgui.radio_button("Density", mode_is_density):
            body.set_charge_mode(ChargeInputMode.DENSITY)
            changed = True
        imgui.same_line()
        if imgui.radio_button("Total Charge Q", not mode_is_density):
            body.set_charge_mode(ChargeInputMode.TOTAL)
            changed = True

        if mode_is_density:
            d_changed, density = imgui.drag_float(density_label, charge.density, 0.01)
            if d_changed:
                body.set_charge_density(density)
                changed = True
            imgui.text(f"Total Charge Q: {charge.total_charge_value(body):.6g} C")
        else:
            q_changed, total = imgui.drag_float("Total Charge Q (C)", charge.total_charge, 0.01)
            if q_changed:
                body.set_total_charge(total)
                changed = True
            imgui.text(f"{density_label}: {charge.density:.6g}")

        editing = imgui.is_window_focused() and imgui.is_any_item_active()
        if editing and not self._editing:
            scene.history.start_group(scene)
        elif self._editing and not editing:
            scene.history.end_group(scene)
        self._editing = editing

        if body.dimension > Dimension.LINE and can_carve(body):
            imgui.separator()
            if imgui.button("Carve"):
                scene.carve(body.id)

        imgui.separator()
        if imgui.button("Delete"):
            scene.remove(body.id)

        if changed:
            scene.mark_dirty()

        imgui.end()
