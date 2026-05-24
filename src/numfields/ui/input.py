"""Viewport input state for camera control."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewportInput:
    focused: bool = False
    hovered: bool = False
    mouse_x: float = 0.0
    mouse_y: float = 0.0

    def allow_camera(self) -> bool:
        return self.focused and self.hovered
