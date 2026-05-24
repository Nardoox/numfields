from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("sphere", dimension=Dimension.VOLUME, display_name="Sphere")
class SphereBody(GeometricBody):
    radius: float = 1.0

    def __init__(self, name: str = "Sphere", *, radius: float = 1.0, **kwargs: object) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.radius = radius

    @property
    def type_id(self) -> str:
        return "sphere"

    @property
    def dimension(self) -> Dimension:
        return Dimension.VOLUME

    def parameters(self) -> dict[str, float]:
        return {"radius": self.radius}

    def set_parameter(self, key: str, value: float) -> None:
        if key == "radius":
            self.radius = max(0.01, value)

    def mesh_spec(self) -> MeshSpec:
        return MeshSpec(
            "uv_sphere",
            {"radius": self.radius, "stacks": 32, "slices": 48},
        )
