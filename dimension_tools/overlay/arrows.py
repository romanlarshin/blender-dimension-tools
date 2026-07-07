"""GPU drawing for dimension arrowheads."""

from __future__ import annotations

from mathutils import Vector

from ..gpu.batch import TriangleBatch


def _view_axis_z(rv3d) -> Vector:
    """Return the view direction in world space."""
    return (rv3d.view_matrix.inverted().to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()


def collect_arrow_head(
    tip: Vector,
    direction: Vector,
    rv3d,
    size: float,
    batch: TriangleBatch,
) -> None:
    """Add a filled arrowhead triangle to ``batch``."""
    dir_n = direction.normalized()
    if dir_n.length_squared < 1e-12:
        return

    view_z = _view_axis_z(rv3d)
    side = dir_n.cross(view_z)
    if side.length_squared < 1e-12:
        side = dir_n.cross(Vector((0.0, 1.0, 0.0)))
    side.normalize()

    back = tip - dir_n * size
    left = back + side * (size * 0.35)
    right = back - side * (size * 0.35)
    batch.add_triangle(tip, left, right)


def collect_arrow_pair(
    start: Vector,
    end: Vector,
    rv3d,
    size: float,
    batch: TriangleBatch,
) -> None:
    """Add inward-facing arrowheads at both ends of a dimension line."""
    direction = end - start
    if direction.length_squared < 1e-12:
        return
    collect_arrow_head(start, direction, rv3d, size, batch)
    collect_arrow_head(end, -direction, rv3d, size, batch)
