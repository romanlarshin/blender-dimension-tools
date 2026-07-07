"""Start linear dimension operator — modal tool entry point.

Activates a persistent modal session for placing linear dimensions. Stays active
until ESC or right-click. GPU preview draws crosses for snap and the first picked point.
"""

from __future__ import annotations

import bpy

from ..engine import modal_engine, snap_engine
from ..log import get_logger
from ..overlay import snap_preview
from ..preferences import DIMTOOLS_AddonPreferences

_log = get_logger("operators.start_dimension")

_STATUS_TEXT = "Linear Dimension Mode (ESC to Exit)"


def _get_snap_radius(context: bpy.types.Context) -> float:
    """Read the snap radius from addon preferences."""
    prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
    return float(prefs.snap_radius)


def _redraw_all_view3d_areas(context: bpy.types.Context) -> None:
    """Force redraw on every 3D Viewport area in the current window."""
    window = context.window
    if window is None or window.screen is None:
        return

    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            area.tag_redraw()


def _update_vertex_snap(context: bpy.types.Context, event: bpy.types.Event) -> None:
    """Find the nearest mesh vertex and store it in the active modal session."""
    session = modal_engine.get_session()
    if session is None:
        return

    with snap_engine.view3d_snap_context(context) as snap_context:
        session.snap_result = snap_engine.find_nearest_vertex(
            snap_context,
            event,
            _get_snap_radius(context),
        )

    _redraw_all_view3d_areas(context)


class DIMTOOLS_OT_start_linear_dimension(bpy.types.Operator):
    """Enter modal linear dimension placement mode."""

    bl_idname = "dimtools.start_linear_dimension"
    bl_label = "Start Linear Dimension"
    bl_description = "Activate linear dimension placement mode until ESC or right-click"
    bl_options = {"REGISTER"}

    _draw_handle = None

    def _add_draw_handler(self) -> None:
        """Register the POST_VIEW draw handler on this operator instance."""
        if self._draw_handle is not None:
            return

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            snap_preview.draw_vertex_snap,
            (),
            "WINDOW",
            "POST_VIEW",
        )
        print("[dimtools] draw handler added")
        _log.info("draw handler added")

    def _remove_draw_handler(self, context: bpy.types.Context) -> None:
        """Remove the POST_VIEW draw handler from this operator instance."""
        if self._draw_handle is None:
            return

        bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, "WINDOW")
        self._draw_handle = None
        print("[dimtools] draw handler removed")
        _log.info("draw handler removed")
        _redraw_all_view3d_areas(context)

    def _finish_modal(self, context: bpy.types.Context) -> None:
        """Restore UI state and tear down the modal session."""
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        self._remove_draw_handler(context)
        modal_engine.end_session()

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ) -> set[str]:
        """Start the modal operator in a 3D Viewport."""
        print("[dimtools] invoke starts")
        _log.info("invoke starts")

        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Start Linear Dimension requires a 3D Viewport")
            return {"CANCELLED"}

        modal_engine.start_session()
        self._draw_handle = None
        self._add_draw_handler()
        _update_vertex_snap(context, event)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("CROSSHAIR")
        context.workspace.status_text_set(_STATUS_TEXT)
        _log.debug("Linear dimension modal started")
        return {"RUNNING_MODAL"}

    def modal(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ) -> set[str]:
        """Handle input while linear dimension mode is active."""
        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            self._finish_modal(context)
            _log.debug("Linear dimension modal cancelled")
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            session = modal_engine.get_session()
            if (
                session is not None
                and session.first_point is None
                and session.snap_result is not None
            ):
                session.first_point = session.snap_result.world_co.copy()
                self.report({"INFO"}, "First point captured")
                _log.debug("First point captured at %s", session.first_point)
                _redraw_all_view3d_areas(context)
            return {"RUNNING_MODAL"}

        if event.type == "MOUSEMOVE":
            _update_vertex_snap(context, event)
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context: bpy.types.Context) -> None:
        """Clean up when the modal session is interrupted."""
        self._finish_modal(context)
