"""Import all body types to register them with BodyRegistry."""

from numfields.domain.bodies.base import GeometricBody, MeshSpec
from numfields.domain.bodies.line import segment  # noqa: F401
from numfields.domain.bodies.registry import create_body, list_body_types
from numfields.domain.bodies.surface import disk, rectangle  # noqa: F401
from numfields.domain.bodies.volume import box, cylinder, sphere  # noqa: F401

__all__ = ["GeometricBody", "MeshSpec", "create_body", "list_body_types"]

