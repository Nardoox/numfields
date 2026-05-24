from __future__ import annotations

from numfields.domain.bodies.registry import register_body
from numfields.domain.bodies.volume.box import BoxBody
from numfields.domain.types import Dimension


@register_body("box_shell", dimension=Dimension.SURFACE, display_name="Box Shell")
class BoxShellBody(BoxBody):
    @property
    def type_id(self) -> str:
        return "box_shell"

    @property
    def dimension(self) -> Dimension:
        return Dimension.SURFACE
