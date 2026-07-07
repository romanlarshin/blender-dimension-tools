"""Snap engine — cursor-to-vertex snapping.

Finds the nearest mesh vertex near the mouse in screen space and returns its
world position. Does not modify the Scene.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from ..log import get_logger

_log = get_logger("engine.snap")


@dataclass(frozen=True)
class SnapResult:
    """Nearest mesh vertex under the cursor."""

    world_co: Vector


@contextmanager
def view3d_snap_context(context: bpy.types.Context):
    """Yield a context whose region and region_data refer to the 3D View window."""
    area = context.area
    if area is None or area.type != "VIEW_3D":
        _log.debug("view3d_snap_context: no active VIEW_3D area")
        yield context
        return

    window_region = next((region for region in area.regions if region.type == "WINDOW"), None)
    space = (
        context.space_data
        if context.space_data is not None and context.space_data.type == "VIEW_3D"
        else area.spaces.active
    )
    rv3d = space.region_3d if space is not None else None

    if window_region is None or rv3d is None:
        _log.debug("view3d_snap_context: missing window region or region_3d")
        yield context
        return

    with context.temp_override(
        area=area,
        region=window_region,
        space_data=space,
        region_data=rv3d,
    ):
        yield context


def _iter_view3d_mesh_objects(context: bpy.types.Context) -> Iterator[bpy.types.Object]:
    """Yield mesh objects visible in the active 3D Viewport."""
    region = context.region
    rv3d = context.region_data
    space = context.space_data

    if region is None or rv3d is None:
        _log.debug("find_nearest_vertex: invalid context.region or context.region_data")
        return

    if space is None or space.type != "VIEW_3D":
        _log.debug("find_nearest_vertex: context.space_data is not VIEW_3D")
        return

    depsgraph = context.evaluated_depsgraph_get()

    for obj in context.view_layer.objects:
        if obj.type != "MESH":
            continue
        if obj.hide_viewport:
            continue
        if obj.display_type == "WIRE":
            continue
        if not obj.visible_get(depsgraph=depsgraph, viewport=space):
            continue
        yield obj


def find_nearest_vertex(
    context: bpy.types.Context,
    event: bpy.types.Event,
    snap_radius: float,
) -> SnapResult | None:
    """Return the closest mesh vertex within ``snap_radius`` pixels of the mouse."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        _log.debug("find_nearest_vertex: aborted — region or region_data is None")
        return None

    if context.space_data is None or context.space_data.type != "VIEW_3D":
        _log.debug("find_nearest_vertex: aborted — not in an active 3D View")
        return None

    mouse_co = Vector((event.mouse_region_x, event.mouse_region_y))
    depsgraph = context.evaluated_depsgraph_get()
    best: SnapResult | None = None
    best_dist = snap_radius
    object_count = 0

    for obj in _iter_view3d_mesh_objects(context):
        object_count += 1
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.data
        if mesh is None or len(mesh.vertices) == 0:
            continue

        matrix = eval_obj.matrix_world

        for vert in mesh.vertices:
            world_co = matrix @ vert.co
            screen_co = view3d_utils.location_3d_to_region_2d(region, rv3d, world_co)
            if screen_co is None:
                continue

            dist = (mouse_co - screen_co).length
            if dist < best_dist:
                best_dist = dist
                best = SnapResult(world_co)

    if best is not None:
        _log.debug(
            "find_nearest_vertex: snap found at %s (objects scanned: %d)",
            best.world_co,
            object_count,
        )
    else:
        _log.debug(
            "find_nearest_vertex: snap result is None (objects scanned: %d, radius: %.1f)",
            object_count,
            snap_radius,
        )

    return best


def register() -> None:
    """Initialize the snap engine."""
    _log.debug("Snap engine registered")


def unregister() -> None:
    """Shut down the snap engine."""
    _log.debug("Snap engine unregistered")
