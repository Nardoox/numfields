"""Offscreen framebuffer for ImGui viewport."""

from __future__ import annotations

import moderngl


class ViewportFBO:
    def __init__(self, ctx: moderngl.Context) -> None:
        self._ctx = ctx
        self._fbo: moderngl.Framebuffer | None = None
        self._color: moderngl.Texture | None = None
        self._picking: moderngl.Texture | None = None
        self._depth: moderngl.RenderBuffer | None = None
        self.width = 1
        self.height = 1

    @property
    def texture_id(self) -> int:
        if self._color is None:
            return 0
        return self._color.glo

    def resize(self, width: int, height: int) -> None:
        width = max(1, int(width))
        height = max(1, int(height))
        if width == self.width and height == self.height and self._fbo is not None:
            return
        self.release()
        self.width = width
        self.height = height
        self._color = self._ctx.texture((width, height), 4)
        self._picking = self._ctx.texture((width, height), 1, dtype='i4')
        self._depth = self._ctx.depth_renderbuffer((width, height))
        self._fbo = self._ctx.framebuffer(
            color_attachments=[self._color, self._picking],
            depth_attachment=self._depth,
        )

    def bind(self) -> None:
        if self._fbo is not None:
            self._fbo.use()

    def clear(self, r: float = 0.12, g: float = 0.13, b: float = 0.15) -> None:
        if self._fbo is not None:
            self._fbo.clear(r, g, b, 1.0, depth=1.0)
            # Clear picking texture to 0
            self._picking.write(b'\x00' * (self.width * self.height * 4))

    def release(self) -> None:
        if self._fbo is not None:
            self._fbo.release()
            self._fbo = None
        if self._color is not None:
            self._color.release()
            self._color = None
        if self._picking is not None:
            self._picking.release()
            self._picking = None
        if self._depth is not None:
            self._depth.release()
            self._depth = None

    def read_picking(self, x: int, y: int) -> int:
        if self._fbo is None or self._picking is None:
            return 0
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        # OpenGL Y origin is bottom-left, ImGui mouse coordinates are top-left
        y = self.height - 1 - y
        data = self._fbo.read(components=1, attachment=1, dtype='i4', viewport=(x, y, 1, 1))
        import struct
        return struct.unpack('i', data)[0]
