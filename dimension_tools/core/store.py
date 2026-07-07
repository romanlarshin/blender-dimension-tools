"""Runtime dimension store backed by Scene PropertyGroups."""

from __future__ import annotations

import uuid

import bpy
from mathutils import Vector

from ..engine.snap_engine import SnapResult
from . import chain as chain_module
from .dimension import get_scene_state


def generate_uid() -> str:
    """Create a unique dimension identifier."""
    return uuid.uuid4().hex


def _copy_snap_to_anchor(anchor, snap: SnapResult) -> None:
    """Copy snap result data into a PropertyGroup anchor."""
    anchor.snap_type = snap.snap_type
    anchor.object_name = snap.object_name
    anchor.element_index = snap.element_index
    anchor.element_index_b = snap.element_index_b
    anchor.local_co = snap.local_co if snap.local_co is not None else snap.world_co
    anchor.edge_param = snap.edge_param


def add_linear_dimension(
    context: bpy.types.Context,
    point_a: Vector,
    point_b: Vector,
    offset_vector: Vector,
    chain_uid: str,
    snap_a: SnapResult | None = None,
    snap_b: SnapResult | None = None,
) -> bpy.types.PropertyGroup:
    """Append a linear dimension to the scene and return the new item."""
    state = get_scene_state(context.scene)
    item = state.dimensions.add()
    item.uid = generate_uid()
    item.point_a = point_a
    item.point_b = point_b
    item.offset_vector = offset_vector
    item.offset = offset_vector.length
    item.chain_uid = chain_uid
    item.visible = True
    item.selected = False
    item.style = "LINEAR"
    item.units = "GLOBAL"
    item.precision = -1
    item.use_custom_color = False
    item.use_custom_text_position = False
    item.text_position = ((point_a + point_b) * 0.5)

    if snap_a is not None:
        _copy_snap_to_anchor(item.anchor_a, snap_a)
    if snap_b is not None:
        _copy_snap_to_anchor(item.anchor_b, snap_b)

    state.active_dimension_index = len(state.dimensions) - 1
    return item


def remove_dimension_by_uid(context: bpy.types.Context, uid: str) -> bool:
    """Remove a dimension by uid. Returns True when removed."""
    state = get_scene_state(context.scene)
    for index, item in enumerate(state.dimensions):
        if item.uid == uid:
            state.dimensions.remove(index)
            if state.active_dimension_index >= len(state.dimensions):
                state.active_dimension_index = len(state.dimensions) - 1
            chain_module.remove_orphan_chains(context.scene)
            return True
    return False


def remove_selected_dimensions(context: bpy.types.Context) -> int:
    """Remove all selected dimensions. Returns the number removed."""
    state = get_scene_state(context.scene)
    remove_indices = [index for index, item in enumerate(state.dimensions) if item.selected]
    for index in reversed(remove_indices):
        state.dimensions.remove(index)
    if state.active_dimension_index >= len(state.dimensions):
        state.active_dimension_index = len(state.dimensions) - 1
    chain_module.remove_orphan_chains(context.scene)
    return len(remove_indices)


def get_dimension_by_uid(context: bpy.types.Context, uid: str):
    """Return a dimension item for the given uid, or None."""
    state = get_scene_state(context.scene)
    for item in state.dimensions:
        if item.uid == uid:
            return item
    return None


def iter_visible_dimensions(context: bpy.types.Context):
    """Yield visible dimension items for the active scene."""
    state = get_scene_state(context.scene)
    for item in state.dimensions:
        if item.visible:
            yield item
