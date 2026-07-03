"""GPU overlay primitives.

Low-level viewport drawing using the ``gpu`` module. Each future submodule
will handle one visual primitive; the draw engine composes them. No Curve
objects and no object-level geometry creation.
"""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("overlay")


def register() -> None:
    """Initialize overlay drawing resources.

    Intentionally empty during bootstrap so the addon loads before GPU
    primitives are implemented.
    """
    _log.debug("Overlay registered")


def unregister() -> None:
    """Release overlay drawing resources."""
    _log.debug("Overlay unregistered")
