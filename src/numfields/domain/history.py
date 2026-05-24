"""Undo/redo history for scene edits."""

from __future__ import annotations

from typing import TYPE_CHECKING

from numfields.domain.snapshot import SceneSnapshot, capture_scene, restore_scene

if TYPE_CHECKING:
    from numfields.domain.scene import Scene


class SceneHistory:
    def __init__(self, *, limit: int = 30) -> None:
        self._limit = limit
        self._undo: list[SceneSnapshot] = []
        self._redo: list[SceneSnapshot] = []
        self._replaying = False
        self._group_active = False
        self._group_snapshot: SceneSnapshot | None = None

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def record(self, scene: Scene) -> None:
        if self._replaying:
            return
        self._cancel_group()
        self._push_undo(capture_scene(scene))
        self._redo.clear()

    def _cancel_group(self) -> None:
        self._group_active = False
        self._group_snapshot = None

    def start_group(self, scene: Scene) -> None:
        if self._replaying or self._group_active:
            return
        self._group_active = True
        self._group_snapshot = capture_scene(scene)

    def end_group(self, scene: Scene) -> None:
        if self._replaying or not self._group_active or self._group_snapshot is None:
            self._group_active = False
            self._group_snapshot = None
            return
        before = self._group_snapshot
        after = capture_scene(scene)
        self._group_active = False
        self._group_snapshot = None
        if before == after:
            return
        self._push_undo(before)
        self._redo.clear()

    def undo(self, scene: Scene) -> bool:
        if not self._undo:
            return False
        self._replaying = True
        try:
            self._redo.append(capture_scene(scene))
            restore_scene(scene, self._undo.pop())
        finally:
            self._replaying = False
        return True

    def redo(self, scene: Scene) -> bool:
        if not self._redo:
            return False
        self._replaying = True
        try:
            self._undo.append(capture_scene(scene))
            restore_scene(scene, self._redo.pop())
        finally:
            self._replaying = False
        return True

    def _push_undo(self, snapshot: SceneSnapshot) -> None:
        if self._undo and self._undo[-1] == snapshot:
            return
        self._undo.append(snapshot)
        if len(self._undo) > self._limit:
            self._undo.pop(0)
