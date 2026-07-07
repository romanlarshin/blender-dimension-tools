"""Start linear dimension operator — modal tool entry point."""

from __future__ import annotations

import bpy
from mathutils import Vector

from ..core import store as dimension_store
from ..engine import chain_engine, modal_engine, offset_engine, snap_engine
from ..engine.offset_engine import (
    OFFSET_AXIS_FREE,
    OFFSET_AXIS_X,
    OFFSET_AXIS_Y,
    OFFSET_AXIS_Z,
)
from ..overlay import snap_preview
from ..utils import viewport as viewport_utils


def _update_snap(context: bpy.types.Context, event: bpy.types.Event) -> None:
    session = modal_engine.get_session()
    if session is None:
        return
    with snap_engine.view3d_snap_context(context) as snap_context:
        session.snap_result = snap_engine.find_nearest_snap(snap_context, event)
    viewport_utils.redraw_view3d(context)


def _update_offset(context: bpy.types.Context, event: bpy.types.Event) -> None:
    session = modal_engine.get_session()
    if session is None or session.first_snap is None or session.second_snap is None:
        return
    session.offset_vector = offset_engine.compute_offset_vector(
        context,
        event,
        session.first_snap.world_co,
        session.second_snap.world_co,
        axis_lock=session.offset_axis_lock,
    )
    viewport_utils.redraw_view3d(context)


def _set_offset_axis_lock(
    context: bpy.types.Context,
    session: modal_engine.ModalSession,
    event: bpy.types.Event,
    axis_lock: str,
) -> None:
    session.offset_axis_lock = axis_lock
    if session.first_snap is not None and session.second_snap is not None:
        session.offset_vector = offset_engine.compute_offset_vector(
            context,
            event,
            session.first_snap.world_co,
            session.second_snap.world_co,
            axis_lock=session.offset_axis_lock,
        )
    viewport_utils.redraw_view3d(context)


def _create_dimension(context: bpy.types.Context, session: modal_engine.ModalSession) -> bool:
    if session.first_snap is None or session.second_snap is None:
        return False
    if session.first_snap.world_co.to_tuple() == session.second_snap.world_co.to_tuple():
        return False

    offset_vector = session.offset_vector.copy()
    chain_uid = chain_engine.compute_chain_uid(
        context,
        session.first_snap.world_co,
        session.second_snap.world_co,
        offset_vector,
    )
    dimension_store.add_linear_dimension(
        context,
        session.first_snap.world_co.copy(),
        session.second_snap.world_co.copy(),
        offset_vector,
        chain_uid,
        snap_a=session.first_snap,
        snap_b=session.second_snap,
    )
    modal_engine.reset_for_next_dimension(session)
    return True


class DIMTOOLS_OT_start_linear_dimension(bpy.types.Operator):
    """Place linear dimensions in a persistent modal session."""

    bl_idname = "dimtools.start_linear_dimension"
    bl_label = "Linear Dimension"
    bl_description = "Create linear dimensions until Esc"
    bl_options = {"REGISTER", "UNDO"}

    _draw_handle_view = None
    _draw_handle_pixel = None

    def _set_status(self, context: bpy.types.Context) -> None:
        context.workspace.status_text_set(modal_engine.status_text(modal_engine.get_session()))

    def _add_draw_handlers(self) -> None:
        if self._draw_handle_view is None:
            self._draw_handle_view = bpy.types.SpaceView3D.draw_handler_add(
                snap_preview.draw_modal_preview,
                (),
                "WINDOW",
                "POST_VIEW",
            )
        if self._draw_handle_pixel is None:
            self._draw_handle_pixel = bpy.types.SpaceView3D.draw_handler_add(
                snap_preview.draw_modal_pixel,
                (),
                "WINDOW",
                "POST_PIXEL",
            )

    def _remove_draw_handlers(self, context: bpy.types.Context) -> None:
        if self._draw_handle_view is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle_view, "WINDOW")
            self._draw_handle_view = None
        if self._draw_handle_pixel is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle_pixel, "WINDOW")
            self._draw_handle_pixel = None
        viewport_utils.redraw_view3d(context)

    def _finish_modal(self, context: bpy.types.Context) -> None:
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        self._remove_draw_handlers(context)
        modal_engine.end_session()

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Requires an active 3D Viewport")
            return {"CANCELLED"}

        modal_engine.start_session()
        self._draw_handle_view = None
        self._draw_handle_pixel = None
        self._add_draw_handlers()
        _update_snap(context, event)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("CROSSHAIR")
        self._set_status(context)
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        session = modal_engine.get_session()

        if event.type == "ESC" and event.value == "PRESS":
            self._finish_modal(context)
            return {"CANCELLED"}

        if event.type == "BACKSPACE" and event.value == "PRESS" and session is not None:
            if modal_engine.undo_last_point(session):
                _update_snap(context, event)
                self._set_status(context)
                viewport_utils.redraw_view3d(context)
            return {"RUNNING_MODAL"}

        if event.type == "RIGHTMOUSE" and event.value == "PRESS" and session is not None:
            if session.offset_mode or session.first_snap is not None:
                modal_engine.undo_last_point(session)
                _update_snap(context, event)
                self._set_status(context)
                viewport_utils.redraw_view3d(context)
                return {"RUNNING_MODAL"}
            self._finish_modal(context)
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            if session is not None and session.offset_mode:
                if _create_dimension(context, session):
                    _update_snap(context, event)
                    self._set_status(context)
                    self.report({"INFO"}, "Dimension created")
                else:
                    self.report({"WARNING"}, "Could not create dimension")
                viewport_utils.redraw_view3d(context)
                return {"RUNNING_MODAL"}

            if session is not None and session.snap_result is not None:
                if session.first_snap is None:
                    session.first_snap = snap_engine.copy_snap_result(session.snap_result)
                    session.first_point = session.first_snap.world_co.copy()
                    self._set_status(context)
                elif session.second_snap is None:
                    session.second_snap = snap_engine.copy_snap_result(session.snap_result)
                    session.snap_result = session.second_snap
                    session.offset_mode = True
                    session.offset_vector = Vector((0.0, 0.0, 0.0))
                    session.offset_axis_lock = OFFSET_AXIS_FREE
                    _update_offset(context, event)
                    self._set_status(context)
                viewport_utils.redraw_view3d(context)
            return {"RUNNING_MODAL"}

        if event.type == "MOUSEMOVE":
            if session is not None and session.offset_mode:
                _update_offset(context, event)
            elif session is not None:
                _update_snap(context, event)
            return {"RUNNING_MODAL"}

        if session is not None and session.offset_mode and event.value == "PRESS":
            if event.type == "X":
                _set_offset_axis_lock(context, session, event, OFFSET_AXIS_X)
                self._set_status(context)
                return {"RUNNING_MODAL"}
            if event.type == "Y":
                _set_offset_axis_lock(context, session, event, OFFSET_AXIS_Y)
                self._set_status(context)
                return {"RUNNING_MODAL"}
            if event.type == "Z":
                _set_offset_axis_lock(context, session, event, OFFSET_AXIS_Z)
                self._set_status(context)
                return {"RUNNING_MODAL"}
            if event.type == "F":
                _set_offset_axis_lock(context, session, event, OFFSET_AXIS_FREE)
                self._set_status(context)
                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context: bpy.types.Context) -> None:
        self._finish_modal(context)
