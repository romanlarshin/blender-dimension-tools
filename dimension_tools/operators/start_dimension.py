"""Start linear dimension operator — modal tool entry point.

Activates a persistent modal session for placing linear dimensions. Stays active
until ESC or right-click. Does not create dimensions or draw GPU overlays yet.
"""

from __future__ import annotations

import bpy

from ..log import get_logger

_log = get_logger("operators.start_dimension")

_STATUS_TEXT = "Linear Dimension Mode (ESC to Exit)"


class DIMTOOLS_OT_start_linear_dimension(bpy.types.Operator):
    """Enter modal linear dimension placement mode."""

    bl_idname = "dimtools.start_linear_dimension"
    bl_label = "Start Linear Dimension"
    bl_description = "Activate linear dimension placement mode until ESC or right-click"
    bl_options = {"REGISTER"}

    @staticmethod
    def _clear_modal_state(context: bpy.types.Context) -> None:
        """Restore cursor and clear workspace status text."""
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ) -> set[str]:
        """Start the modal operator in a 3D Viewport."""
        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Start Linear Dimension requires a 3D Viewport")
            return {"CANCELLED"}

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
            self._clear_modal_state(context)
            _log.debug("Linear dimension modal cancelled")
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            print("Click captured")
            _log.debug("Linear dimension click captured")
            return {"RUNNING_MODAL"}

        if event.type == "MOUSEMOVE":
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context: bpy.types.Context) -> None:
        """Clean up when the modal session is interrupted."""
        self._clear_modal_state(context)
