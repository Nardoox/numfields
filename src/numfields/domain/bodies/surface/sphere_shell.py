from __future__ import annotations

from numfields.domain.bodies.registry import register_body
from numfields.domain.bodies.volume.sphere import SphereBody
from numfields.domain.types import Dimension


@register_body("sphere_shell", dimension=Dimension.SURFACE, display_name="Sphere Shell")
class SphereShellBody(SphereBody):
    @property
    def type_id(self) -> str:
        return "sphere_shell"

    @property
    def dimension(self) -> Dimension:
        return Dimension.SURFACE
