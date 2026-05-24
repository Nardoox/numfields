from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("rectangle", dimension=Dimension.SURFACE, display_name="Rectangle")
class RectangleBody(GeometricBody):
    width: float = 2.0
    height: float = 1.0

    def __init__(
        self,
        name: str = "Rectangle",
        *,
        width: float = 2.0,
        height: float = 1.0,
        **kwargs: object,
    ) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.width = width
        self.height = height

    @property
    def type_id(self) -> str:
        return "rectangle"

    @property
    def dimension(self) -> Dimension:
        return Dimension.SURFACE

    def parameters(self) -> dict[str, float]:
        return {"width": self.width, "height": self.height}

    def set_parameter(self, key: str, value: float) -> None:
        v = max(0.01, value)
        if key == "width":
            self.width = v
        elif key == "height":
            self.height = v

    def mesh_spec(self) -> MeshSpec:
        return MeshSpec("rectangle", {"width": self.width, "height": self.height})
