"""Offset stage geometry for linear dimension placement."""

from __future__ import annotations

from dataclasses import dataclass

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

OFFSET_AXIS_FREE = "FREE"
OFFSET_AXIS_X = "X"
OFFSET_AXIS_Y = "Y"
OFFSET_AXIS_Z = "Z"

WORLD_AXES = {
    OFFSET_AXIS_X: Vector((1.0, 0.0, 0.0)),
    OFFSET_AXIS_Y: Vector((0.0, 1.0, 0.0)),
    OFFSET_AXIS_Z: Vector((0.0, 0.0, 1.0)),
}


@dataclass(frozen=True)
class DimensionLayout:
    """World-space layout for a linear dimension preview."""

    point_a: Vector
    point_b: Vector
    dim_a: Vector
    dim_b: Vector
    text_center: Vector
    measured_distance: float


def _offset_direction(ab_dir: Vector, rv3d: bpy.types.RegionView3D) -> Vector:
    """Return a view-aligned direction perpendicular to the measured segment."""
    view_z = (rv3d.view_matrix.inverted().to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    offset_dir = ab_dir.cross(view_z)
    if offset_dir.length_squared < 1e-12:
        offset_dir = ab_dir.cross(Vector((0.0, 1.0, 0.0)))
    return offset_dir.normalized()


def _mouse_world(context: bpy.types.Context, event: bpy.types.Event, depth: Vector) -> Vector | None:
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None
    mouse_co = Vector((event.mouse_region_x, event.mouse_region_y))
    return view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_co, depth)


def compute_offset_vector(
    context: bpy.types.Context,
    event: bpy.types.Event,
    point_a: Vector,
    point_b: Vector,
    *,
    axis_lock: str = OFFSET_AXIS_FREE,
) -> Vector:
    """Compute a world-space offset vector from the current mouse position."""
    segment = point_b - point_a
    if segment.length_squared < 1e-12:
        return Vector((0.0, 0.0, 0.0))

    midpoint = (point_a + point_b) * 0.5
    mouse_world = _mouse_world(context, event, midpoint)
    if mouse_world is None:
        return Vector((0.0, 0.0, 0.0))

    delta = mouse_world - midpoint

    if axis_lock == OFFSET_AXIS_X:
        return Vector((delta.x, 0.0, 0.0))
    if axis_lock == OFFSET_AXIS_Y:
        return Vector((0.0, delta.y, 0.0))
    if axis_lock == OFFSET_AXIS_Z:
        return Vector((0.0, 0.0, delta.z))

    rv3d = context.region_data
    if rv3d is None:
        return Vector((0.0, 0.0, 0.0))

    offset_dir = _offset_direction(segment.normalized(), rv3d)
    distance = delta.dot(offset_dir)
    return offset_dir * distance


def compute_offset_distance(
    context: bpy.types.Context,
    event: bpy.types.Event,
    point_a: Vector,
    point_b: Vector,
    *,
    axis_lock: str = OFFSET_AXIS_FREE,
) -> float:
    """Return the scalar length of the world-space offset vector."""
    return compute_offset_vector(
        context,
        event,
        point_a,
        point_b,
        axis_lock=axis_lock,
    ).length


def build_dimension_layout(
    point_a: Vector,
    point_b: Vector,
    offset_vector: Vector,
) -> DimensionLayout | None:
    """Build extension, dimension line, and label positions using a fixed world offset."""
    segment = point_b - point_a
    if segment.length_squared < 1e-12:
        return None

    dim_a = point_a + offset_vector
    dim_b = point_b + offset_vector

    return DimensionLayout(
        point_a=point_a,
        point_b=point_b,
        dim_a=dim_a,
        dim_b=dim_b,
        text_center=(dim_a + dim_b) * 0.5,
        measured_distance=segment.length,
    )


def format_measured_distance(
    context: bpy.types.Context,
    distance: float,
    *,
    units: str = "SCENE",
    precision: int = 2,
) -> str:
    """Format the measured segment length for display."""
    if units == "NONE":
        return f"{distance:.{precision}f}"

    unit_settings = context.scene.unit_settings
    if unit_settings.system == "NONE":
        return f"{distance:.{precision}f}"

    return bpy.utils.units.to_string(
        unit_settings.system,
        "LENGTH",
        distance * unit_settings.scale_length,
        precision=precision,
    )
