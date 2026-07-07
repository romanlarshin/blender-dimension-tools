"""Logical dimension data — endpoints, chain membership, and display overrides.

A dimension stores only logical information (id, point A, point B, chain id,
text override, visibility, selection). It never stores geometry.
"""

from __future__ import annotations

import bpy
from mathutils import Vector

from ..engine.offset_engine import DimensionLayout, build_dimension_layout
from ..preferences import DIMTOOLS_AddonPreferences


def get_scene_state(scene: bpy.types.Scene):
    """Return the Dimension Tools scene state, creating access if missing."""
    return scene.dimtools


def resolve_anchor_world(context: bpy.types.Context, anchor) -> Vector | None:
    """Resolve a snap anchor to a current world-space position."""
    snap_type = anchor.snap_type
    if snap_type == "NONE":
        return None

    if snap_type == "ORIGIN":
        obj = bpy.data.objects.get(anchor.object_name)
        if obj is None:
            return None
        return obj.matrix_world.translation.copy()

    if snap_type == "GRID":
        return Vector(anchor.local_co)

    obj = bpy.data.objects.get(anchor.object_name)
    if obj is None or obj.type != "MESH":
        return None

    depsgraph = context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.data
    matrix = eval_obj.matrix_world

    if snap_type == "VERTEX":
        index = anchor.element_index
        if index < 0 or index >= len(mesh.vertices):
            return None
        return matrix @ mesh.vertices[index].co

    if snap_type == "EDGE_MID":
        index = anchor.element_index
        if index < 0 or index >= len(mesh.edges):
            return None
        edge = mesh.edges[index]
        v0 = matrix @ mesh.vertices[edge.vertices[0]].co
        v1 = matrix @ mesh.vertices[edge.vertices[1]].co
        return (v0 + v1) * 0.5

    if snap_type == "EDGE":
        index = anchor.element_index
        if index < 0 or index >= len(mesh.edges):
            return None
        edge = mesh.edges[index]
        v0 = matrix @ mesh.vertices[edge.vertices[0]].co
        v1 = matrix @ mesh.vertices[edge.vertices[1]].co
        return v0.lerp(v1, anchor.edge_param)

    if snap_type == "FACE":
        index = anchor.element_index
        if index < 0 or index >= len(mesh.polygons):
            return None
        return matrix @ mesh.polygons[index].center

    return None


def resolve_endpoints(context: bpy.types.Context, item) -> tuple[Vector, Vector]:
    """Return current world-space endpoints for a dimension item."""
    point_a = Vector(item.point_a)
    point_b = Vector(item.point_b)

    resolved_a = resolve_anchor_world(context, item.anchor_a)
    if resolved_a is not None:
        point_a = resolved_a

    resolved_b = resolve_anchor_world(context, item.anchor_b)
    if resolved_b is not None:
        point_b = resolved_b

    return point_a, point_b


def get_effective_color(context: bpy.types.Context, item) -> tuple[float, float, float, float]:
    """Return the display color for a dimension."""
    if item.use_custom_color:
        return tuple(item.color)
    prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
    return tuple(prefs.color)


def get_effective_precision(context: bpy.types.Context, item) -> int:
    """Return label decimal precision for a dimension."""
    if item.precision >= 0:
        return item.precision
    prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
    return int(prefs.precision)


def get_effective_units(context: bpy.types.Context, item) -> str:
    """Return the unit mode for a dimension label."""
    if item.units != "GLOBAL":
        return item.units
    prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
    return prefs.units


def get_label_text(context: bpy.types.Context, item, measured_distance: float) -> str:
    """Return the display label for a dimension."""
    if item.text_override:
        return item.text_override

    from ..engine.offset_engine import format_measured_distance

    return format_measured_distance(
        context,
        measured_distance,
        units=get_effective_units(context, item),
        precision=get_effective_precision(context, item),
    )


def build_layout(context: bpy.types.Context, item, rv3d=None) -> DimensionLayout | None:
    """Build a viewport layout for a stored dimension."""
    point_a, point_b = resolve_endpoints(context, item)
    return build_dimension_layout(point_a, point_b, Vector(item.offset_vector))


def get_text_world_position(layout: DimensionLayout, item) -> Vector:
    """Return the world position used for dimension text."""
    if item.use_custom_text_position:
        return Vector(item.text_position)
    return layout.text_center.copy()
