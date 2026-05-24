from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("disk", dimension=Dimension.SURFACE, display_name="Disk")
class DiskBody(GeometricBody):
    radius: float = 1.0

    def __init__(self, name: str = "Disk", *, radius: float = 1.0, **kwargs: object) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.radius = radius

    @property
    def type_id(self) -> str:
        return "disk"

    @property
    def dimension(self) -> Dimension:
        return Dimension.SURFACE

    def parameters(self) -> dict[str, float]:
        return {"radius": self.radius}

    def set_parameter(self, key: str, value: float) -> None:
        if key == "radius":
            self.radius = max(0.01, value)

    def mesh_spec(self) -> MeshSpec:
        return MeshSpec("disk", {"radius": self.radius, "slices": 64})
