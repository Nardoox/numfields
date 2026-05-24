"""Load combined GLSL sources for moderngl."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


def _split_stages(source: str) -> tuple[str, str]:
    if "#version" not in source:
        raise ValueError("Shader source must contain #version")
    parts = source.split("#ifdef VERTEX_SHADER")
    header = parts[0]
    rest = parts[1]
    vert_body, frag_part = rest.split("#ifdef FRAGMENT_SHADER", 1)
    vert = header + vert_body.replace("#endif", "").strip()
    frag = header + frag_part.replace("#endif", "").strip()
    return vert, frag


def load_shader_pair(name: str) -> tuple[str, str]:
    path = resources.files("numfields.rendering.shaders").joinpath(name)
    source = Path(path).read_text(encoding="utf-8")
    return _split_stages(source)
