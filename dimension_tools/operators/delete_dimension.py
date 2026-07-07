"""Delete dimension operator."""

from __future__ import annotations

import bpy

from ..core import selection as selection_core
from ..core import store as dimension_store
from ..utils import viewport as viewport_utils


class DIMTOOLS_OT_delete_dimension(bpy.types.Operator):
    """Delete selected dimensions from the scene."""

    bl_idname = "dimtools.delete_dimension"
    bl_label = "Delete Selected Dimensions"
    bl_description = "Remove all selected dimensions"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return bool(selection_core.get_selected(context.scene))

    def execute(self, context: bpy.types.Context) -> set[str]:
        removed = dimension_store.remove_selected_dimensions(context)
        if removed == 0:
            self.report({"WARNING"}, "No dimensions selected")
            return {"CANCELLED"}
        viewport_utils.redraw_view3d(context)
        self.report({"INFO"}, f"Deleted {removed} dimension(s)")
        return {"FINISHED"}
