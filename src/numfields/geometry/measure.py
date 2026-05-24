"""Analytical measure (length, area, volume) for geometric bodies."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from numfields.geometry.expression_eval import evaluate_expression

if TYPE_CHECKING:
    from numfields.domain.bodies.base import GeometricBody


def body_measure(body: GeometricBody) -> float:
    scale = max(body.transform.scale, 0.0)
    params = body.parameters()
    type_id = body.type_id

    if body.dimension.name == "LINE":
        length = _line_measure(type_id, params, body)
        return length * scale
    if body.dimension.name == "SURFACE":
        area = _surface_measure(type_id, params)
        return area * scale * scale
    volume = _volume_measure(type_id, params)
    return volume * scale * scale * scale


def _line_measure(type_id: str, params: dict[str, float], body: GeometricBody) -> float:
    if type_id == "segment":
        return params["length"]
    if type_id == "circle":
        return 2.0 * math.pi * params["radius"]
    if type_id == "rect_outline":
        return 2.0 * (params["width"] + params["height"])
    if type_id == "coil":
        turns = max(1.0, params["windings"])
        r = params["radius"]
        h = params["length"]
        return math.sqrt((2.0 * math.pi * r * turns) ** 2 + h * h)
    if type_id == "parametric_curve":
        return _parametric_curve_length(body)
    raise ValueError(f"No line measure for type: {type_id}")


def _parametric_curve_length(body: GeometricBody) -> float:
    expr_x = getattr(body, "expr_x", "0")
    expr_y = getattr(body, "expr_y", "0")
    expr_z = getattr(body, "expr_z", "0")
    t_min = getattr(body, "t_min", 0.0)
    t_max = getattr(body, "t_max", 1.0)
    segments = int(getattr(body, "segments", 64))
    variables = body.variables() if hasattr(body, "variables") else {}

    count = max(3, segments)
    ts = np.linspace(t_min, t_max, count + 1)
    points: list[tuple[float, float, float]] = []
    for t in ts:
        ctx = {"t": float(t), **variables}
        try:
            points.append(
                (
                    evaluate_expression(expr_x, ctx),
                    evaluate_expression(expr_y, ctx),
                    evaluate_expression(expr_z, ctx),
                )
            )
        except Exception:
            return 0.0

    length = 0.0
    for i in range(len(points) - 1):
        length += math.dist(points[i], points[i + 1])
    return length


def _surface_measure(type_id: str, params: dict[str, float]) -> float:
    if type_id == "disk":
        r = params["radius"]
        return math.pi * r * r
    if type_id == "rectangle":
        return params["width"] * params["height"]
    if type_id == "sphere_shell":
        r = params["radius"]
        return 4.0 * math.pi * r * r
    if type_id == "box_shell":
        sx, sy, sz = params["size_x"], params["size_y"], params["size_z"]
        return 2.0 * (sx * sy + sy * sz + sx * sz)
    if type_id == "cylinder_shell":
        r, h = params["radius"], params["height"]
        return 2.0 * math.pi * r * h + 2.0 * math.pi * r * r
    raise ValueError(f"No surface measure for type: {type_id}")


def _volume_measure(type_id: str, params: dict[str, float]) -> float:
    if type_id == "sphere":
        r = params["radius"]
        return (4.0 / 3.0) * math.pi * r * r * r
    if type_id == "box":
        return params["size_x"] * params["size_y"] * params["size_z"]
    if type_id == "cylinder":
        r, h = params["radius"], params["height"]
        return math.pi * r * r * h
    raise ValueError(f"No volume measure for type: {type_id}")
