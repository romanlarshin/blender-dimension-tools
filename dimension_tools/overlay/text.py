"""GPU drawing for dimension labels (POST_PIXEL)."""

from __future__ import annotations

import blf
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

SNAP_CROSS_PIXEL_SIZE = 14.0
SNAP_CROSS_LINE_WIDTH = 2.0


def draw_region_cross(
    context,
    world_pos: Vector,
    color: tuple[float, float, float, float],
    *,
    size_px: float = SNAP_CROSS_PIXEL_SIZE,
    line_width: float = SNAP_CROSS_LINE_WIDTH,
) -> None:
    """Draw a screen-space cross at a projected world position (POST_PIXEL)."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return

    screen_pos = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
    if screen_pos is None:
        return

    x = screen_pos.x
    y = screen_pos.y
    coords = [
        (x - size_px, y),
        (x + size_px, y),
        (x, y - size_px),
        (x, y + size_px),
    ]

    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": coords})
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.line_width_set(line_width)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)


def draw_world_label(
    context,
    text: str,
    world_pos: Vector,
    *,
    font_id: int,
    size: int,
    color: tuple[float, float, float, float],
) -> None:
    """Draw a label at a projected world position using BLF (POST_PIXEL)."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None or not text:
        return

    screen_pos = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
    if screen_pos is None:
        return

    blf.size(font_id, size)
    blf.position(font_id, screen_pos.x + 1, screen_pos.y - 1, 0)
    blf.color(font_id, 0.0, 0.0, 0.0, color[3] * 0.65)
    blf.draw(font_id, text)
    blf.position(font_id, screen_pos.x, screen_pos.y, 0)
    blf.color(font_id, color[0], color[1], color[2], color[3])
    blf.draw(font_id, text)
