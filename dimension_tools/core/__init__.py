"""Core domain layer — dimension data model and scene storage logic.

Business rules that are independent of operators, GPU drawing, and Blender UI.
Reads and writes only through RNA PropertyGroups defined in ``properties``;
never attaches arbitrary Python state to the Scene.
"""

from __future__ import annotations

from ..log import get_logger
from . import chain, dimension, selection, store

_log = get_logger("core")

__all__ = (
    "chain",
    "dimension",
    "selection",
    "store",
)


def register() -> None:
    """Initialize the core domain layer.

    Reserved for future runtime managers. Intentionally empty during bootstrap.
    """
    _log.debug("Core registered")


def unregister() -> None:
    """Shut down the core domain layer."""
    _log.debug("Core unregistered")
