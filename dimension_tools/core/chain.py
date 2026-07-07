"""Dimension chain — shared plane, offset, and grouped dimensions.

New dimensions automatically join nearby chains instead of using a separate
keep-same-level flag.
"""

from __future__ import annotations

import uuid

import bpy
from mathutils import Vector

from .dimension import get_scene_state

CHAIN_OFFSET_TOLERANCE = 0.001
CHAIN_NORMAL_TOLERANCE = 0.01


def _generate_chain_uid() -> str:
    return uuid.uuid4().hex


def find_or_create_chain(
    scene: bpy.types.Scene,
    plane_normal: Vector,
    offset: float,
) -> str:
    """Return an existing chain uid or create a new chain for the given plane."""
    state = get_scene_state(scene)
    normal = plane_normal.normalized()

    for chain in state.chains:
        chain_normal = Vector(chain.plane_normal).normalized()
        if chain_normal.dot(normal) >= 1.0 - CHAIN_NORMAL_TOLERANCE:
            if abs(chain.offset - offset) <= CHAIN_OFFSET_TOLERANCE:
                return chain.uid

    chain = state.chains.add()
    chain.uid = _generate_chain_uid()
    chain.plane_normal = normal
    chain.offset = offset
    return chain.uid


def remove_orphan_chains(scene: bpy.types.Scene) -> None:
    """Remove chains that no longer have any dimensions."""
    state = get_scene_state(scene)
    used_uids = {item.chain_uid for item in state.dimensions if item.chain_uid}
    remove_indices = [
        index for index, chain in enumerate(state.chains) if chain.uid not in used_uids
    ]
    for index in reversed(remove_indices):
        state.chains.remove(index)
