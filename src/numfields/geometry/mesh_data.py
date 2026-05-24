"""CPU-side mesh buffers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class MeshData:
    positions: np.ndarray
    normals: np.ndarray
    indices: np.ndarray

    def interleaved_vertices(self) -> np.ndarray:
        return np.hstack([self.positions, self.normals]).astype("f4")

    @property
    def vertex_count(self) -> int:
        return len(self.positions)

    @property
    def triangle_count(self) -> int:
        return len(self.indices) // 3
