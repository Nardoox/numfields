from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("rect_outline", dimension=Dimension.LINE, display_name="Rect Outline")
class RectOutlineBody(GeometricBody):
    width: float = 2.0
    height: float = 1.0

    def __init__(
        self,
        name: str = "Rect Outline",
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
        return "rect_outline"

    @property
    def dimension(self) -> Dimension:
        return Dimension.LINE

    def parameters(self) -> dict[str, float]:
        return {"width": self.width, "height": self.height}

    def set_parameter(self, key: str, value: float) -> None:
        v = max(0.01, value)
        if key == "width":
            self.width = v
        elif key == "height":
            self.height = v

    def mesh_spec(self) -> MeshSpec:
        min_edge = min(self.width, self.height)
        tube_radius = max(0.005, min_edge * 0.005)
        return MeshSpec(
            "rect_outline",
            {"width": self.width, "height": self.height, "tube_radius": tube_radius},
        )
