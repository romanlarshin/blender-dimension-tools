"""Edit dimension operators — move text and offset."""

from __future__ import annotations

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from ..core import dimension as dimension_core
from ..core import selection as selection_core
from ..core import store as dimension_store
from ..engine import offset_engine
from ..utils import viewport as viewport_utils


class DIMTOOLS_OT_move_dimension_text(bpy.types.Operator):
    """Move the text label of the selected dimension."""

    bl_idname = "dimtools.move_dimension_text"
    bl_label = "Move Dimension Text"
    bl_description = "Drag to reposition the label of the selected dimension"
    bl_options = {"REGISTER", "UNDO"}

    _target_uid: str = ""
    _initial_position: Vector | None = None

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return selection_core.get_first_selected(context.scene) is not None

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        item = selection_core.get_first_selected(context.scene)
        if item is None or context.region_data is None:
            return {"CANCELLED"}

        layout = dimension_core.build_layout(context, item, context.region_data)
        if layout is None:
            return {"CANCELLED"}

        self._target_uid = item.uid
        self._initial_position = dimension_core.get_text_world_position(layout, item).copy()
        item.use_custom_text_position = True
        item.text_position = self._initial_position

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("SCROLL_XY")
        context.workspace.status_text_set("Move text: drag | Click confirm | Esc cancel")
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        item = dimension_store.get_dimension_by_uid(context, self._target_uid)
        if item is None:
            return {"CANCELLED"}

        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return {"CANCELLED"}

        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            if self._initial_position is not None:
                item.text_position = self._initial_position
            context.window.cursor_modal_restore()
            context.workspace.status_text_set(None)
            viewport_utils.redraw_view3d(context)
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            context.window.cursor_modal_restore()
            context.workspace.status_text_set(None)
            viewport_utils.redraw_view3d(context)
            return {"FINISHED"}

        if event.type == "MOUSEMOVE":
            layout = dimension_core.build_layout(context, item, rv3d)
            if layout is None:
                return {"RUNNING_MODAL"}
            mouse_co = Vector((event.mouse_region_x, event.mouse_region_y))
            depth = dimension_core.get_text_world_position(layout, item)
            world_pos = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_co, depth)
            if world_pos is not None:
                item.text_position = world_pos
                item.use_custom_text_position = True
                viewport_utils.redraw_view3d(context)

        return {"RUNNING_MODAL"}

    def cancel(self, context: bpy.types.Context) -> None:
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        viewport_utils.redraw_view3d(context)


class DIMTOOLS_OT_move_dimension_offset(bpy.types.Operator):
    """Move the offset of the selected dimension."""

    bl_idname = "dimtools.move_dimension_offset"
    bl_label = "Move Dimension Offset"
    bl_description = "Drag to change the offset of the selected dimension"
    bl_options = {"REGISTER", "UNDO"}

    _target_uid: str = ""
    _initial_offset_vector: Vector | None = None

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return selection_core.get_first_selected(context.scene) is not None

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        item = selection_core.get_first_selected(context.scene)
        if item is None:
            return {"CANCELLED"}

        self._target_uid = item.uid
        self._initial_offset_vector = Vector(item.offset_vector)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("SCROLL_Y")
        context.workspace.status_text_set("Move offset: drag | Click confirm | Esc cancel")
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        target = dimension_store.get_dimension_by_uid(context, self._target_uid)
        if target is None:
            return {"CANCELLED"}

        point_a, point_b = dimension_core.resolve_endpoints(context, target)

        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            if self._initial_offset_vector is not None:
                target.offset_vector = self._initial_offset_vector.copy()
                target.offset = target.offset_vector.length
            context.window.cursor_modal_restore()
            context.workspace.status_text_set(None)
            viewport_utils.redraw_view3d(context)
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            context.window.cursor_modal_restore()
            context.workspace.status_text_set(None)
            viewport_utils.redraw_view3d(context)
            return {"FINISHED"}

        if event.type == "MOUSEMOVE":
            offset_vector = offset_engine.compute_offset_vector(context, event, point_a, point_b)
            target.offset_vector = offset_vector
            target.offset = offset_vector.length
            viewport_utils.redraw_view3d(context)

        return {"RUNNING_MODAL"}

    def cancel(self, context: bpy.types.Context) -> None:
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        viewport_utils.redraw_view3d(context)
