"""Batched GPU draw helpers for viewport overlays."""

from __future__ import annotations

import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


class LineBatch:
    """Accumulates line segments and draws them in a single GPU call."""

    __slots__ = ("_positions",)

    def __init__(self) -> None:
        self._positions: list[Vector] = []

    def clear(self) -> None:
        """Remove all accumulated segments."""
        self._positions.clear()

    def add_segment(self, start: Vector, end: Vector) -> None:
        """Append one line segment."""
        self._positions.append(start.copy())
        self._positions.append(end.copy())

    def add_segments(self, pairs: list[Vector]) -> None:
        """Append multiple coordinate pairs as independent segments."""
        for index in range(0, len(pairs) - 1, 2):
            self.add_segment(pairs[index], pairs[index + 1])

    @property
    def segment_count(self) -> int:
        """Return the number of line segments."""
        return len(self._positions) // 2

    def draw(
        self,
        color: tuple[float, float, float, float],
        *,
        line_width: float = 1.5,
    ) -> None:
        """Draw all accumulated segments using the polyline shader."""
        if len(self._positions) < 2:
            return

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        batch = batch_for_shader(shader, "LINES", {"pos": self._positions})
        shader.bind()
        shader.uniform_float("color", color)
        shader.uniform_float("lineWidth", line_width)
        viewport = gpu.state.viewport_get()
        shader.uniform_float("viewportSize", (float(viewport[2]), float(viewport[3])))
        batch.draw(shader)


class TriangleBatch:
    """Accumulates triangles and draws them in a single GPU call."""

    __slots__ = ("_positions",)

    def __init__(self) -> None:
        self._positions: list[Vector] = []

    def clear(self) -> None:
        """Remove all accumulated triangles."""
        self._positions.clear()

    def add_triangle(self, a: Vector, b: Vector, c: Vector) -> None:
        """Append one triangle."""
        self._positions.extend((a.copy(), b.copy(), c.copy()))

    def draw(self, color: tuple[float, float, float, float]) -> None:
        """Draw all accumulated triangles."""
        if len(self._positions) < 3:
            return

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        batch = batch_for_shader(shader, "TRIS", {"pos": self._positions})
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
