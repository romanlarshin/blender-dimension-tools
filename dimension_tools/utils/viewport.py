"""Viewport utility helpers."""

from __future__ import annotations

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector


def redraw_view3d(context: bpy.types.Context | None = None) -> None:
    """Tag every 3D View area for redraw."""
    window_manager = bpy.context.window_manager if context is None else context.window_manager
    if window_manager is None:
        return
    for window in window_manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def pixel_size_to_world(
    context: bpy.types.Context,
    world_pos: Vector,
    pixel_size: float,
) -> float:
    """Convert a pixel length to world units at ``world_pos``."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return max(pixel_size * 0.01, 0.01)

    screen_pos = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
    if screen_pos is None:
        return max(pixel_size * 0.01, 0.01)

    offset_screen = screen_pos + Vector((pixel_size, 0.0))
    offset_world = view3d_utils.region_2d_to_location_3d(region, rv3d, offset_screen, world_pos)
    if offset_world is None:
        return max(pixel_size * 0.01, 0.01)

    return max((offset_world - world_pos).length, 0.005)


def world_to_region(
    context: bpy.types.Context,
    world_pos: Vector,
) -> Vector | None:
    """Project a world position to region 2D coordinates."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None
    return view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
