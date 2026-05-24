"""ImGui dark theme with comfortable spacing."""

from __future__ import annotations

from imgui_bundle import imgui


def apply_theme() -> None:
    imgui.style_colors_dark()
    style = imgui.get_style()
    style.window_rounding = 6.0
    style.frame_rounding = 4.0
    style.grab_rounding = 4.0
    style.scrollbar_rounding = 4.0
    style.window_padding = imgui.ImVec2(12.0, 12.0)
    style.frame_padding = imgui.ImVec2(8.0, 4.0)
    style.item_spacing = imgui.ImVec2(8.0, 6.0)
