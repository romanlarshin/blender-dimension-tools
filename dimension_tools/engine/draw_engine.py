"""Draw engine — viewport overlay orchestration.

Will register the View3D POST_PIXEL draw handler, iterate stored dimensions,
and dispatch GPU drawing calls to the overlay package. GPU drawing only — no
Curve or Mesh objects.
"""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("engine.draw")


def register() -> None:
    """Register the viewport draw handler.

    Intentionally empty during bootstrap so the addon loads before rendering
    is implemented.
    """
    _log.debug("Draw engine registered (no handler yet)")


def unregister() -> None:
    """Remove the viewport draw handler."""
    _log.debug("Draw engine unregistered")
