from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension


@register_body("box", dimension=Dimension.VOLUME, display_name="Box")
class BoxBody(GeometricBody):
    size_x: float = 1.0
    size_y: float = 1.0
    size_z: float = 1.0

    def __init__(
        self,
        name: str = "Box",
        *,
        size_x: float = 1.0,
        size_y: float = 1.0,
        size_z: float = 1.0,
        **kwargs: object,
    ) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z

    @property
    def type_id(self) -> str:
        return "box"

    @property
    def dimension(self) -> Dimension:
        return Dimension.VOLUME

    def parameters(self) -> dict[str, float]:
        return {"size_x": self.size_x, "size_y": self.size_y, "size_z": self.size_z}

    def set_parameter(self, key: str, value: float) -> None:
        v = max(0.01, value)
        if key == "size_x":
            self.size_x = v
        elif key == "size_y":
            self.size_y = v
        elif key == "size_z":
            self.size_z = v

    def mesh_spec(self) -> MeshSpec:
        return MeshSpec(
            "box",
            {"size_x": self.size_x, "size_y": self.size_y, "size_z": self.size_z},
        )
