"""Viewport GPU preview — snap markers and modal overlays."""

from __future__ import annotations

import bpy
import gpu

from ..gpu.batch import LineBatch
from ..utils import viewport as viewport_utils
from . import dimension_preview, lines

SNAP_COLOR = (0.2, 1.0, 0.2, 1.0)
FIRST_POINT_COLOR = (1.0, 1.0, 0.0, 1.0)
SECOND_POINT_COLOR = (1.0, 0.2, 0.2, 1.0)
PREVIEW_LINE_COLOR = (1.0, 1.0, 0.0, 0.9)
MARKER_PIXEL_SIZE = 22.0
MARKER_LINE_WIDTH = 3.5
MARKER_POINT_SIZE = 10.0


def _marker_world_size(context, world_co) -> float:
    return viewport_utils.pixel_size_to_world(context, world_co, MARKER_PIXEL_SIZE)


def _draw_marker(context, world_co, color: tuple[float, float, float, float]) -> None:
    """Draw a clearly visible cross and point at a world position."""
    size = _marker_world_size(context, world_co)
    lines.draw_world_cross(world_co, size, color, line_width=MARKER_LINE_WIDTH)
    lines.draw_world_point(world_co, color, size=MARKER_POINT_SIZE)


def draw_modal_preview() -> None:
    """Draw snap markers and modal placement geometry (POST_VIEW)."""
    from ..engine import modal_engine

    context = bpy.context
    session = modal_engine.get_session()
    if session is None:
        return

    show_offset = (
        session.first_snap is not None
        and session.second_snap is not None
        and session.offset_mode
    )

    if (
        not show_offset
        and session.first_point is None
        and session.snap_result is None
    ):
        return

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_test_set("NONE")

    if show_offset:
        dimension_preview.draw_offset_preview(
            context,
            session.first_snap.world_co,
            session.second_snap.world_co,
            session.offset_vector,
        )
        _draw_marker(context, session.first_snap.world_co, FIRST_POINT_COLOR)
        _draw_marker(context, session.second_snap.world_co, SECOND_POINT_COLOR)
    else:
        if session.first_point is not None and session.snap_result is not None:
            batch = LineBatch()
            batch.add_segment(session.first_point, session.snap_result.world_co)
            batch.draw(PREVIEW_LINE_COLOR, line_width=2.5)

        if session.first_point is not None:
            _draw_marker(context, session.first_point, FIRST_POINT_COLOR)

        if session.snap_result is not None:
            _draw_marker(context, session.snap_result.world_co, SNAP_COLOR)

    gpu.state.depth_test_set("LESS_EQUAL")
    gpu.state.blend_set("NONE")


def draw_modal_pixel() -> None:
    """Draw preview measurement labels during offset placement (POST_PIXEL)."""
    from ..engine import modal_engine

    context = bpy.context
    session = modal_engine.get_session()
    if session is None:
        return

    show_offset = (
        session.first_snap is not None
        and session.second_snap is not None
        and session.offset_mode
    )
    if not show_offset:
        return

    gpu.state.blend_set("ALPHA")
    dimension_preview.draw_offset_preview_label(
        context,
        session.first_snap.world_co,
        session.second_snap.world_co,
        session.offset_vector,
    )
    gpu.state.blend_set("NONE")
