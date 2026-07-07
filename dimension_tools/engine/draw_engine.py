"""Draw engine — viewport overlay orchestration."""

from __future__ import annotations

import bpy
import gpu
from bpy.app.handlers import persistent

from ..log import get_logger
from ..overlay import dimension_preview

_log = get_logger("engine.draw")

_draw_handle_view = None
_draw_handle_pixel = None
_hover_uid: str | None = None


@persistent
def _load_post_handler(_dummy) -> None:
    """Redraw viewports after loading a file so dimensions appear immediately."""
    window_manager = bpy.context.window_manager
    if window_manager is None:
        return
    for window in window_manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def get_hover_uid() -> str | None:
    """Return the dimension uid currently hovered in selection mode."""
    return _hover_uid


def set_hover_uid(uid: str | None) -> None:
    """Set the hovered dimension uid for highlight drawing."""
    global _hover_uid
    _hover_uid = uid


def _draw_stored_dimensions_view() -> None:
    """POST_VIEW callback for dimension lines and arrows."""
    context = bpy.context
    if context is None or context.region is None:
        return

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_test_set("NONE")
    dimension_preview.draw_scene_dimensions(context, hover_uid=_hover_uid)
    gpu.state.depth_test_set("LESS_EQUAL")
    gpu.state.blend_set("NONE")


def _draw_stored_dimensions_pixel() -> None:
    """POST_PIXEL callback for dimension measurement text."""
    context = bpy.context
    if context is None or context.region is None:
        return

    gpu.state.blend_set("ALPHA")
    dimension_preview.draw_scene_labels(context, hover_uid=_hover_uid)
    gpu.state.blend_set("NONE")


def register() -> None:
    """Register the persistent draw handlers."""
    global _draw_handle_view, _draw_handle_pixel
    if _draw_handle_view is not None:
        return

    _draw_handle_view = bpy.types.SpaceView3D.draw_handler_add(
        _draw_stored_dimensions_view,
        (),
        "WINDOW",
        "POST_VIEW",
    )
    _draw_handle_pixel = bpy.types.SpaceView3D.draw_handler_add(
        _draw_stored_dimensions_pixel,
        (),
        "WINDOW",
        "POST_PIXEL",
    )
    if _load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post_handler)
    _log.debug("Draw engine registered")


def unregister() -> None:
    """Unregister the persistent draw handlers."""
    global _draw_handle_view, _draw_handle_pixel, _hover_uid
    if _draw_handle_view is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle_view, "WINDOW")
        _draw_handle_view = None
    if _draw_handle_pixel is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle_pixel, "WINDOW")
        _draw_handle_pixel = None
    if _load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post_handler)
    _hover_uid = None
    _log.debug("Draw engine unregistered")
