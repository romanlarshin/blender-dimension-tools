"""GPU drawing for dimension extension and dimension lines."""

from __future__ import annotations

import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


def draw_world_lines(
    segments: list[Vector],
    color: tuple[float, float, float, float],
) -> None:
    """Draw independent line segments in world space using the LINES primitive."""
    if len(segments) < 2:
        return

    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": segments})
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.line_width_set(3.0)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)


def draw_world_cross(
    center: Vector,
    size: float,
    color: tuple[float, float, float, float],
) -> None:
    """Draw a 3D axis cross centered on ``center`` with the given full span."""
    half = size * 0.5
    cx, cy, cz = center.x, center.y, center.z
    segments = [
        Vector((cx - half, cy, cz)),
        Vector((cx + half, cy, cz)),
        Vector((cx, cy - half, cz)),
        Vector((cx, cy + half, cz)),
        Vector((cx, cy, cz - half)),
        Vector((cx, cy, cz + half)),
    ]
    draw_world_lines(segments, color)


def draw_world_polyline(
    points: list[Vector],
    color: tuple[float, float, float, float],
    width: float = 1.5,
) -> None:
    """Draw a connected polyline in world space."""
    if len(points) < 2:
        return

    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINE_STRIP", {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)
    shader.uniform_float("lineWidth", width)
    batch.draw(shader)
