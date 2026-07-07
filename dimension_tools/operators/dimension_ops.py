"""Additional dimension management operators."""

from __future__ import annotations

import bpy

from ..core import selection as selection_core
from ..core import store as dimension_store
from ..core.dimension import get_scene_state
from ..utils import viewport as viewport_utils


class DIMTOOLS_OT_select_all_dimensions(bpy.types.Operator):
    """Select all dimensions in the scene."""

    bl_idname = "dimtools.select_all_dimensions"
    bl_label = "Select All Dimensions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        for item in get_scene_state(context.scene).dimensions:
            item.selected = True
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}


class DIMTOOLS_OT_deselect_all_dimensions(bpy.types.Operator):
    """Clear dimension selection."""

    bl_idname = "dimtools.deselect_all_dimensions"
    bl_label = "Deselect All Dimensions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        selection_core.clear_selection(context.scene)
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}


class DIMTOOLS_OT_toggle_dimension_visibility(bpy.types.Operator):
    """Toggle visibility of selected dimensions."""

    bl_idname = "dimtools.toggle_dimension_visibility"
    bl_label = "Toggle Visibility"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return bool(selection_core.get_selected(context.scene))

    def execute(self, context: bpy.types.Context) -> set[str]:
        selected = selection_core.get_selected(context.scene)
        target = not selected[0].visible
        for item in selected:
            item.visible = target
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}


class DIMTOOLS_OT_set_dimension_text(bpy.types.Operator):
    """Set a custom text override on selected dimensions."""

    bl_idname = "dimtools.set_dimension_text"
    bl_label = "Set Dimension Text"
    bl_options = {"REGISTER", "UNDO"}

    text: bpy.props.StringProperty(name="Text", default="")

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return bool(selection_core.get_selected(context.scene))

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        first = selection_core.get_first_selected(context.scene)
        if first is not None:
            self.text = first.text_override
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.prop(self, "text")

    def execute(self, context: bpy.types.Context) -> set[str]:
        for item in selection_core.get_selected(context.scene):
            item.text_override = self.text.strip()
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}


class DIMTOOLS_OT_clear_dimension_text(bpy.types.Operator):
    """Clear custom text overrides on selected dimensions."""

    bl_idname = "dimtools.clear_dimension_text"
    bl_label = "Clear Dimension Text"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return bool(selection_core.get_selected(context.scene))

    def execute(self, context: bpy.types.Context) -> set[str]:
        for item in selection_core.get_selected(context.scene):
            item.text_override = ""
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}


class DIMTOOLS_OT_dimension_list_action(bpy.types.Operator):
    """Select or toggle visibility for one dimension from the UI list."""

    bl_idname = "dimtools.dimension_list_action"
    bl_label = "Dimension List Action"
    bl_options = {"REGISTER", "UNDO"}

    uid: bpy.props.StringProperty()
    action: bpy.props.EnumProperty(
        items=[
            ("SELECT", "Select", ""),
            ("TOGGLE_VISIBLE", "Toggle Visible", ""),
        ],
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        item = dimension_store.get_dimension_by_uid(context, self.uid)
        if item is None:
            return {"CANCELLED"}
        if self.action == "SELECT":
            selection_core.select_dimension(context.scene, self.uid, extend=False)
        elif self.action == "TOGGLE_VISIBLE":
            item.visible = not item.visible
        viewport_utils.redraw_view3d(context)
        return {"FINISHED"}
