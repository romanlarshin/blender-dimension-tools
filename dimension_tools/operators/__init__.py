"""Blender operators for dimension tool interaction."""

from __future__ import annotations

import bpy

from .delete_dimension import DIMTOOLS_OT_delete_dimension
from .dimension_ops import (
    DIMTOOLS_OT_clear_dimension_text,
    DIMTOOLS_OT_deselect_all_dimensions,
    DIMTOOLS_OT_dimension_list_action,
    DIMTOOLS_OT_select_all_dimensions,
    DIMTOOLS_OT_set_dimension_text,
    DIMTOOLS_OT_toggle_dimension_visibility,
)
from .edit_dimension import DIMTOOLS_OT_move_dimension_offset, DIMTOOLS_OT_move_dimension_text
from .select_dimension import DIMTOOLS_OT_select_dimension
from .start_dimension import DIMTOOLS_OT_start_linear_dimension

classes = (
    DIMTOOLS_OT_start_linear_dimension,
    DIMTOOLS_OT_select_dimension,
    DIMTOOLS_OT_delete_dimension,
    DIMTOOLS_OT_move_dimension_text,
    DIMTOOLS_OT_move_dimension_offset,
    DIMTOOLS_OT_select_all_dimensions,
    DIMTOOLS_OT_deselect_all_dimensions,
    DIMTOOLS_OT_toggle_dimension_visibility,
    DIMTOOLS_OT_set_dimension_text,
    DIMTOOLS_OT_clear_dimension_text,
    DIMTOOLS_OT_dimension_list_action,
)

_addon_keymaps: list[tuple] = []


def register() -> None:
    """Register dimension tool operators."""
    for cls in classes:
        bpy.utils.register_class(cls)

    window_manager = bpy.context.window_manager
    if window_manager is not None:
        keymap = window_manager.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        for key in ("DEL", "X"):
            keymap_item = keymap.keymap_items.new(
                DIMTOOLS_OT_delete_dimension.bl_idname,
                type=key,
                value="PRESS",
            )
            _addon_keymaps.append((keymap, keymap_item))

    wm = bpy.context.window_manager
    if wm is not None:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            DIMTOOLS_OT_start_linear_dimension.bl_idname,
            type="D",
            value="PRESS",
            alt=True,
        )
        _addon_keymaps.append((km, kmi))


def unregister() -> None:
    """Unregister dimension tool operators."""
    for keymap, keymap_item in _addon_keymaps:
        keymap.keymap_items.remove(keymap_item)
    _addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
