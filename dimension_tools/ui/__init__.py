"""User interface — panels and lists."""

from __future__ import annotations

import bpy

from .panel import DIMTOOLS_PT_dimension_list, DIMTOOLS_PT_main

classes = (
    DIMTOOLS_PT_main,
    DIMTOOLS_PT_dimension_list,
)


def register() -> None:
    """Register UI classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister UI classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
