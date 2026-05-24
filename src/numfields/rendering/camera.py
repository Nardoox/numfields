"""Orbit camera for 3D viewport."""

from __future__ import annotations

import math

import glm


class OrbitCamera:
    def __init__(self) -> None:
        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.distance = 8.0
        self.yaw = math.radians(45.0)
        self.pitch = math.radians(25.0)
        self.fov = 45.0
        self.near = 0.05
        self.far = 500.0
        self.aspect = 1.0

    def eye_position(self) -> glm.vec3:
        x = self.distance * math.cos(self.pitch) * math.sin(self.yaw)
        y = self.distance * math.sin(self.pitch)
        z = self.distance * math.cos(self.pitch) * math.cos(self.yaw)
        return self.target + glm.vec3(x, y, z)

    def view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.eye_position(), self.target, glm.vec3(0.0, 1.0, 0.0))

    def projection_matrix(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.fov), max(self.aspect, 0.01), self.near, self.far)

    def orbit(self, dx: float, dy: float) -> None:
        self.yaw -= dx * 0.005
        self.pitch += dy * 0.005
        limit = math.radians(89.0)
        self.pitch = max(-limit, min(limit, self.pitch))

    def pan(self, dx: float, dy: float) -> None:
        eye = self.eye_position()
        forward = glm.normalize(self.target - eye)
        right = glm.normalize(glm.cross(forward, glm.vec3(0.0, 1.0, 0.0)))
        up = glm.cross(right, forward)
        scale = self.distance * 0.001
        self.target += right * (-dx * scale) + up * (dy * scale)

    def zoom(self, delta: float) -> None:
        self.distance *= 1.0 - delta * 0.1
        self.distance = max(0.5, min(200.0, self.distance))
