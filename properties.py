"""Scene-attached RNA data for persistent dimensions.

Defines PropertyGroups stored on :class:`bpy.types.Scene`. Only typed RNA
properties belong here — no Python objects, GPU batches, or arbitrary
collections.
"""

from __future__ import annotations

from .log import get_logger

_log = get_logger("properties")


def register() -> None:
    """Register scene property classes.

    Reserved for future dimension PropertyGroups. Intentionally empty during
    bootstrap so the addon loads before the data model is implemented.
    """
    _log.debug("Properties registered (no classes yet)")


def unregister() -> None:
    """Unregister scene property classes and remove Scene pointer properties."""
    _log.debug("Properties unregistered")
