"""Blender operators for dimension tool interaction."""

from __future__ import annotations

import bpy

from ..log import get_logger
from .start_dimension import DIMTOOLS_OT_start_linear_dimension

_log = get_logger("operators")

classes = (DIMTOOLS_OT_start_linear_dimension,)


def register() -> None:
    """Register dimension tool operators."""
    for cls in classes:
        bpy.utils.register_class(cls)
    _log.debug("Operators registered")


def unregister() -> None:
    """Unregister dimension tool operators."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    _log.debug("Operators unregistered")
