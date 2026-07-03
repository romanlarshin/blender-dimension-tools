"""Snap engine — cursor-to-geometry snapping.

Will find snap targets near the mouse in screen space and return plain data
(world point, target type). Does not modify the Scene.
"""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("engine.snap")


def register() -> None:
    """Initialize the snap engine.

    Intentionally empty during bootstrap so the addon loads before snapping
    is implemented.
    """
    _log.debug("Snap engine registered")


def unregister() -> None:
    """Shut down the snap engine."""
    _log.debug("Snap engine unregistered")
