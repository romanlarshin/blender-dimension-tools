"""Dimension selection state and queries."""

from __future__ import annotations

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from .dimension import build_layout, get_scene_state, get_text_world_position, resolve_endpoints

HIT_LINE_THRESHOLD = 12.0
HIT_TEXT_THRESHOLD = 18.0


def clear_selection(scene: bpy.types.Scene) -> None:
    """Clear selection on all dimensions."""
    for item in get_scene_state(scene).dimensions:
        item.selected = False


def select_dimension(
    scene: bpy.types.Scene,
    uid: str,
    *,
    extend: bool = False,
) -> bool:
    """Select a dimension by uid. Returns True when found."""
    if not extend:
        clear_selection(scene)

    for index, item in enumerate(get_scene_state(scene).dimensions):
        if item.uid == uid:
            item.selected = True
            get_scene_state(scene).active_dimension_index = index
            return True
    return False


def get_selected(scene: bpy.types.Scene) -> list:
    """Return all selected dimension items."""
    return [item for item in get_scene_state(scene).dimensions if item.selected]


def get_first_selected(scene: bpy.types.Scene):
    """Return the first selected dimension item, if any."""
    selected = get_selected(scene)
    return selected[0] if selected else None


def _dist_point_to_segment_2d(point: Vector, start: Vector, end: Vector) -> float:
    """Return the shortest distance from a 2D point to a segment."""
    segment = end - start
    length_sq = segment.length_squared
    if length_sq < 1e-12:
        return (point - start).length
    t = max(0.0, min(1.0, (point - start).dot(segment) / length_sq))
    projection = start + segment * t
    return (point - projection).length


def hit_test(context: bpy.types.Context, mouse_x: float, mouse_y: float) -> str | None:
    """Return the uid of the dimension under the cursor, if any."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None

    mouse = Vector((mouse_x, mouse_y))
    best_uid: str | None = None
    best_dist = float("inf")

    for item in get_scene_state(context.scene).dimensions:
        if not item.visible:
            continue

        layout = build_layout(context, item, rv3d)
        if layout is None:
            continue

        dim_a_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, layout.dim_a)
        dim_b_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, layout.dim_b)
        if dim_a_2d is None or dim_b_2d is None:
            continue

        line_dist = _dist_point_to_segment_2d(mouse, dim_a_2d, dim_b_2d)
        if line_dist <= HIT_LINE_THRESHOLD and line_dist < best_dist:
            best_dist = line_dist
            best_uid = item.uid

        text_pos = get_text_world_position(layout, item)
        text_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, text_pos)
        if text_2d is not None:
            text_dist = (mouse - text_2d).length
            if text_dist <= HIT_TEXT_THRESHOLD and text_dist < best_dist:
                best_dist = text_dist
                best_uid = item.uid

        point_a, point_b = resolve_endpoints(context, item)
        for endpoint in (point_a, point_b):
            endpoint_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, endpoint)
            if endpoint_2d is None:
                continue
            endpoint_dist = (mouse - endpoint_2d).length
            if endpoint_dist <= HIT_LINE_THRESHOLD and endpoint_dist < best_dist:
                best_dist = endpoint_dist
                best_uid = item.uid

    return best_uid
