"""Scene hierarchy — select and remove bodies."""

from __future__ import annotations

from imgui_bundle import imgui

from numfields.domain.scene import Scene
from numfields.domain.types import BodyId, Dimension


_DIM_LABEL = {
    Dimension.VOLUME: "Vol",
    Dimension.SURFACE: "Surf",
    Dimension.LINE: "Line",
}


class HierarchyPanel:
    def draw(self, scene: Scene) -> None:
        expanded, _ = imgui.begin("Hierarchy")
        if not expanded:
            imgui.end()
            return

        if imgui.button("Delete") and scene.selected_id() is not None:
            scene.remove(scene.selected_id())  # type: ignore[arg-type]

        imgui.separator()

        for body in scene.bodies():
            label = f"[{_DIM_LABEL[body.dimension]}] {body.name}"
            selected = scene.selected_id() == body.id
            flags = imgui.SelectableFlags_.none
            if imgui.selectable(label, selected, flags)[0]:
                scene.select(body.id)

        if imgui.begin_popup_context_window():
            if imgui.menu_item("Delete", "", False, scene.selected_id() is not None)[0]:
                if scene.selected_id():
                    scene.remove(scene.selected_id())  # type: ignore[arg-type]
            imgui.end_popup()

        imgui.end()
