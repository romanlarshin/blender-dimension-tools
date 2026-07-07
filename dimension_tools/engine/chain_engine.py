"""Chain attachment engine."""

from __future__ import annotations

import bpy
from mathutils import Vector

from ..core import chain as chain_core
from .offset_engine import build_dimension_layout


def compute_chain_uid(
    context: bpy.types.Context,
    point_a: Vector,
    point_b: Vector,
    offset_vector: Vector,
) -> str:
    """Find or create a chain uid for a new dimension layout."""
    layout = build_dimension_layout(point_a, point_b, offset_vector)
    if layout is None:
        return chain_core.find_or_create_chain(context.scene, Vector((0.0, 0.0, 1.0)), 0.0)

    if offset_vector.length_squared < 1e-12:
        return chain_core.find_or_create_chain(context.scene, Vector((0.0, 0.0, 1.0)), 0.0)

    offset_dir = offset_vector.normalized()
    return chain_core.find_or_create_chain(context.scene, offset_dir, offset_vector.length)


def register() -> None:
    """Initialize the chain engine."""


def unregister() -> None:
    """Shut down the chain engine."""
