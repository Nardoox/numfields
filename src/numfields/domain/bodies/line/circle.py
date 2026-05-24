from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("circle", dimension=Dimension.LINE, display_name="Circle")
class CircleBody(GeometricBody):
    radius: float = 1.0

    def __init__(self, name: str = "Circle", *, radius: float = 1.0, **kwargs: object) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.radius = radius

    @property
    def type_id(self) -> str:
        return "circle"

    @property
    def dimension(self) -> Dimension:
        return Dimension.LINE

    def parameters(self) -> dict[str, float]:
        return {"radius": self.radius}

    def set_parameter(self, key: str, value: float) -> None:
        if key == "radius":
            self.radius = max(0.01, value)

    def mesh_spec(self) -> MeshSpec:
        tube_radius = max(0.005, self.radius * 0.005)
        return MeshSpec(
            "circle_loop",
            {"radius": self.radius, "slices": 64, "tube_radius": tube_radius},
        )
