from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("segment", dimension=Dimension.LINE, display_name="Segment")
class SegmentBody(GeometricBody):
    length: float = 2.0

    def __init__(self, name: str = "Segment", *, length: float = 2.0, **kwargs: object) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.length = length

    @property
    def type_id(self) -> str:
        return "segment"

    @property
    def dimension(self) -> Dimension:
        return Dimension.LINE

    def parameters(self) -> dict[str, float]:
        return {"length": self.length}

    def set_parameter(self, key: str, value: float) -> None:
        if key == "length":
            self.length = max(0.01, value)

    def mesh_spec(self) -> MeshSpec:
        line_radius = max(0.005, self.length * 0.005)
        return MeshSpec(
            "segment",
            {"length": self.length, "radius": line_radius, "segments": 16},
        )
