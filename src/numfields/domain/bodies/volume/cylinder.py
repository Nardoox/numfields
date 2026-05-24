from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("cylinder", dimension=Dimension.VOLUME, display_name="Cylinder")
class CylinderBody(GeometricBody):
    radius: float = 0.5
    height: float = 2.0

    def __init__(
        self,
        name: str = "Cylinder",
        *,
        radius: float = 0.5,
        height: float = 2.0,
        **kwargs: object,
    ) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.radius = radius
        self.height = height

    @property
    def type_id(self) -> str:
        return "cylinder"

    @property
    def dimension(self) -> Dimension:
        return Dimension.VOLUME

    def parameters(self) -> dict[str, float]:
        return {"radius": self.radius, "height": self.height}

    def set_parameter(self, key: str, value: float) -> None:
        if key == "radius":
            self.radius = max(0.01, value)
        elif key == "height":
            self.height = max(0.01, value)

    def mesh_spec(self) -> MeshSpec:
        return MeshSpec(
            "cylinder",
            {"radius": self.radius, "height": self.height, "segments": 48},
        )
