"""Viewport GPU preview — vertex snap cross for POST_VIEW handlers."""

from __future__ import annotations

import gpu

from ..log import get_logger
from . import lines

_log = get_logger("overlay.snap_preview")

SNAP_CROSS_COLOR = (0.2, 1.0, 0.2, 1.0)
FIRST_POINT_CROSS_COLOR = (1.0, 1.0, 0.2, 1.0)
SECOND_POINT_CROSS_COLOR = (1.0, 0.2, 0.2, 1.0)
PREVIEW_LINE_COLOR = (1.0, 1.0, 0.2, 1.0)
SNAP_CROSS_SIZE = 0.25


def draw_vertex_snap() -> None:
    """Draw crosses and a preview line for the first point and current snap."""
    from ..engine import modal_engine

    session = modal_engine.get_session()
    if session is None:
        return

    if (
        session.first_point is None
        and session.snap_result is None
        and session.second_point is None
    ):
        return

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_test_set("NONE")

    if session.first_point is not None and session.snap_result is not None:
        lines.draw_world_lines(
            [session.first_point, session.snap_result.world_co],
            PREVIEW_LINE_COLOR,
        )

    if session.first_point is not None:
        lines.draw_world_cross(session.first_point, SNAP_CROSS_SIZE, FIRST_POINT_CROSS_COLOR)

    if session.second_point is not None:
        lines.draw_world_cross(session.second_point, SNAP_CROSS_SIZE, SECOND_POINT_CROSS_COLOR)

    if session.snap_result is not None:
        lines.draw_world_cross(
            session.snap_result.world_co,
            SNAP_CROSS_SIZE,
            SNAP_CROSS_COLOR,
        )

    gpu.state.depth_test_set("LESS_EQUAL")
    gpu.state.blend_set("NONE")
