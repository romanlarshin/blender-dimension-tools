"""Viewport GPU preview — origin cross drawing for POST_VIEW handlers."""

from __future__ import annotations

import gpu
from mathutils import Vector

from ..log import get_logger
from . import lines

_log = get_logger("overlay.snap_preview")

ORIGIN_CROSS_COLOR = (0.2, 1.0, 0.2, 1.0)
ORIGIN_CROSS_SIZE = 1.0


def draw_origin_point() -> None:
    """Draw a large green 3D cross at world origin for POST_VIEW verification."""
    origin = Vector((0.0, 0.0, 0.0))
    _log.debug("draw origin cross at %s", origin)

    gpu.state.blend_set("ALPHA")
    gpu.state.depth_test_set("NONE")
    lines.draw_world_cross(origin, ORIGIN_CROSS_SIZE, ORIGIN_CROSS_COLOR)
    gpu.state.depth_test_set("LESS_EQUAL")
    gpu.state.blend_set("NONE")
