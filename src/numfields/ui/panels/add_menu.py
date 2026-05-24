"""Add body menu — volume / surface / line primitives."""

from __future__ import annotations

from imgui_bundle import imgui

from numfields.domain.bodies.registry import body_types_by_dimension, create_body
from numfields.domain.scene import Scene
from numfields.domain.types import Dimension


_DIM_TITLE = {
    Dimension.VOLUME: "Volume",
    Dimension.SURFACE: "Surface",
    Dimension.LINE: "Line",
}


class AddMenuPanel:
    def draw(self, scene: Scene) -> None:
        expanded, _ = imgui.begin("Add Body")
        if not expanded:
            imgui.end()
            return

        by_dim = body_types_by_dimension()
        flags = imgui.TreeNodeFlags_.default_open

        for dim in (Dimension.VOLUME, Dimension.SURFACE, Dimension.LINE):
            if imgui.collapsing_header(_DIM_TITLE[dim], flags):
                for type_id, display_name in by_dim[dim]:
                    if imgui.button(display_name, imgui.ImVec2(-1, 0)):
                        body = create_body(type_id)
                        scene.add(body, select=True)

        imgui.end()
