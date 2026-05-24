from __future__ import annotations

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.registry import register_body
from numfields.domain.types import Dimension
from numfields.geometry.expression_eval import ExpressionError, evaluate_expression

DEFAULT_HELIX = {
    "expr_x": "R * cos(t)",
    "expr_y": "R * sin(t)",
    "expr_z": "pitch * t / (2 * pi)",
    "t_min": 0.0,
    "t_max": 12.566185307179586,  # 4 * pi
    "segments": 96.0,
    "R": 1.0,
    "pitch": 1.0,
}


@register_body("parametric_curve", dimension=Dimension.LINE, display_name="Parametric Curve")
class ParametricCurveBody(GeometricBody):
    expr_x: str
    expr_y: str
    expr_z: str
    t_min: float
    t_max: float
    segments: float
    R: float
    pitch: float
    last_error: str | None

    def __init__(
        self,
        name: str = "Parametric Curve",
        *,
        expr_x: str = DEFAULT_HELIX["expr_x"],
        expr_y: str = DEFAULT_HELIX["expr_y"],
        expr_z: str = DEFAULT_HELIX["expr_z"],
        t_min: float = DEFAULT_HELIX["t_min"],
        t_max: float = DEFAULT_HELIX["t_max"],
        segments: float = DEFAULT_HELIX["segments"],
        R: float = DEFAULT_HELIX["R"],
        pitch: float = DEFAULT_HELIX["pitch"],
        **kwargs: object,
    ) -> None:
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self.expr_x = expr_x
        self.expr_y = expr_y
        self.expr_z = expr_z
        self.t_min = t_min
        self.t_max = t_max
        self.segments = segments
        self.R = R
        self.pitch = pitch
        self.last_error: str | None = None

    @property
    def type_id(self) -> str:
        return "parametric_curve"

    @property
    def dimension(self) -> Dimension:
        return Dimension.LINE

    def expression_parameters(self) -> dict[str, str]:
        return {"x(t)": self.expr_x, "y(t)": self.expr_y, "z(t)": self.expr_z}

    def set_expression_parameter(self, key: str, value: str) -> None:
        if key == "x(t)":
            self.expr_x = value
        elif key == "y(t)":
            self.expr_y = value
        elif key == "z(t)":
            self.expr_z = value

    def variables(self) -> dict[str, float]:
        return {"R": self.R, "pitch": self.pitch}

    def parameters(self) -> dict[str, float]:
        return {
            "t_min": self.t_min,
            "t_max": self.t_max,
            "segments": self.segments,
            "R": self.R,
            "pitch": self.pitch,
        }

    def set_parameter(self, key: str, value: float) -> None:
        if key == "t_min":
            self.t_min = value
        elif key == "t_max":
            self.t_max = max(value, self.t_min + 0.01)
        elif key == "segments":
            self.segments = max(3.0, min(512.0, value))
        elif key == "R":
            self.R = max(0.01, value)
        elif key == "pitch":
            self.pitch = value

    def validate_expressions(self) -> str | None:
        if self.t_max <= self.t_min:
            return "t_max must be greater than t_min"
        try:
            for t in (self.t_min, self.t_max, (self.t_min + self.t_max) * 0.5):
                ctx = {"t": t, **self.variables()}
                evaluate_expression(self.expr_x, ctx)
                evaluate_expression(self.expr_y, ctx)
                evaluate_expression(self.expr_z, ctx)
        except ExpressionError as exc:
            return str(exc)
        return None

    def mesh_spec(self) -> MeshSpec:
        self.last_error = self.validate_expressions()
        return MeshSpec(
            "parametric_curve",
            {
                "expr_x": self.expr_x,
                "expr_y": self.expr_y,
                "expr_z": self.expr_z,
                "t_min": self.t_min,
                "t_max": self.t_max,
                "segments": int(self.segments),
                "variables": self.variables(),
            },
        )

    def mesh_cache_key(self) -> tuple:
        base = super().mesh_cache_key()
        return base + (self.expr_x, self.expr_y, self.expr_z)
