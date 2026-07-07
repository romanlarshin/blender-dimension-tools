"""Select dimension operator."""

from __future__ import annotations

import bpy

from ..core import selection as selection_core
from ..engine import draw_engine
from ..utils import viewport as viewport_utils


class DIMTOOLS_OT_select_dimension(bpy.types.Operator):
    """Select dimensions in the viewport by clicking them."""

    bl_idname = "dimtools.select_dimension"
    bl_label = "Select Dimension"
    bl_description = "Click dimensions to select them (Shift = add, Esc = exit)"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Requires an active 3D Viewport")
            return {"CANCELLED"}

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("EYEDROPPER")
        context.workspace.status_text_set("Select dimension: click | Shift add | Esc exit")
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            draw_engine.set_hover_uid(None)
            context.window.cursor_modal_restore()
            context.workspace.status_text_set(None)
            viewport_utils.redraw_view3d(context)
            return {"CANCELLED"}

        if event.type == "MOUSEMOVE":
            draw_engine.set_hover_uid(
                selection_core.hit_test(context, event.mouse_region_x, event.mouse_region_y)
            )
            viewport_utils.redraw_view3d(context)
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            hit_uid = selection_core.hit_test(context, event.mouse_region_x, event.mouse_region_y)
            if hit_uid is not None:
                selection_core.select_dimension(context.scene, hit_uid, extend=event.shift)
            elif not event.shift:
                selection_core.clear_selection(context.scene)
            viewport_utils.redraw_view3d(context)
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context: bpy.types.Context) -> None:
        draw_engine.set_hover_uid(None)
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        viewport_utils.redraw_view3d(context)
