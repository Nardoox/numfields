"""Core domain types: dimensions, IDs, transforms."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import NewType

import glm

BodyId = NewType("BodyId", str)


class Dimension(IntEnum):
    LINE = 1
    SURFACE = 2
    VOLUME = 3


@dataclass
class Transform:
    position: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0))
    rotation: glm.quat = field(default_factory=lambda: glm.quat(1.0, 0.0, 0.0, 0.0))
    scale: float = 1.0

    def matrix(self) -> glm.mat4:
        t = glm.translate(glm.mat4(1.0), self.position)
        r = glm.mat4_cast(self.rotation)
        s = glm.scale(glm.mat4(1.0), glm.vec3(self.scale))
        return t * r * s

    def euler_degrees(self) -> glm.vec3:
        return glm.degrees(glm.eulerAngles(self.rotation))

    def set_euler_degrees(self, pitch: float, yaw: float, roll: float) -> None:
        self.rotation = glm.quat(glm.radians(glm.vec3(pitch, yaw, roll)))


def new_body_id() -> BodyId:
    return BodyId(str(uuid.uuid4()))
