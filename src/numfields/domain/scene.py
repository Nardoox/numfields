"""Scene graph — bodies, selection, change notifications."""

from __future__ import annotations

from collections.abc import Callable

from numfields.domain.bodies.base import GeometricBody
from numfields.domain.types import BodyId

ChangeCallback = Callable[[], None]


class Scene:
    def __init__(self) -> None:
        self._bodies: list[GeometricBody] = []
        self._selected_id: BodyId | None = None
        self._on_changed: list[ChangeCallback] = []
        self._version = 0

    @property
    def version(self) -> int:
        return self._version

    def on_changed(self, callback: ChangeCallback) -> None:
        self._on_changed.append(callback)

    def _notify(self) -> None:
        self._version += 1
        for cb in self._on_changed:
            cb()

    def bodies(self) -> list[GeometricBody]:
        return list(self._bodies)

    def add(self, body: GeometricBody, *, select: bool = True) -> GeometricBody:
        self._bodies.append(body)
        if select:
            self._selected_id = body.id
        self._notify()
        return body

    def remove(self, body_id: BodyId) -> bool:
        for i, b in enumerate(self._bodies):
            if b.id == body_id:
                self._bodies.pop(i)
                if self._selected_id == body_id:
                    self._selected_id = self._bodies[-1].id if self._bodies else None
                self._notify()
                return True
        return False

    def get(self, body_id: BodyId) -> GeometricBody | None:
        for b in self._bodies:
            if b.id == body_id:
                return b
        return None

    def select(self, body_id: BodyId | None) -> None:
        if self._selected_id != body_id:
            self._selected_id = body_id
            self._notify()

    def selected(self) -> GeometricBody | None:
        if self._selected_id is None:
            return None
        return self.get(self._selected_id)

    def selected_id(self) -> BodyId | None:
        return self._selected_id

    def mark_dirty(self) -> None:
        self._notify()
