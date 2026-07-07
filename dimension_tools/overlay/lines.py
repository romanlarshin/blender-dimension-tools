"""GPU drawing for dimension extension and dimension lines."""

from __future__ import annotations

import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..gpu.batch import LineBatch


def draw_world_lines(
    segments: list[Vector],
    color: tuple[float, float, float, float],
    *,
    line_width: float = 1.5,
) -> None:
    """Draw independent line segments in world space."""
    if len(segments) < 2:
        return
    batch = LineBatch()
    batch.add_segments(segments)
    batch.draw(color, line_width=line_width)


def draw_world_cross(
    center: Vector,
    size: float,
    color: tuple[float, float, float, float],
    *,
    line_width: float = 3.0,
) -> None:
    """Draw a visible 3D axis cross centered on ``center`` (POST_VIEW)."""
    half = size * 0.5
    cx, cy, cz = center.x, center.y, center.z
    batch = LineBatch()
    batch.add_segment(Vector((cx - half, cy, cz)), Vector((cx + half, cy, cz)))
    batch.add_segment(Vector((cx, cy - half, cz)), Vector((cx, cy + half, cz)))
    batch.add_segment(Vector((cx, cy, cz - half)), Vector((cx, cy, cz + half)))
    batch.draw(color, line_width=line_width)


def draw_world_point(
    center: Vector,
    color: tuple[float, float, float, float],
    *,
    size: float = 8.0,
) -> None:
    """Draw a visible world-space point marker (POST_VIEW)."""
    shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "POINTS", {"pos": [center]})
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.point_size_set(size)
    batch.draw(shader)
    gpu.state.point_size_set(1.0)
