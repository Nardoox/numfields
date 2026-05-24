from __future__ import annotations

from numfields.domain.bodies.registry import register_body
from numfields.domain.bodies.volume.cylinder import CylinderBody
from numfields.domain.types import Dimension


@register_body("cylinder_shell", dimension=Dimension.SURFACE, display_name="Cylinder Shell")
class CylinderShellBody(CylinderBody):
    @property
    def type_id(self) -> str:
        return "cylinder_shell"

    @property
    def dimension(self) -> Dimension:
        return Dimension.SURFACE
