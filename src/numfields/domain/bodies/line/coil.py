from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("coil", dimension=Dimension.LINE, display_name="Coil")
class CoilBody(GeometricBody):
    length: float = 2.0
    radius: float = 0.5
    windings: float = 3.0

    def __init__(
        self,
        name: str = "Coil",
        *,
        length: float = 2.0,
        radius: float = 0.5,
        windings: float = 3.0,
        **kwargs: object,
    ) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.length = length
        self.radius = radius
        self.windings = windings

    @property
    def type_id(self) -> str:
        return "coil"

    @property
    def dimension(self) -> Dimension:
        return Dimension.LINE

    def parameters(self) -> dict[str, float]:
        return {
            "length": self.length,
            "radius": self.radius,
            "windings": self.windings,
        }

    def set_parameter(self, key: str, value: float) -> None:
        if key == "length":
            self.length = max(0.01, value)
        elif key == "radius":
            self.radius = max(0.01, value)
        elif key == "windings":
            self.windings = max(1.0, value)

    def mesh_spec(self) -> MeshSpec:
        segments = max(48, int(self.windings * 48))
        return MeshSpec(
            "coil",
            {
                "length": self.length,
                "radius": self.radius,
                "windings": self.windings,
                "segments": segments,
            },
        )
