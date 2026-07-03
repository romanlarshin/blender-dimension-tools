"""User interface — panels and lists."""

from __future__ import annotations

import bpy

from ..log import get_logger
from .panel import DIMTOOLS_PT_main

_log = get_logger("ui")

classes = (DIMTOOLS_PT_main,)


def register() -> None:
    """Register UI classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    _log.debug("UI registered")


def unregister() -> None:
    """Unregister UI classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    _log.debug("UI unregistered")
