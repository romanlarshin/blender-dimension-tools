"""GPU drawing for snap preview points."""

from __future__ import annotations

import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


def draw_world_point(co: Vector, color: tuple[float, float, float, float], size: float = 8.0) -> None:
    """Draw a single world-space point in a POST_VIEW draw handler."""
    shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "POINTS", {"pos": [co]})
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.point_size_set(size)
    batch.draw(shader)


def draw_world_points(
    coords: list[Vector],
    color: tuple[float, float, float, float],
    size: float = 8.0,
) -> None:
    """Draw multiple world-space points in a POST_VIEW draw handler."""
    if not coords:
        return

    shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "POINTS", {"pos": coords})
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.point_size_set(size)
    batch.draw(shader)
